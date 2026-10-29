# Charter

Charter puts security controls into arc42 architecture documents, so control selection happens during design.

It reads an OSCAL profile, such as the NIST SP 800-53 Rev 5 moderate baseline, and places each control in the arc42 chapter where it belongs. Each control appears as a question for the architect to answer in place.

Status: early. Nothing to run yet.

## How it will work

1. Copy the arc42 template, twelve chapter files.
2. Run `charter attach <profile>`.
3. Each chapter that has controls gets a `### Security controls` section at the bottom.
4. Answer the questions in place. Rerunning `attach` refreshes the questions and keeps your answers.

Charter works with any OSCAL catalog, not only 800-53.

## Sources

- NIST SP 800-53 Rev 5 catalog and baselines, from the NIST OSCAL content repository.
- arc42 architecture template.
