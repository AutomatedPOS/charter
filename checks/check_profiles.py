"""Check every OSCAL profile in the repo.

1. Validates against the pinned OSCAL profile JSON schema.
2. Checks that every JSON catalog link equals CATALOG_HREF, the string NIST's own profiles use.

Run from the repo root: python checks/check_profiles.py
Needs: jsonschema, regex (the schema uses \\p{...} patterns that Python's re cannot compile).
Exits 1 if any check fails.
"""
import json
import pathlib
import sys

import jsonschema
import regex
from jsonschema import validators

ROOT = pathlib.Path(__file__).resolve().parent.parent
SCHEMA = ROOT / 'oscal/schema/oscal_profile_schema.json'
CATALOG_HREF = '../../../../nist.gov/SP800-53/rev5/json/NIST_SP-800-53_rev5_catalog.json'
CATALOG_JSON = 'application/oscal.catalog+json'


def pattern(validator, patrn, instance, schema):
    if validator.is_type(instance, 'string') and not regex.search(patrn, instance):
        yield jsonschema.ValidationError(f'{instance!r} does not match {patrn!r}')


Validator = validators.extend(jsonschema.Draft7Validator, {'pattern': pattern})


def profiles():
    yield from sorted((ROOT / 'oscal/profiles').glob('*.json'))
    yield from sorted((ROOT / 'oscal/nist.gov').rglob('*_profile.json'))


def catalog_links(profile):
    resources = {r['uuid']: r for r in profile.get('back-matter', {}).get('resources', [])}
    for imp in profile['imports']:
        href = imp['href']
        if not href.startswith('#'):
            yield href
            continue
        for link in resources[href[1:]].get('rlinks', []):
            if link.get('media-type', CATALOG_JSON) == CATALOG_JSON:
                yield link['href']


def main():
    validator = Validator(json.loads(SCHEMA.read_text(encoding='utf-8')))
    failures = 0
    for path in profiles():
        doc = json.loads(path.read_text(encoding='utf-8'))
        problems = [f'schema: {"/".join(map(str, e.absolute_path)) or "(root)"}: {e.message[:200]}'
                    for e in validator.iter_errors(doc)]
        problems += [f'catalog href {href!r} is not {CATALOG_HREF!r}'
                     for href in catalog_links(doc['profile']) if href != CATALOG_HREF]
        name = path.relative_to(ROOT).as_posix()
        if problems:
            failures += 1
            print(f'FAIL {name}')
            for p in problems:
                print(f'  {p}')
        else:
            print(f'ok   {name}')
    print(f'{failures} profile(s) failed' if failures else 'all profiles pass')
    return 1 if failures else 0


if __name__ == '__main__':
    sys.exit(main())
