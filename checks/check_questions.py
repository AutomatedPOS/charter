"""Check one family's Ask questions in data/questions/<family>.csv against the pinned catalog.

1. The file parses, has exactly the five columns, and every field is quoted.
2. Every active control and enhancement in the family has rows; no withdrawn or foreign ids.
3. Every covers id is an assessment objective of that control, and a control's rows
   cover all of its leaf objectives (covering a parent objective covers its children).
4. Question wording: no forbidden first word, no NIST vocabulary, no control ids, 35 words max.
5. q runs 1..n per control, rows are in catalog order, status is reviewed or drafted.

Run from the repo root: python checks/check_questions.py ac
Exits 1 if any check fails.
"""
import csv
import io
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
CATALOG = ROOT / 'oscal/nist.gov/SP800-53/rev5/json/NIST_SP-800-53_rev5_catalog.json'
QUESTIONS = ROOT / 'data/questions'
COLUMNS = ['control_id', 'q', 'question', 'covers', 'status']
STATUSES = {'reviewed', 'drafted'}
FORBIDDEN_START = {'do', 'does', 'is', 'are', 'has', 'have', 'can', 'will'}
FORBIDDEN_TEXT = ['organization-defined', '[', 'odp', 'information system']
HARD_LIMIT = 35
SOFT_LIMIT = 25


def walk(controls):
    for control in controls:
        yield control
        yield from walk(control.get('controls', []))


def withdrawn(control):
    return any(p['name'] == 'status' and p['value'] == 'withdrawn' for p in control.get('props', []))


def objectives(control):
    """Map each assessment-objective id to the set of leaf ids under it (itself if a leaf)."""
    found = {}

    def visit(part):
        if part['name'] != 'assessment-objective':
            return set()
        children = set()
        for child in part.get('parts', []):
            children |= visit(child)
        leaves = children or {part['id']}
        found[part['id']] = leaves
        return leaves

    for part in control.get('parts', []):
        visit(part)
    return found


def family_controls(family):
    catalog = json.loads(CATALOG.read_text(encoding='utf-8'))['catalog']
    group = next(g for g in catalog['groups'] if g['id'] == family)
    return [c for c in walk(group['controls']) if not withdrawn(c)]


def main():
    if len(sys.argv) != 2:
        sys.exit('usage: python checks/check_questions.py <family>')
    family = sys.argv[1].lower()
    path = QUESTIONS / f'{family}.csv'
    text = path.read_text(encoding='utf-8')
    problems = []

    rows = list(csv.reader(io.StringIO(text)))
    if rows[0] != COLUMNS:
        problems.append(f'header is {rows[0]}, expected {COLUMNS}')
    rows = rows[1:]
    for n, row in enumerate(rows, 2):
        if len(row) != len(COLUMNS):
            problems.append(f'line {n}: {len(row)} columns')
    rows = [dict(zip(COLUMNS, r)) for r in rows if len(r) == len(COLUMNS)]

    quoted = io.StringIO()
    writer = csv.writer(quoted, quoting=csv.QUOTE_ALL, lineterminator='\n')
    writer.writerow(COLUMNS)
    writer.writerows([r[c] for c in COLUMNS] for r in rows)
    if quoted.getvalue() != text.replace('\r\n', '\n'):
        problems.append('file is not in canonical form (every field quoted, one row per line)')

    controls = family_controls(family)
    order = {c['id']: i for i, c in enumerate(controls)}
    by_control = {}
    for r in rows:
        by_control.setdefault(r['control_id'], []).append(r)

    for cid in by_control:
        if cid not in order:
            problems.append(f'{cid}: not an active control in family {family}')
    keys = [(order.get(r['control_id'], -1), int(r['q']) if r['q'].isdigit() else -1) for r in rows]
    if keys != sorted(keys):
        problems.append('rows are not in catalog order, then q order')

    id_pattern = re.compile(r'\b(ac|at|au|ca|cm|cp|ia|ir|ma|mp|pe|pl|pm|ps|pt|ra|sa|sc|si|sr)-\d', re.I)
    long_count = 0
    multi = 0
    for control in controls:
        cid = control['id']
        mine = by_control.get(cid, [])
        if not mine:
            problems.append(f'{cid}: no questions')
            continue
        if len(mine) > 1:
            multi += 1
        if [r['q'] for r in mine] != [str(i) for i in range(1, len(mine) + 1)]:
            problems.append(f'{cid}: q numbers are {[r["q"] for r in mine]}')
        objs = objectives(control)
        leaves = set().union(*objs.values()) if objs else set()
        covered = set()
        for r in mine:
            tag = f'{cid} q{r["q"]}'
            ids = r['covers'].split()
            if not ids:
                problems.append(f'{tag}: covers is empty')
            for oid in ids:
                if oid in objs:
                    covered |= objs[oid]
                else:
                    problems.append(f'{tag}: covers id {oid} is not an objective of {cid}')
            q = r['question']
            words = q.split()
            if not words:
                problems.append(f'{tag}: empty question')
                continue
            if words[0].lower().strip(',:') in FORBIDDEN_START:
                problems.append(f'{tag}: starts with {words[0]!r}')
            for bad in FORBIDDEN_TEXT:
                if bad in q.lower():
                    problems.append(f'{tag}: contains {bad!r}')
            if id_pattern.search(q):
                problems.append(f'{tag}: contains a control id')
            if len(words) > HARD_LIMIT:
                problems.append(f'{tag}: {len(words)} words')
            elif len(words) > SOFT_LIMIT:
                long_count += 1
            if r['status'] not in STATUSES:
                problems.append(f'{tag}: status {r["status"]!r}')
        missing = leaves - covered
        if missing:
            problems.append(f'{cid}: leaf objectives not covered: {" ".join(sorted(missing))}')

    base = sum('.' not in c['id'] for c in controls)
    status = {s: sum(r['status'] == s for r in rows) for s in sorted(STATUSES)}
    print(f'{family}: {base} controls, {len(controls) - base} enhancements, {len(rows)} questions, '
          f'{long_count} over {SOFT_LIMIT} words, {multi} controls with 2+ questions, {status}')
    for p in problems:
        print(f'  FAIL {p}')
    sys.exit(1 if problems else 0)


if __name__ == '__main__':
    main()
