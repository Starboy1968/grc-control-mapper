# GRC Control Mapper: A Strategic Assessment Tool

> "Know the enemy and know yourself." Sun Tzu, *The Art of War*

Turns a security policy into an audit-ready control mapping, then reads the result as a battle plan. It maps each policy requirement to NIST SP 800-53 Rev. 5 controls (with a CSF 2.0 crosswalk), finds the gaps, and tells leadership **where the organization is weakest and what to fix first**.

**Why it exists:** mapping policies to controls is slow, repetitive GRC work, and a list of gaps does not tell leaders what matters. This tool does the first pass in seconds, ranks the weak ground, and keeps a human analyst in charge of the final call.

## Quick start

```bash
python3 -m controlmapper samples/acme_infosec_policy.md -o reports
```

No dependencies for the core. Output: `reports/acme_infosec_policy_report.md` and `.json`.

**Sample result** (fictional policy): 20 statements, 42.9% high-confidence coverage, 17 gaps, 13 mappings queued for review. Overall posture: **Open ground**, because the policy says nothing about logging or monitoring. See [`reports/`](reports/).

## The Art of War lens

The report groups every control under one principle from the book (paraphrased, chapter named). The posture is set by the **weakest** lens, not the average, because an attacker goes where you are least ready (Ch. VI, Weak Points and Strong).

| Lens | Principle | Question it answers |
|---|---|---|
| **Defense** (Ch. IV) | Make yourself unbeatable first | Can an attacker get in, move around, or stay in? |
| **Intelligence** (Ch. III, XIII) | Know the enemy and yourself | Would we see an attack? Do we know what we own? |
| **Speed** (Ch. II) | A long fight drains you | How fast can we respond and recover? |
| **Discipline** (Ch. I) | Clear command, trained people | Do leaders, staff, and vendors follow the rules? |

Each lens gets a posture: **Fortified** (75%+), **Defensible** (50%+), **Exposed** (25%+), **Open ground** (below 25%). The report then shows:

1. **Weakest ground:** the lens most open to attack.
2. **Know the enemy:** the real attacker techniques (MITRE ATT&CK) your policy leaves open.
3. **Fix first:** the top five controls to close, ranked by how much attacker risk each one closes.
4. **Unverified troops:** controls with only weak support. They count as untested until an analyst confirms them.

### Threat-informed ranking (MITRE ATT&CK)

Each of 27 common ATT&CK techniques lists the controls that help stop it. If those controls are missing, the technique is exposed. Risk = how often attackers use it (1 to 3) x the share of its controls that are missing. A control's threat score is the exposed risk it would close, split across the missing controls so no technique is counted many times. The result: the fix-first list says *"close SI-4 first because it helps stop credential theft and data exfiltration,"* not just *"SI-4 is missing."*

**Honest limits:** the technique-to-control links and the 1 to 3 weights are a curated starting set I wrote from public ATT&CK mitigations and common breach reporting. They are **not** the official MITRE Center for Threat-Informed Defense mapping. The report says so on every run.

## How it works

```
Policy file → Parser → Mapper → Analyst review → Gap analysis → Strategy → Report
              (obligation   (TF-IDF +     (accept /       (vs. baseline)   (4 lenses)  (MD + JSON)
               sentences)    keyword        reject)
                             phrases)
```

1. **Parser** keeps sentences with obligation words (shall, must, will, required).
2. **Mapper** scores each statement against each control with TF-IDF cosine similarity plus a boost for exact control phrases. Pure Python, deterministic, and every score lists the terms that caused it.
3. **Review queue:** scores below 0.45 are flagged. Analysts accept or reject them in a JSON decisions file (`--decisions`).
4. **Gap analysis** counts only high-confidence or analyst-accepted mappings as coverage. Gaps are ranked High or Medium.
5. **Strategy** regroups the same coverage numbers into the four lenses, then **threat ranking** scores the open gaps against ATT&CK techniques. Every score traces back to a mapping.
6. **Optional LLM second opinion** (`--llm`): an LLM re-scores the candidates the baseline found. It cannot add new controls, must justify each verdict, and any failure falls back to the baseline.

## Design choices

| Choice | Reason |
|---|---|
| Explainable baseline first | Auditors need to see why a mapping exists |
| LLM can only re-rank | Prevents invented control mappings |
| Low confidence is not coverage | A weak match must never make a gap look closed |
| Posture follows the weakest lens | One open flank is enough for an attacker |
| Fix-first ranked by attacker risk | Leaders fix what attackers actually use, not what is alphabetically first |
| Threat data labeled as curated | Does not pretend to be the official MITRE mapping |
| Every control sits in exactly one lens | Enforced by a test, so nothing is counted twice or missed |
| Human decisions file | Keeps a record of who accepted what |
| No real client data | Public frameworks and a fictional sample policy only |

## Usage

```bash
# Scope gaps to your own baseline (one control ID per line)
python3 -m controlmapper policy.md --baseline my_baseline.txt

# Apply analyst decisions
python3 -m controlmapper policy.md --decisions decisions.json
# {"S001": {"AC-2": "accept", "SC-13": "reject"}}

# Add LLM second opinion
pip install anthropic && export ANTHROPIC_API_KEY=...
python3 -m controlmapper policy.md --llm
```

## Tests

```bash
pip install pytest && python3 -m pytest -q
```

64 tests cover the parser, mapper accuracy on known statements, review flags, decisions, gap math, the strategy lenses and posture bands, ATT&CK exposure and ranking math, reports, the LLM reviewer (with a fake client, no network), and the CLI.

## Limits (read these)

- The catalog is a curated subset of 800-53 (42 controls), not the full set.
- The lens groupings and posture bands are a judgment call, not a standard. They are documented in `controlmapper/strategy.py` and easy to change.
- The ATT&CK technique list (27 techniques), its control links, and its weights are curated by hand, not the official CTID mapping. See `controlmapper/threat.py`.
- Fix-first only looks at the weakest lens. A bigger threat in another lens still shows up in the attack paths table.
- Keyword and TF-IDF matching misses unusual wording. That is why the review queue exists.
- Some false positives happen, for example AT-3 on a general training statement. They land in review, not in coverage.
- Control descriptions are plain-language summaries, not official NIST text.
- This is decision support. It is not audit evidence.

## Roadmap

- Full 800-53 catalog from NIST OSCAL JSON
- Load the official MITRE CTID NIST 800-53 to ATT&CK mapping instead of the curated set
- ISO 27001 and SOC 2 crosswalks
- Evidence tracking per control
- Streamlit review interface

## Author

Rashon Alsberry, AURA-BOROS LLC. Built to show how AI can speed up GRC work while keeping people accountable.

License: MIT
