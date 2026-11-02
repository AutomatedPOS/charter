# Charter

Charter puts security controls into arc42 architecture documents, so control selection happens during design.

It reads an OSCAL profile, such as the NIST SP 800-53 Rev 5 baseline, and places each control in the arc42 chapter where it belongs. Each control appears as a question for the architect to answer in place.

**Status: v0.2.0 Pre-release - Working and ready for use.**

---

## Getting Started

### Quick Start

```bash
# Clone the repository
git clone https://github.com/farathZ/charter.git
cd charter

# Install dependencies
pip install -r requirements.txt

# Generate all packages (creates build/ folder)
python scripts/generate.py
```

This creates 15 ready-to-use packages in the `build/` directory.

### Your First Assessment

1. **Pick a package** from `build/` based on your needs:
   - Standard: `nist-800-53r5.2-moderate.zip`
   - AI systems: `nist-800-53r5.2-ai-safe-ai-draft-moderate.zip` or `nist-800-53r5.2-ai-cosais-predictive-draft-moderate.zip`
   - OT systems: `nist-800-53r5.2-ot-moderate.zip`

2. **Extract the package** to a working directory:
   ```bash
   mkdir my-assessment
   cd my-assessment
   unzip ../charter/build/nist-800-53r5.2-ai-safe-ai-draft-moderate.zip
   ```

3. **Start with START-HERE.md** - answer the 18 system questions first

4. **Work through chapters** 01-12, answering control questions as you go

---

## How It Works

Charter generates **arc42 architecture packages** with security controls placed as design questions in the chapters where they belong. Each package includes:

- `START-HERE.md` - 18 foundational system questions
- `01_introduction_and_goals.md` through `12_glossary.md` - arc42 chapters with embedded control questions
- `README.md` - Package-specific information
- `AGENTS.md` - Instructions for AI assistants

### Control Placement

Each NIST 800-53 control is placed in the arc42 chapter where it logically belongs:

| Chapter | Controls |
|---------|----------|
| 1. Introduction and Goals | PL (Planning), PM (Program Management - org-level) |
| 2. Architecture Constraints | PL-2 (Security/Privacy Plans) |
| 3. Context and Scope | CA (Assessment), SC (System & Communications) |
| 4. Solution Strategy | SA (System & Services Acquisition), SR (Supply Chain) |
| 5. Building Block View | CM (Configuration Management), AC (Access Control), IA (Identification) |
| 6. Runtime View | SI (System & Information Integrity) |
| 7. Deployment View | CP (Contingency Planning), MP (Media Protection), PE (Physical) |
| 8. Cross-cutting Concepts | AT (Awareness), AU (Audit), IR (Incident Response), PS (Personnel), PT (Privacy) |
| 9. Architecture Decisions | Tailoring decisions |
| 10. Quality Requirements | Baseline requirements |
| 11. Risks and Technical Debts | RA (Risk Assessment), parked items |
| 12. Glossary | - |

---

## For AI System Assessments

### Available AI Packages

| Package | Framework | Impact Levels | Status |
|---------|-----------|----------------|--------|
| `nist-800-53r5.2-ai-safe-ai-draft-*` | MITRE SAFE-AI | low, moderate, high | Draft |
| `nist-800-53r5.2-ai-cosais-predictive-draft-*` | NIST COSAiS | low, moderate, high | Draft |

### Selecting an AI Package

**MITRE SAFE-AI** is based on "A Framework for Securing AI-Enabled Systems" (April 2025). Use this for:
- General AI systems
- Comprehensive security framework
- MITRE's control set

**NIST COSAiS** is based on "Control Overlay for Securing AI Systems: Using and Fine-Tuning Predictive AI" (January 2026). Use this for:
- Predictive AI systems
- Fine-tuning scenarios
- NIST-aligned controls

### AI Assessment Workflow

1. **In START-HERE.md:**
   - Set **sh-14** to `AI system` (enables AI-specific controls)
   - Set **sh-18** to your personal information types (e.g., `user data, conversation logs, training inputs`) (enables privacy overlay)
   - Complete **sh-05, sh-15, sh-16, sh-17, sh-12** for impact rating

2. **Focus on these chapters:**
   - **Chapter 05** (Building Block View): Model architecture, training data, components
   - **Chapter 07** (Deployment View): Model serving, inference endpoints
   - **Chapter 08** (Cross-cutting): Privacy, access, auditing
   - **Chapter 11** (Risks): AI-specific risks (prompt injection, data poisoning, model theft)

3. **Answer control questions** in each chapter's "Security controls" section

4. **Park unanswered items** in Chapter 11 under "Parked items"

### AI-Specific Controls

AI overlay packages include controls for:
- AI risk management and assessment
- Data quality and provenance
- Model validation and verification
- Human-AI interaction safety
- Governance and oversight

---

## Package Types

### Standard Baselines
NIST SP 800-53 Rev 5 baselines without overlays:
- `nist-800-53r5.2-low.zip`
- `nist-800-53r5.2-moderate.zip`
- `nist-800-53r5.2-high.zip`

### OT Overlay
NIST SP 800-82 Rev 3 (OT/ICS systems):
- `nist-800-53r5.2-ot-low.zip`
- `nist-800-53r5.2-ot-moderate.zip`
- `nist-800-53r5.2-ot-high.zip`

### AI Overlays (Draft)
AI-specific control overlays:
- `nist-800-53r5.2-ai-safe-ai-draft-low.zip`
- `nist-800-53r5.2-ai-safe-ai-draft-moderate.zip`
- `nist-800-53r5.2-ai-safe-ai-draft-high.zip`
- `nist-800-53r5.2-ai-cosais-predictive-draft-low.zip`
- `nist-800-53r5.2-ai-cosais-predictive-draft-moderate.zip`
- `nist-800-53r5.2-ai-cosais-predictive-draft-high.zip`

**Note:** All packages include the NIST Privacy Baseline as an add-on overlay, activated by answering **sh-18** in START-HERE.md.

---

## Answering Control Questions

Each control appears as a question block:

```markdown
<!-- charter:control id="ac-1" profile="nist-800-53r5.2-moderate" -->
#### Access Control Policy and Procedures  `AC-1`  `[M H]`

**Ask:**
1. Which access control policy and procedures govern this system?
2. Who owns them, and when were they last reviewed?

**Status:** implemented / partial / planned / alternative / not-applicable
**Origination:** organization / system-specific / customer-configured / customer-provided / inherited
**Answer state:** answered / parked: <reason>
**Answer:** Your response here

**See also:** AC-2 (chapter 5), AC-3 (chapter 5)

<!-- /charter:control -->
```

### Field Descriptions

| Field | Values | Description |
|-------|--------|-------------|
| **Status** | implemented, partial, planned, alternative, not-applicable | Current state of the control |
| **Origination** | organization, system-specific, customer-configured, customer-provided, inherited | Where the control comes from |
| **Answer state** | answered, parked: <reason> | Whether the question is answered or waiting on someone |
| **Answer** | Free text | Your actual response to the control questions |

---

## Workflow

### Step 1: Answer START-HERE.md
Complete all 18 questions. These answers:
- Pre-fill control questions throughout the chapters
- Determine impact level (sh-12)
- Enable overlays (sh-14 for AI, sh-18 for privacy)

### Step 2: Work Through Chapters
Start with Chapter 01 and work sequentially. Each chapter has:
- Architecture content area (write your design)
- "From START-HERE" section (pre-filled from START-HERE.md)
- "Security controls" section (control questions to answer)

### Step 3: Answer Control Questions
For each control block:
1. Read the **Ask** questions
2. Check the **Consider** notes (overlay-specific guidance)
3. Review **See also** for related controls
4. Fill in **Status**, **Origination**, **Answer state**, and **Answer**

### Step 4: Track Parked Items
Anything you cannot answer immediately:
1. Set **Answer state** to `parked: <reason>`
2. Add it to **Chapter 11** under "Parked items" with who it's waiting on

---

## Scripts

### generate.py
Generates all packages from OSCAL profiles.

```bash
python scripts/generate.py
```

**Output:** Creates `build/` directory with all packages as .zip files

**Options:** None - generates all packages at once

### build_membership.py
Builds the control-to-baseline membership table (used internally).

```bash
python scripts/build_membership.py
```

**Output:** Updates `data/baseline-membership.csv`

---

## Data Files

| File | Purpose |
|------|---------|
| `data/baseline-membership.csv` | Which controls are in which baselines (L, M, H) |
| `data/placement-families.csv` | Which arc42 chapter each control family belongs in |
| `data/placement-exceptions.csv` | Individual control placements that differ from family rule |
| `data/questions/*.csv` | Control questions (one file per NIST family) |
| `data/start-here.csv` | START-HERE question definitions |

---

## Sources

- NIST SP 800-53 Rev 5 catalog and baselines, from the NIST OSCAL content repository.
- NIST SP 800-53B Privacy Control Catalog (included as add-on overlay in all packages)
- arc42 architecture template by Gernot Starke and Peter Hruschka (CC BY-SA 4.0)

---

## Drafts

The AI overlay profiles in `oscal/profiles/profile-ai-*` are drafts. Both are derived from draft or third-party material:

- MITRE SAFE-AI, "A Framework for Securing AI-Enabled Systems" (April 2025), Appendix D.
- NIST COSAiS annotated outline, "Control Overlay for Securing AI Systems: Using and Fine-Tuning Predictive AI" (January 2026).

They will be replaced when NIST publishes its final AI overlays.

The SAFE-AI profiles keep the four PM controls MITRE names (PM-7, PM-12, PM-18, PM-30). The generator skips the PM family, per the placement map, so they do not appear in chapter output.

---

## Version History

### v0.2.0 (Current)
- Impact questions now use FIPS 199 definitions
- Privacy add-on overlay included in every package
- START-HERE.md expanded with rating guidance
- AI packages updated with latest draft overlays

### v0.1.0
- First pre-release
- Basic package generation
- Initial AI overlay support

---

## License

The arc42 chapter structure and headings come from the arc42 template by Gernot Starke and Peter Hruschka, licensed under CC BY-SA 4.0. Charter's modifications and additions are also available under CC BY-SA 4.0. Your own answers and assessments remain your property.
