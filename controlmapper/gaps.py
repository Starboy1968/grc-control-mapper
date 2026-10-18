"""Gap and coverage analysis."""

from collections import defaultdict
from dataclasses import dataclass, field

from .catalog import BY_ID, CATALOG, FAMILIES

# Priority guide for gap triage. Judgment call, documented in README.
HIGH_PRIORITY = {
    "IA-2", "IA-5", "AC-2", "AC-6", "IR-4", "IR-8", "IR-6", "CP-9",
    "RA-3", "RA-5", "SI-2", "SC-8", "SC-28", "SA-9", "AU-2", "AU-6",
}


@dataclass
class Coverage:
    covered: dict = field(default_factory=dict)   # control_id -> [statement ids]
    pending: dict = field(default_factory=dict)   # needs human review only
    gaps: list = field(default_factory=list)      # control ids with nothing
    by_family: dict = field(default_factory=dict)
    percent: float = 0.0


def analyze(results: list, baseline_ids=None) -> Coverage:
    baseline = list(baseline_ids) if baseline_ids else [c.id for c in CATALOG]
    unknown = [b for b in baseline if b not in BY_ID]
    if unknown:
        raise ValueError(f"Unknown control IDs in baseline: {', '.join(unknown)}")

    covered, pending = defaultdict(list), defaultdict(list)
    for r in results:
        for m in r.mappings:
            bucket = pending if m.needs_review else covered
            bucket[m.control_id].append(r.statement.id)

    gaps = [cid for cid in baseline if cid not in covered and cid not in pending]
    fam = {}
    for code, name in FAMILIES.items():
        ids = [c for c in baseline if c.startswith(code + "-")]
        if not ids:
            continue
        done = [c for c in ids if c in covered]
        fam[code] = {
            "name": name,
            "total": len(ids),
            "covered": len(done),
            "percent": round(100 * len(done) / len(ids), 1),
        }
    in_scope_covered = [c for c in baseline if c in covered]
    pct = round(100 * len(in_scope_covered) / len(baseline), 1) if baseline else 0.0
    return Coverage(
        covered={k: v for k, v in covered.items() if k in baseline},
        pending={k: v for k, v in pending.items() if k in baseline},
        gaps=gaps,
        by_family=fam,
        percent=pct,
    )


def priority(control_id: str) -> str:
    return "High" if control_id in HIGH_PRIORITY else "Medium"
