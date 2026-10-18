"""Map policy statements to controls.

Baseline matcher: TF-IDF cosine similarity plus a phrase boost for
control keywords found verbatim. Pure Python, deterministic, explainable.
An optional Reviewer (for example an LLM) can re-rank the candidates;
the baseline always runs first so results stay auditable.
"""

import math
import re
from collections import Counter
from dataclasses import dataclass, field
from typing import Protocol

from .catalog import CATALOG, Control
from .parser import Statement

STOPWORDS = frozenset(
    """a an and are as at be by for from has have in is it its of on or that the
    to was were will with all any each must shall should may their this these
    those which who within than then them they we our us not no per using use
    used also such into over under when where while both other more most""".split()
)

STRONG = 0.45   # auto-accepted candidate
REVIEW = 0.18   # shown, but flagged for human review


def _stem(word: str) -> str:
    for suffix in ("ations", "ation", "ings", "ing", "ed", "es", "s"):
        if word.endswith(suffix) and len(word) - len(suffix) >= 4:
            return word[: -len(suffix)]
    return word


def tokenize(text: str) -> list:
    words = re.findall(r"[a-z0-9][a-z0-9\-]*", text.lower())
    return [_stem(w) for w in words if w not in STOPWORDS and len(w) > 1]


@dataclass
class Mapping:
    control_id: str
    score: float
    matched_terms: list = field(default_factory=list)
    needs_review: bool = False
    source: str = "baseline"

    @property
    def confidence(self) -> str:
        if self.score >= STRONG:
            return "high"
        return "low"


@dataclass
class StatementResult:
    statement: Statement
    mappings: list = field(default_factory=list)


class Reviewer(Protocol):
    """Optional second opinion on candidate mappings (e.g. an LLM)."""

    def review(self, statement: Statement, candidates: list) -> list: ...


class ControlMapper:
    def __init__(self, controls=None, top_k: int = 3):
        self.controls = list(controls or CATALOG)
        self.top_k = top_k
        docs = [Counter(tokenize(c.match_text)) for c in self.controls]
        n = len(docs)
        df = Counter()
        for d in docs:
            df.update(d.keys())
        self.idf = {t: math.log((1 + n) / (1 + f)) + 1 for t, f in df.items()}
        self.vectors = [self._weigh(d) for d in docs]

    def _weigh(self, counts: Counter) -> dict:
        vec = {t: (1 + math.log(c)) * self.idf.get(t, 1.0) for t, c in counts.items()}
        norm = math.sqrt(sum(v * v for v in vec.values())) or 1.0
        return {t: v / norm for t, v in vec.items()}

    @staticmethod
    def _cosine(a: dict, b: dict) -> float:
        if len(a) > len(b):
            a, b = b, a
        return sum(v * b.get(t, 0.0) for t, v in a.items())

    def _phrase_hits(self, control: Control, text_lower: str) -> list:
        return [k for k in control.keywords if k.lower() in text_lower]

    def map_statement(self, statement: Statement) -> StatementResult:
        tokens = tokenize(statement.text)
        vec = self._weigh(Counter(tokens))
        text_lower = statement.text.lower()
        scored = []
        for control, cvec in zip(self.controls, self.vectors):
            cos = self._cosine(vec, cvec)
            hits = self._phrase_hits(control, text_lower)
            boost = min(0.4, 0.2 * len(hits))
            score = min(1.0, cos + boost)
            if score >= REVIEW:
                shared = sorted(set(tokens) & set(tokenize(control.match_text)))
                terms = hits + [t for t in shared if not any(t in h for h in hits)][:4]
                scored.append(
                    Mapping(control.id, round(score, 3), terms,
                            needs_review=score < STRONG)
                )
        scored.sort(key=lambda m: (-m.score, m.control_id))
        return StatementResult(statement, scored[: self.top_k])

    def map_all(self, statements, reviewer: Reviewer = None) -> list:
        results = [self.map_statement(s) for s in statements]
        if reviewer is not None:
            for r in results:
                if r.mappings:
                    r.mappings = reviewer.review(r.statement, r.mappings)
        return results


def apply_decisions(results: list, decisions: dict) -> list:
    """Apply analyst decisions.

    decisions = {"S001": {"AC-2": "accept", "AC-6": "reject"}}
    Rejected mappings are removed; accepted ones are marked reviewed.
    """
    for r in results:
        d = decisions.get(r.statement.id, {})
        kept = []
        for m in r.mappings:
            verdict = d.get(m.control_id)
            if verdict == "reject":
                continue
            if verdict == "accept":
                m.needs_review = False
                m.source = "analyst"
            kept.append(m)
        r.mappings = kept
    return results
