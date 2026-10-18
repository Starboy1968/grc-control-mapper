"""Render results as Markdown and JSON."""

import json
from datetime import date

from .catalog import BY_ID
from .gaps import Coverage, priority
from . import strategy as strat


def _short(text: str, n: int = 140) -> str:
    text = text.replace("|", "\\|")
    return text if len(text) <= n else text[: n - 1].rstrip() + "…"


def to_json(results: list, coverage: Coverage, source: str = "") -> str:
    payload = {
        "source": source,
        "generated": date.today().isoformat(),
        "coverage_percent": coverage.percent,
        "gaps": coverage.gaps,
        "strategy": strat.to_dict(strat.assess(coverage)),
        "statements": [
            {
                "id": r.statement.id,
                "section": r.statement.section,
                "text": r.statement.text,
                "mappings": [
                    {
                        "control": m.control_id,
                        "score": m.score,
                        "confidence": m.confidence,
                        "needs_review": m.needs_review,
                        "matched_terms": m.matched_terms,
                        "source": m.source,
                    }
                    for m in r.mappings
                ],
            }
            for r in results
        ],
    }
    return json.dumps(payload, indent=2)


def to_markdown(results: list, coverage: Coverage, source: str = "") -> str:
    total = len(results)
    mapped = sum(1 for r in results if r.mappings)
    review = [(r, m) for r in results for m in r.mappings if m.needs_review]
    lines = [
        "# Policy-to-Control Mapping Report",
        "",
        f"- **Source:** {source or 'n/a'}",
        f"- **Generated:** {date.today().isoformat()}",
        f"- **Framework:** NIST SP 800-53 Rev. 5 (curated subset), CSF 2.0 crosswalk",
        "",
        "## Executive summary",
        "",
        f"- **{coverage.percent}%** of in-scope controls have a high-confidence policy statement.",
        f"- **{mapped} of {total}** policy statements mapped to at least one control.",
        f"- **{len(coverage.gaps)}** controls have no supporting statement (gaps).",
        f"- **{len(review)}** mappings are low confidence and need analyst review.",
        "",
    ]
    lines += strat.to_markdown(strat.assess(coverage))
    lines += [
        "## Coverage by control family",
        "",
        "| Family | Covered | Total | % |",
        "|---|---:|---:|---:|",
    ]
    for code, f in coverage.by_family.items():
        lines.append(f"| {code} {f['name']} | {f['covered']} | {f['total']} | {f['percent']}% |")

    lines += ["", "## Gaps (no supporting statement)", ""]
    if coverage.gaps:
        lines += ["| Priority | Control | Title | CSF |", "|---|---|---|---|"]
        ordered = sorted(coverage.gaps, key=lambda c: (priority(c) != "High", c))
        for cid in ordered:
            c = BY_ID[cid]
            lines.append(f"| {priority(cid)} | {cid} | {c.title} | {c.csf} |")
    else:
        lines.append("No gaps found.")

    lines += ["", "## Mapped statements", "",
              "| ID | Section | Statement | Control | Score | Confidence |",
              "|---|---|---|---|---:|---|"]
    for r in results:
        for m in r.mappings:
            lines.append(
                f"| {r.statement.id} | {_short(r.statement.section, 30)} | "
                f"{_short(r.statement.text)} | {m.control_id} | {m.score:.2f} | {m.confidence} |"
            )

    lines += ["", "## Analyst review queue", ""]
    if review:
        lines += ["Low-confidence mappings. Accept or reject each before using this report in an audit.",
                  "", "| Statement | Control | Score | Matched terms |", "|---|---|---:|---|"]
        for r, m in review:
            lines.append(
                f"| {r.statement.id} | {m.control_id} | {m.score:.2f} | {', '.join(m.matched_terms)} |"
            )
    else:
        lines.append("Nothing needs review.")

    unmapped = [r for r in results if not r.mappings]
    lines += ["", "## Unmapped statements", ""]
    if unmapped:
        for r in unmapped:
            lines.append(f"- **{r.statement.id}** ({r.statement.section}): {_short(r.statement.text, 200)}")
    else:
        lines.append("Every statement mapped to at least one control.")

    lines += ["", "---", "",
              "*Method: TF-IDF similarity plus keyword phrase matching. "
              "Scores are decision support, not audit evidence. A human reviews every low-confidence mapping.*", ""]
    return "\n".join(lines)
