"""Optional LLM second opinion. Needs `pip install anthropic` and ANTHROPIC_API_KEY.

The baseline mapper always runs first. The LLM only re-scores the
candidates it is given and must explain itself; it cannot add controls
the baseline did not surface. Failures fall back to the baseline result.
"""

import json
import os

from .catalog import BY_ID
from .mapper import REVIEW, STRONG, Mapping

PROMPT = """You are a GRC analyst. Decide which candidate NIST 800-53 controls a policy statement
actually supports. Be strict: only mark a control as supported if the statement
requires the activity the control describes.

Policy statement:
{statement}

Candidates:
{candidates}

Reply with JSON only: [{{"control": "AC-2", "supported": true, "score": 0.0-1.0, "reason": "short"}}]"""


class AnthropicReviewer:
    def __init__(self, model: str = None, client=None):
        if client is None:
            import anthropic  # imported lazily so the core has no dependencies
            client = anthropic.Anthropic()
        self.client = client
        self.model = model or os.environ.get("CONTROLMAPPER_MODEL", "claude-sonnet-5-5")

    def review(self, statement, candidates: list) -> list:
        listing = "\n".join(
            f"- {m.control_id} {BY_ID[m.control_id].title}: {BY_ID[m.control_id].description}"
            for m in candidates
        )
        try:
            msg = self.client.messages.create(
                model=self.model,
                max_tokens=600,
                messages=[{"role": "user",
                           "content": PROMPT.format(statement=statement.text, candidates=listing)}],
            )
            verdicts = {v["control"]: v for v in json.loads(msg.content[0].text)}
        except Exception:
            return candidates  # fall back to baseline

        out = []
        for m in candidates:
            v = verdicts.get(m.control_id)
            if v is None:
                out.append(m)
                continue
            if not v.get("supported", False):
                continue
            score = max(0.0, min(1.0, float(v.get("score", m.score))))
            out.append(Mapping(m.control_id, round(score, 3), m.matched_terms,
                               needs_review=score < STRONG, source="llm"))
        return [m for m in out if m.score >= REVIEW]
