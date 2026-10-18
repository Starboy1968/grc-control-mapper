"""Strategic assessment: read the control coverage through Sun Tzu's *Art of War*.

Each lens groups controls by the job they do and ties that job to one
principle from the book (paraphrased, chapter named). The numbers come
from the same gap analysis as the rest of the report; this module only
re-groups them so a leader can see where the organization is strong,
where it is open to attack, and what to fix first.
"""

from dataclasses import dataclass, field

from .catalog import BY_ID, CATALOG
from .gaps import Coverage, priority


@dataclass(frozen=True)
class Lens:
    key: str
    name: str
    chapter: str
    principle: str
    question: str
    controls: tuple


LENSES = (
    Lens(
        "defense", "Defense: be unbeatable first", "Ch. IV, Tactical Dispositions",
        "Make yourself unbeatable before anything else. Do not count on the enemy's mistakes.",
        "Can an attacker get in, move around, or stay in?",
        ("IA-2", "IA-5", "AC-2", "AC-3", "AC-6", "AC-7", "AC-17", "SC-7", "SC-8",
         "SC-13", "SC-28", "SI-2", "SI-3", "CM-2", "CM-3", "CP-9"),
    ),
    Lens(
        "intelligence", "Intelligence: know the enemy and yourself", "Ch. III and XIII, Attack by Stratagem and Use of Spies",
        "Knowing both the enemy and yourself, you can face many battles without fear. Good intelligence decides the outcome.",
        "Would we see an attack, and do we know what we own and where we are weak?",
        ("AU-2", "AU-6", "AU-11", "SI-4", "CA-7", "RA-3", "RA-5", "CM-8"),
    ),
    Lens(
        "speed", "Speed: a long fight drains you", "Ch. II, Waging War",
        "Long, drawn-out conflict drains the state. Speed in response protects the organization.",
        "How fast can we respond, contain, and recover?",
        ("IR-4", "IR-5", "IR-6", "IR-8", "CP-2", "CP-10"),
    ),
    Lens(
        "discipline", "Discipline: clear command, trained people", "Ch. I, Laying Plans",
        "Victory starts with clear command, trained people, and rules everyone follows.",
        "Does leadership set direction, and do people and vendors follow the rules?",
        ("AC-1", "AC-5", "AT-2", "AT-3", "PS-3", "PS-4", "PE-2", "MP-6",
         "PM-9", "SA-9", "SR-2", "CA-2"),
    ),
)

# Posture bands, checked from the top down.
POSTURES = ((75.0, "Fortified"), (50.0, "Defensible"), (25.0, "Exposed"), (0.0, "Open ground"))


def posture(percent: float) -> str:
    for floor, label in POSTURES:
        if percent >= floor:
            return label
    return POSTURES[-1][1]


@dataclass
class LensResult:
    lens: Lens
    in_scope: list
    covered: list
    unverified: list      # low-confidence only: claimed but not proven
    open_gaps: list       # nothing supports them
    percent: float
    posture: str


@dataclass
class Strategy:
    lenses: list = field(default_factory=list)
    weakest: LensResult = None
    fix_first: list = field(default_factory=list)
    overall: str = ""


def assess(coverage: Coverage, baseline_ids=None) -> Strategy:
    """Group coverage by lens and find the weakest ground."""
    # Scope is the baseline the gap analysis used: covered + pending + gaps.
    scope = set(baseline_ids) if baseline_ids else (
        set(coverage.covered) | set(coverage.pending) | set(coverage.gaps)
    )
    results = []
    for lens in LENSES:
        ids = [c for c in lens.controls if c in scope]
        if not ids:
            continue
        covered = [c for c in ids if c in coverage.covered]
        unverified = [c for c in ids if c in coverage.pending and c not in coverage.covered]
        gaps = [c for c in ids if c in coverage.gaps]
        pct = round(100 * len(covered) / len(ids), 1)
        results.append(LensResult(lens, ids, covered, unverified, gaps, pct, posture(pct)))

    if not results:
        return Strategy()

    weakest = min(results, key=lambda r: (r.percent, r.lens.key))
    todo = weakest.open_gaps + weakest.unverified
    todo = sorted(todo, key=lambda c: (priority(c) != "High", c in weakest.unverified, c))
    return Strategy(
        lenses=results,
        weakest=weakest,
        fix_first=todo[:5],
        overall=weakest.posture,
    )


def to_dict(s: Strategy) -> dict:
    if not s.lenses:
        return {}
    return {
        "overall_posture": s.overall,
        "weakest_ground": s.weakest.lens.key,
        "fix_first": s.fix_first,
        "lenses": [
            {
                "key": r.lens.key,
                "name": r.lens.name,
                "chapter": r.lens.chapter,
                "percent": r.percent,
                "posture": r.posture,
                "covered": r.covered,
                "unverified": r.unverified,
                "gaps": r.open_gaps,
            }
            for r in s.lenses
        ],
    }


def to_markdown(s: Strategy) -> list:
    """Markdown lines for the report's strategic section."""
    if not s.lenses:
        return []
    w = s.weakest
    lines = [
        "## Strategic assessment (Art of War lens)",
        "",
        f"**Overall posture: {s.overall}.** An attacker strikes where you are weakest, "
        "so the posture is set by the weakest lens, not the average (Ch. VI, Weak Points and Strong).",
        "",
        "| Lens | Chapter | Covered | Posture |",
        "|---|---|---:|---|",
    ]
    for r in s.lenses:
        lines.append(
            f"| {r.lens.name} | {r.lens.chapter} | {len(r.covered)}/{len(r.in_scope)} ({r.percent}%) | {r.posture} |"
        )
    lines += ["", "### Weakest ground", "",
              f"**{w.lens.name}.** {w.lens.principle}", "",
              f"*Question to answer:* {w.lens.question}", ""]
    if s.fix_first:
        lines += ["### Fix first", "",
                  "Ranked by risk. High-priority gaps come first, then claims no one has verified yet.", "",
                  "| Order | Control | Title | State |", "|---:|---|---|---|"]
        for i, cid in enumerate(s.fix_first, 1):
            state = "Unverified claim" if cid in w.unverified else "No policy support"
            lines.append(f"| {i} | {cid} | {BY_ID[cid].title} | {state} |")
        lines.append("")
    unverified = [(r.lens.name, c) for r in s.lenses for c in r.unverified]
    if unverified:
        lines += ["### Unverified troops", "",
                  "These controls have only weak policy support. Treat them as untested until an analyst confirms them.", ""]
        for name, c in unverified:
            lines.append(f"- {c} {BY_ID[c].title} ({name.split(':')[0]})")
        lines.append("")
    return lines
