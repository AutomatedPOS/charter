# Pinned NIST content

Source: https://github.com/usnistgov/oscal-content
Release: v1.6.0
Commit: f0de6d8d8c059d374f15e0ae07508d82e370fc1d
Path: nist.gov/SP800-53/rev5/json/
Local path: oscal/nist.gov/SP800-53/rev5/json/ (mirrors the source path, so NIST's relative catalog links work unchanged)
Catalog version: 5.2.0 (OSCAL 1.2.3, last modified 2026-10-22)

These files are unmodified copies. Do not edit them. To update, fetch a new release and change this file.

| File | SHA-256 |
| --- | --- |
| NIST_SP-800-53_rev5_catalog.json | 64ca6b4161de51ab6af098a7d101d326f14c95e1abf721396cd8a049e8115eeb |
| NIST_SP-800-53_rev5_LOW-baseline_profile.json | cfd4f5d9a192eb42dc04b745d82f95a85926a2a85a45418034a380a42bda9424 |
| NIST_SP-800-53_rev5_MODERATE-baseline_profile.json | e3a0f11237cfaac24dfcf1586e07683f17423757fd84208deb33196b12e8f590 |
| NIST_SP-800-53_rev5_HIGH-baseline_profile.json | d2ef340986b9f1ee820ad866a0f964d9a9d1088b24080c74b795ddb0148b9f83 |
| NIST_SP-800-53_rev5_PRIVACY-baseline_profile.json | c0e3d54d9f474bc6c33338a8e524bc52ad070f94f9274db7ec48242242fecacc |

## Draft AI overlay sources

The `profile-ai-*` files in `oscal/profiles/` are drafts. They import the catalog above. They use only control ids from the sources below; no source text is copied.

SAFE-AI (`profile-ai-safe-ai-*`): "SAFE-AI: A Framework for Securing AI-Enabled Systems", MITRE MP250397, April 2025, Appendix D Table 2. ©2025 The MITRE Corporation, all rights reserved. "Approved for Public Release; Distribution Unlimited", Public Release Case Number 25-1028. Only the control ids and the report's own L/M/H column were used. That column matches NIST's baselines on all 96 non-PM rows. The report marks PM controls LMH; PM is in no NIST baseline.

NIST COSAiS (`profile-ai-nist-cosais-predictive-draft-*`): "Control Overlay for Securing AI Systems: Using and Fine-Tuning Predictive AI", annotated outline, January 2026, intended as NISTIR 8605/8605A. 11 controls from its summary table and 48 from its additional proposed list. NIST states the list is not complete. No public draft or final overlay exists as of 2026-10-29. The project was renamed COSIS on 2026-10-20.
