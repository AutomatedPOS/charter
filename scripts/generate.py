"""Build one arc42 package per profile into build/.

Each package holds START-HERE.md, the twelve arc42 chapter files with control
blocks, README.md and AGENTS.md, and is zipped as build/<package>.zip.
START-HERE.md is also written to the repo root.

Base baseline and overlay are resolved separately with trestle and merged here:
the overlay profile gives the control selection and its guidance notes, the
NIST baselines give the [L M H] tags.

Run from anywhere: python scripts/generate.py
Needs: compliance-trestle (build time only).
"""
import csv
import json
import os
import pathlib
import re
import shutil
import tempfile
import zipfile

from trestle.core.profile_resolver import ProfileResolver

ROOT = pathlib.Path(__file__).resolve().parent.parent
NIST = ROOT / 'oscal/nist.gov/SP800-53/rev5/json'
PROFILES = ROOT / 'oscal/profiles'
DATA = ROOT / 'data'
BUILD = ROOT / 'build'
CATALOG_VERSION = '5.2.0'
CONTENT_RELEASE = 'usnistgov/oscal-content v1.6.0'
LEVELS = ['low', 'moderate', 'high']

OVERLAYS = {
    None: None,
    'ot': {'tag': 'OT', 'source': 'sp800-82r3-ot', 'draft': False,
           'files': {'low': 'profile-ot-low.json', 'moderate': 'profile-ot.json', 'high': 'profile-ot-high.json'}},
    'ai-safe-ai-draft': {'tag': 'SAFE-AI', 'source': 'safe-ai', 'draft': True,
                         'files': {lv: f'profile-ai-safe-ai-{lv}.json' for lv in LEVELS}},
    'ai-cosais-predictive-draft': {'tag': 'COSAiS', 'source': 'nist-cosais-predictive-draft', 'draft': True,
                                   'files': {lv: f'profile-ai-nist-cosais-predictive-draft-{lv}.json' for lv in LEVELS}},
}

CHAPTERS = [
    ('01_introduction_and_goals', 'Introduction and Goals'),
    ('02_architecture_constraints', 'Architecture Constraints'),
    ('03_context_and_scope', 'Context and Scope'),
    ('04_solution_strategy', 'Solution Strategy'),
    ('05_building_block_view', 'Building Block View'),
    ('06_runtime_view', 'Runtime View'),
    ('07_deployment_view', 'Deployment View'),
    ('08_concepts', 'Cross-cutting Concepts'),
    ('09_architecture_decisions', 'Architecture Decisions'),
    ('10_quality_requirements', 'Quality Requirements'),
    ('11_technical_risks', 'Risks and Technical Debts'),
    ('12_glossary', 'Glossary'),
]

STATUS_VALUES = ['implemented', 'partial', 'planned', 'alternative', 'not-applicable']
ORIGINATION_VALUES = ['organization', 'system-specific', 'customer-configured', 'customer-provided', 'inherited']
SEE_ALSO_MAX = 5
FIXED_ZIP_TIME = (2026, 1, 1, 0, 0, 0)


# ---------- inputs ----------

def walk(controls):
    for c in controls:
        yield c
        yield from walk(c.get('controls', []))


def load_catalog():
    cat = json.loads((NIST / 'NIST_SP-800-53_rev5_catalog.json').read_text(encoding='utf-8'))['catalog']
    controls, order, families = {}, {}, {}
    for g in cat['groups']:
        families[g['id']] = g['title']
        for c in walk(g.get('controls', [])):
            if any(p['name'] == 'status' and p['value'] == 'withdrawn' for p in c.get('props', [])):
                continue
            label = next(p['value'] for p in c['props'] if p['name'] == 'label' and 'class' not in p)
            related = [l['href'][1:] for l in c.get('links', []) if l.get('rel') == 'related']
            controls[c['id']] = {'id': c['id'], 'title': c['title'], 'label': label,
                                 'family': g['id'], 'related': related}
            order[c['id']] = len(order)
    return controls, order, families


def read_csv(path):
    with path.open(newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))


def load_questions():
    questions = {}
    for path in sorted((DATA / 'questions').glob('*.csv')):
        for r in read_csv(path):
            questions.setdefault(r['control_id'], []).append(r['question'])
    return questions


def resolved_catalog(trestle_root, profile):
    """Resolve one profile with trestle. NIST's relative hrefs assume NIST as the working folder."""
    cwd = os.getcwd()
    os.chdir(NIST)
    try:
        cat = ProfileResolver.get_resolved_profile_catalog(trestle_root, str(profile))
    finally:
        os.chdir(cwd)
    return json.loads(cat.oscal_serialize_json())['catalog']


def control_parts(catalog):
    return {c['id']: c.get('parts', []) for g in catalog.get('groups', []) for c in walk(g.get('controls', []))}


def overlay_notes(parts_by_id, source):
    """Guidance parts the overlay added, found by their overlay-source prop."""
    notes = {}
    for cid, parts in parts_by_id.items():
        for p in parts:
            if p['name'] == 'guidance' and any(pr['name'] == 'overlay-source' and pr['value'] == source
                                               for pr in p.get('props', [])):
                notes.setdefault(cid, []).append(p['prose'].strip())
    return notes


# ---------- placement ----------

class Placement:
    def __init__(self):
        self.family = {r['family']: r for r in read_csv(DATA / 'placement-families.csv')}
        self.exceptions = {r['control_id']: int(r['chapter']) for r in read_csv(DATA / 'placement-exceptions.csv')}

    def __call__(self, control):
        """(chapter, mode, gate) for a control. Enhancements are placed by parent id."""
        row = self.family.get(control['family'])
        if row is None:
            raise SystemExit(f'no placement for {control["id"]}: family {control["family"]} has no row')
        if row['mode'] == 'skip':
            return None, 'skip', ''
        parent = control['id'].split('.')[0]
        chapter = self.exceptions.get(control['id'], self.exceptions.get(parent))
        if chapter is None:
            if not row['chapter']:
                raise SystemExit(f'no placement for {control["id"]}: family {control["family"]} has no chapter')
            chapter = int(row['chapter'])
        return chapter, row['mode'], row['gate']


# ---------- START-HERE ----------

PREFILL = re.compile(r'([a-z]{2}-\d+(?:\.\d+)?)(?:\s+q(\d+))?')


def load_start_here(controls, place):
    items = []
    for r in read_csv(DATA / 'start-here.csv'):
        prefills = [(cid, int(q) if q else None) for cid, q in PREFILL.findall(r['prefills'])]
        chapters = []
        for part in r['arc42_chapter'].split(','):
            part = part.strip()
            m = re.fullmatch(r'follows ([a-z]{2}-\d+(?:\.\d+)?) placement', part)
            chapters.append(place(controls[m.group(1)])[0] if m else int(part))
        items.append({**r, 'prefill_ids': prefills, 'chapters': chapters})
    return items


def prefill_text(cid, q, controls):
    label = controls[cid]['label']
    text = f'{label} question {q}' if q else label
    if controls[cid]['family'] == 'pm':
        text += ' (organization-level, kept for the SSP export)'
    return text


def render_start_here(items, controls):
    out = ['# START HERE', '',
           'Answer these questions before you work the arc42 chapters. They are the same for every system.',
           '',
           'Anyone can answer any of them: the business owner, the security contact, or the architect. '
           'The answers are a first draft. They pre-fill the arc42 chapters and the control questions '
           'listed under each one, and get sharpened there.',
           '',
           'The last question picks the overlay. Together with the impact level from the rating question, '
           'it tells you which package to use.', '']
    for it in items:
        chapters = ', '.join(str(c) for c in it['chapters'])
        out += [f'<!-- charter:start-here id="{it["id"]}" -->',
                f'## {it["id"]}  ({it["task"]})', '',
                it['question'], '']
        if it['id'] == 'sh-12':
            out += ['State low, moderate, or high for each of confidentiality, integrity, and availability, '
                    'with a reason for each.', '']
        if it['prefill_ids']:
            out.append('**Pre-fills:** ' + ', '.join(prefill_text(c, q, controls) for c, q in it['prefill_ids']))
        else:
            out.append(f'**Pre-fills:** {it["prefills"]}')
        out += ['', f'**arc42 chapter:** {chapters}', '', '**Answer:**', '', '',
                '<!-- /charter:start-here -->', '']
    return '\n'.join(out)


# ---------- control blocks ----------

def tags(cid, members, overlay, notes, base_ids):
    letters = ' '.join(l for l, lv in zip('LMH', LEVELS) if cid in members[lv])
    out = []
    if letters:
        out.append(f'[{letters}]')
    if overlay and (cid in notes or cid not in base_ids):
        out.append(f'[{overlay["tag"]}]')
    return ' '.join(f'`{t}`' for t in out)


def see_also(control, selected, controls, place):
    picks = []
    for rid in control['related']:
        if rid in selected and rid != control['id'] and rid not in [p[0] for p in picks]:
            chapter = place(controls[rid])[0]
            if chapter is not None:
                picks.append((rid, chapter))
        if len(picks) == SEE_ALSO_MAX:
            break
    if not picks:
        return ''
    groups = []
    for rid, chapter in picks:
        if groups and groups[-1][1] == chapter:
            groups[-1][0].append(controls[rid]['label'])
        else:
            groups.append(([controls[rid]['label']], chapter))
    return ', '.join(f'{", ".join(labels)} (chapter {ch})' for labels, ch in groups)


def ask_lines(questions):
    if len(questions) == 1:
        return [f'**Ask:** {questions[0]}']
    return ['**Ask:**', ''] + [f'{i}. {q}' for i, q in enumerate(questions, 1)]


def answer_fields():
    return ['**Status:**', '', '**Origination:**', '', '**Answer state:**', '', '**Answer:**', '', '']


def control_block(c, ctx, level):
    cid = c['id']
    lines = [f'<!-- charter:control id="{cid}" profile="{ctx["name"]}" -->',
             f'{"#" * level} {c["title"]}  `{c["label"]}`  {ctx["tags"](cid)}'.rstrip(), '']
    lines += ask_lines(ctx['questions'][cid]) + ['']
    for note in ctx['notes'].get(cid, []):
        lines += [f'**Consider ({ctx["overlay"]["tag"]}):** {note}', '']
    if cid in ctx['from_start']:
        lines += [f'**From START-HERE:** {", ".join(ctx["from_start"][cid])}', '']
    lines += answer_fields()
    also = ctx['see_also'](c)
    if also:
        lines += [f'**See also:** {also}', '']
    lines += ['<!-- /charter:control -->', '']
    return lines


def family_block(family, members_list, ctx):
    ids = ' '.join(c['id'] for c in members_list)
    lines = [f'<!-- charter:family id="{family}" profile="{ctx["name"]}" controls="{ids}" -->',
             f'#### {ctx["families"][family]}  `{family.upper()}`', '',
             'These controls are usually provided by the organization or the facility, not built into the system. '
             'Answer once for the family. Name any control this system handles differently in the answer.', '']
    for c in members_list:
        cid = c['id']
        qs = ctx['questions'][cid]
        lines.append(f'- `{c["label"]}` {c["title"]} {ctx["tags"](cid)}: {qs[0]}'.replace('  ', ' '))
        lines += [f'  {q}' for q in qs[1:]]
        for note in ctx['notes'].get(cid, []):
            lines.append(f'  - Consider ({ctx["overlay"]["tag"]}): {note}')
        if cid in ctx['from_start']:
            lines.append(f'  - From START-HERE: {", ".join(ctx["from_start"][cid])}')
    lines += [''] + answer_fields() + ['<!-- /charter:family -->', '']
    return lines


def render_chapter(number, title, placed, ctx):
    name = ctx['name']
    lines = []
    if number == 1:
        lines += ['---', f'charter-profile: {name}', f'catalog: NIST SP 800-53 Rev {CATALOG_VERSION}', '---', '']
    lines += [f'# {number}. {title}', '', 'Write this chapter\'s architecture content here.', '']

    starts = [it for it in ctx['start_here'] if number in it['chapters']]
    if starts:
        lines += ['## From START-HERE', '']
        for it in starts:
            lines += [f'<!-- charter:start-here id="{it["id"]}" -->', f'**{it["id"]}:** {it["question"]}', '',
                      '**Answer:**', '', '', '<!-- /charter:start-here -->', '']

    if number == 1:
        pm = [ctx['controls'][cid]['label'] for cid in ctx['pm']]
        line = 'Organization-level controls (the PM family) are answered outside this system document.'
        if pm:
            line += f' This profile includes {len(pm)}: {", ".join(pm)}.'
        lines += [line, '']
    if number == 9:
        lines += ['Record tailoring decisions here as architecture decision records.', '']
    if number == 10:
        lines += [f'Required control baseline: {ctx["baseline_text"]}.', '']
    if number == 11:
        lines += ['## Parked items', '', 'List every control or START-HERE answer marked parked, with who it is waiting on.',
                  '', '<!-- charter:parked -->', '', '<!-- /charter:parked -->', '']

    if placed:
        lines += ['## Security controls', '']
        by_family = {}
        for c, mode, gate in placed:
            by_family.setdefault(c['family'], []).append((c, mode, gate))
        for family in sorted(by_family, key=lambda f: list(ctx['families']).index(f)):
            rows = by_family[family]
            lines += [f'### {ctx["families"][family]}', '']
            if rows[0][2] == 'pii':
                lines += ['Answer this family only if this system handles personal data (START-HERE sh-05). '
                          'If it does not, mark each control not-applicable.', '']
            if rows[0][1] == 'inherited':
                lines += family_block(family, [c for c, _, _ in rows], ctx)
                continue
            for c, _, _ in rows:
                lines += control_block(c, ctx, 5 if '.' in c['id'] else 4)
    return '\n'.join(lines).rstrip() + '\n'


# ---------- package text ----------

ARC42_CREDIT = ('The chapter structure and headings come from the arc42 template by Gernot Starke and Peter Hruschka '
                '(https://arc42.org), licensed under CC BY-SA 4.0 (https://creativecommons.org/licenses/by-sa/4.0/). '
                'Changed: arc42\'s explanatory text is left out, and Charter adds START-HERE slots and security '
                'control questions to the chapters. Under CC BY-SA, adaptations of the arc42 structure that you share '
                'outside your organization carry the same license. Your own answers stay yours.')


def render_readme(ctx):
    o = ctx['overlay']
    lines = [f'# {ctx["name"]}', '']
    if o and o['draft']:
        lines += ['> **DRAFT.** This package is built from a draft AI overlay. It will be replaced when NIST '
                  'publishes final AI overlays. Do not treat its control selection as settled.', '']
    lines += ['An arc42 architecture package with NIST SP 800-53 Rev 5 security controls placed in the chapters '
              'where they belong. Each control appears as a design question to answer in place.', '',
              '## Profile', '',
              f'- Package: `{ctx["name"]}`',
              f'- Baseline: {ctx["baseline_text"]}',
              f'- Profile file in the Charter repo: `{ctx["profile_file"]}`',
              f'- Catalog: NIST SP 800-53 Rev {CATALOG_VERSION}, from {CONTENT_RELEASE}',
              f'- Controls: {ctx["count"]} in the profile, {ctx["count"] - len(ctx["pm"])} in the chapters, '
              f'{len(ctx["pm"])} organization-level (PM) answered outside this document']
    if o:
        lines.append(f'- Overlay source: {ctx["source_publication"]}')
    if ctx['removed']:
        lines.append('- Removed by the overlay, relative to the NIST baseline: '
                     + ', '.join(ctx['controls'][c]['label'] for c in ctx['removed']))
    lines.append('')
    if o and o['tag'] == 'SAFE-AI':
        lines += ['SAFE-AI is ©2025 The MITRE Corporation, all rights reserved; approved for public release, '
                  'distribution unlimited, case 25-1028. Only its control ids are used. Its guidance text is not '
                  'reproduced.', '']
    if o and o['tag'] == 'COSAiS':
        lines += ['The COSAiS source is an annotated outline. NIST states its control list is not complete.', '']
    lines += ['## Files', '',
              '- `START-HERE.md`: answer first.',
              '- `01_` to `12_`: the twelve arc42 chapters, with control blocks.',
              '- `AGENTS.md`: instructions for an AI assistant working this package.', '',
              '## arc42', '', ARC42_CREDIT, '']
    return '\n'.join(lines)


def render_agents(ctx):
    return '\n'.join([
        '# Working this package', '',
        f'This is the `{ctx["name"]}` arc42 package. Follow these steps in order.', '',
        '1. Answer START-HERE.md first.',
        '2. Write each START-HERE answer into its arc42 chapter (the "From START-HERE" slot) and into the control '
        'questions it pre-fills (blocks marked "From START-HERE").',
        '3. Then work the chapters, one control block at a time.',
        '4. Put anything not answered as parked in chapter 11, under "Parked items", with who it is waiting on.', '',
        '## Rules', '',
        '- Change only Status, Origination, Answer state, and Answer. Never edit headings, Ask lines, or the '
        '`charter:` comment markers.',
        f'- Status is one of: {", ".join(STATUS_VALUES)}.',
        f'- Origination is one of: {", ".join(ORIGINATION_VALUES)}.',
        '- Answer state is `answered`, or `parked: <who it is waiting on>`.',
        '- Every block needs an answer or a parked note.',
        '- Organization-level (PM) controls are answered outside this document.', ''])


# ---------- build ----------

def write_zip(folder, target):
    with zipfile.ZipFile(target, 'w', zipfile.ZIP_DEFLATED) as z:
        for path in sorted(folder.rglob('*')):
            if path.is_file():
                info = zipfile.ZipInfo(f'{folder.name}/{path.relative_to(folder).as_posix()}', FIXED_ZIP_TIME)
                info.compress_type = zipfile.ZIP_DEFLATED
                z.writestr(info, path.read_bytes())


def main():
    controls, order, families = load_catalog()
    questions = load_questions()
    place = Placement()
    start_here = load_start_here(controls, place)

    from_start = {}
    for it in start_here:
        for cid, q in it['prefill_ids']:
            from_start.setdefault(cid, []).append(f'{it["id"]} (question {q})' if q else it['id'])

    (ROOT / 'START-HERE.md').write_text(render_start_here(start_here, controls), encoding='utf-8')
    BUILD.mkdir(exist_ok=True)

    with tempfile.TemporaryDirectory() as tmp:
        trestle_root = pathlib.Path(tmp)
        (trestle_root / '.trestle/cache').mkdir(parents=True)
        members = {lv: set(control_parts(resolved_catalog(
            trestle_root, f'NIST_SP-800-53_rev5_{lv.upper()}-baseline_profile.json'))) for lv in LEVELS}

        for key, overlay in OVERLAYS.items():
            for level in LEVELS:
                name = f'nist-800-53r5.2-{key}-{level}' if key else f'nist-800-53r5.2-{level}'
                if overlay:
                    profile = PROFILES / overlay['files'][level]
                    parts = control_parts(resolved_catalog(trestle_root, profile))
                    notes = overlay_notes(parts, overlay['source'])
                    meta = json.loads(profile.read_text(encoding='utf-8'))['profile']['metadata']
                    props = {p['name']: p['value'] for p in meta.get('props', [])}
                    source_publication = props.get('source-publication', '')
                    profile_file = profile.relative_to(ROOT).as_posix()
                    baseline_text = f'NIST SP 800-53B {level} with the {overlay["tag"]} overlay'
                else:
                    parts, notes, source_publication = {}, {}, ''
                    profile_file = (NIST / f'NIST_SP-800-53_rev5_{level.upper()}-baseline_profile.json').relative_to(ROOT).as_posix()
                    baseline_text = f'NIST SP 800-53B {level}'
                base_ids = members[level]
                selected = set(parts) if overlay else base_ids
                missing = sorted(set(selected) - set(controls), key=str)
                if missing:
                    raise SystemExit(f'{name}: not active controls in the catalog: {missing}')
                no_q = sorted(c for c in selected if c not in questions)
                if no_q:
                    raise SystemExit(f'{name}: controls with no questions: {no_q}')

                ctx = {'name': name, 'overlay': overlay, 'notes': notes, 'questions': questions,
                       'controls': controls, 'families': families, 'start_here': start_here,
                       'from_start': {k: v for k, v in from_start.items() if k in selected},
                       'baseline_text': baseline_text, 'profile_file': profile_file,
                       'source_publication': source_publication, 'count': len(selected),
                       'removed': sorted(base_ids - selected, key=order.__getitem__)}
                ctx['tags'] = lambda cid, ctx=ctx: tags(cid, members, overlay, notes, base_ids)
                ctx['see_also'] = lambda c, selected=selected: see_also(c, selected, controls, place)

                chapters = {n: [] for n in range(1, 13)}
                ctx['pm'] = []
                for cid in sorted(selected, key=order.__getitem__):
                    chapter, mode, gate = place(controls[cid])
                    if mode == 'skip':
                        ctx['pm'].append(cid)
                    else:
                        chapters[chapter].append((controls[cid], mode, gate))
                placed = sum(len(v) for v in chapters.values())
                if placed + len(ctx['pm']) != len(selected):
                    raise SystemExit(f'{name}: {placed} placed + {len(ctx["pm"])} skipped != {len(selected)}')

                folder = BUILD / name
                if folder.exists():
                    shutil.rmtree(folder)
                folder.mkdir()
                (folder / 'START-HERE.md').write_text(render_start_here(start_here, controls), encoding='utf-8')
                for n, (stem, title) in enumerate(CHAPTERS, 1):
                    (folder / f'{stem}.md').write_text(render_chapter(n, title, chapters[n], ctx), encoding='utf-8')
                (folder / 'README.md').write_text(render_readme(ctx), encoding='utf-8')
                (folder / 'AGENTS.md').write_text(render_agents(ctx), encoding='utf-8')
                target = BUILD / f'{name}.zip'
                write_zip(folder, target)
                print(f'{name}: {len(selected)} controls, {placed} in chapters, {len(ctx["pm"])} PM, '
                      f'{len(notes)} with overlay notes, {target.stat().st_size} bytes')


if __name__ == '__main__':
    main()
