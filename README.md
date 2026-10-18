# GRC Control Mapper

Turns a security policy into an audit-ready control mapping. It reads the policy, maps each requirement to NIST SP 800-53 Rev. 5 controls (with a CSF 2.0 crosswalk), finds gaps, and queues weak matches for a human analyst.

**Why it exists:** mapping policies to controls is slow, repetitive GRC work. This tool does the first pass in seconds and keeps the analyst in charge of the final call.

## Quick start

```bash
python3 -m controlmapper samples/acme_infosec_policy.md -o reports
```

No dependencies for the core. Output: `reports/acme_infosec_policy_report.md` and `.json`.

Sample result: 20 statements, 42.9% high-confidence coverage, 17 gaps, 13 mappings queued for review. See [`reports/`](reports/).

## How it works

```
Policy file → Parser → Mapper → Analyst review → Gap analysis → Report
              (obligation   (TF-IDF +     (accept /       (vs. baseline)   (MD + JSON)
               sentences)    keyword        reject)
                             phrases)
```

1. **Parser** keeps sentences with obligation words (shall, must, will, required).
2. **Mapper** scores each statement against each control with TF-IDF cosine similarity plus a boost for exact control phrases. Pure Python, deterministic, and every score lists the terms that caused it.
3. **Review queue:** scores below 0.45 are flagged. Analysts accept or reject them in a JSON decisions file (`--decisions`).
4. **Gap analysis** counts only high-confidence or analyst-accepted mappings as coverage. Gaps are ranked High or Medium.
5. **Optional LLM second opinion** (`--llm`): an LLM re-scores the candidates the baseline found. It cannot add new controls, must justify each verdict, and any failure falls back to the baseline.

## Design choices

| Choice | Reason |
|---|---|
| Explainable baseline first | Auditors need to see why a mapping exists |
| LLM can only re-rank | Prevents invented control mappings |
| Low confidence is not coverage | A weak match must never make a gap look closed |
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

37 tests cover the parser, mapper accuracy on known statements, review flags, decisions, gap math, reports, the LLM reviewer (with a fake client, no network), and the CLI.

## Limits (read these)

- The catalog is a curated subset of 800-53 (43 controls), not the full set.
- Keyword and TF-IDF matching misses unusual wording. That is why the review queue exists.
- Some false positives happen, for example AT-3 on a general training statement. They land in review, not in coverage.
- Control descriptions are plain-language summaries, not official NIST text.
- This is decision support. It is not audit evidence.

## Roadmap

- Full 800-53 catalog from NIST OSCAL JSON
- ISO 27001 and SOC 2 crosswalks
- Evidence tracking per control
- Streamlit review interface

## Author

Rashon Alsberry, AURA-BOROS LLC. Built to show how AI can speed up GRC work while keeping people accountable.

License: MIT
