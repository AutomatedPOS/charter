"""Build the control-id to baseline membership table.

Resolves the pinned NIST low, moderate and high profiles with trestle and writes
data/baseline-membership.csv: one row per control in at least one baseline,
in catalog order, with an x under each baseline that contains it.

Run from anywhere: python scripts/build_membership.py
Needs: compliance-trestle (build time only).
"""
import csv
import os
import pathlib
import tempfile

from trestle.core.profile_resolver import ProfileResolver

ROOT = pathlib.Path(__file__).resolve().parent.parent
NIST = ROOT / 'oscal/nist.gov/SP800-53/rev5/json'
OUT = ROOT / 'data/baseline-membership.csv'
LEVELS = ['low', 'moderate', 'high']


def control_ids(catalog):
    ids = []
    def walk(controls):
        for c in controls or []:
            ids.append(c.id)
            walk(c.controls)
    for g in catalog.groups or []:
        walk(g.controls)
    walk(catalog.controls)
    return ids


def catalog_order():
    """Control ids in the order the pinned catalog lists them."""
    import json
    cat = json.loads((NIST / 'NIST_SP-800-53_rev5_catalog.json').read_text(encoding='utf-8'))['catalog']
    order = []
    def walk(controls):
        for c in controls:
            order.append(c['id'])
            walk(c.get('controls', []))
    for g in cat['groups']:
        walk(g.get('controls', []))
    return {cid: i for i, cid in enumerate(order)}


def main():
    members = {}
    # trestle resolves relative hrefs against the working folder; NIST's hrefs assume this one.
    cwd = os.getcwd()
    with tempfile.TemporaryDirectory() as trestle_root:
        (pathlib.Path(trestle_root) / '.trestle/cache').mkdir(parents=True)
        os.chdir(NIST)
        try:
            for level in LEVELS:
                profile = f'NIST_SP-800-53_rev5_{level.upper()}-baseline_profile.json'
                resolved = ProfileResolver.get_resolved_profile_catalog(pathlib.Path(trestle_root), profile)
                members[level] = set(control_ids(resolved))
                print(f'{level}: {len(members[level])} controls')
        finally:
            os.chdir(cwd)

    order = catalog_order()
    rows = sorted(set().union(*members.values()), key=order.__getitem__)
    OUT.parent.mkdir(exist_ok=True)
    with OUT.open('w', newline='', encoding='utf-8') as f:
        w = csv.writer(f, lineterminator='\n')
        w.writerow(['control_id'] + LEVELS)
        for cid in rows:
            w.writerow([cid] + ['x' if cid in members[level] else '' for level in LEVELS])
    print(f'{len(rows)} rows -> {OUT.relative_to(ROOT).as_posix()}')


if __name__ == '__main__':
    main()
