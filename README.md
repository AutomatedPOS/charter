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

## Drafts

The AI overlay profiles in `oscal/profiles/profile-ai-*` are drafts. Both are derived from draft or third-party material:

- MITRE SAFE-AI, "A Framework for Securing AI-Enabled Systems" (April 2025), Appendix D.
- NIST COSAiS annotated outline, "Control Overlay for Securing AI Systems: Using and Fine-Tuning Predictive AI" (January 2026).

They will be replaced when NIST publishes its AI overlays.

The SAFE-AI profiles keep the four PM controls MITRE names (PM-7, PM-12, PM-18, PM-30). The generator skips the PM family, per the placement map, so they do not appear in chapter output.
