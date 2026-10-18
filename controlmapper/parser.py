"""Split a policy document into individual statements."""

import re
from dataclasses import dataclass

OBLIGATION = re.compile(
    r"\b(shall|must|will|should|required|requires?|responsible for|are to|is to|prohibited|may not)\b",
    re.IGNORECASE,
)
HEADING = re.compile(r"^(#{1,6}\s+|\d+(\.\d+)*\.?\s+[A-Z][^.!?]{0,80}$)")
BULLET = re.compile(r"^\s*([-*•]|\d+[.)]|[a-z][.)])\s+")
SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+(?=[A-Z])")


@dataclass(frozen=True)
class Statement:
    id: str
    section: str
    text: str


def _clean(line: str) -> str:
    line = BULLET.sub("", line.strip())
    return re.sub(r"\s+", " ", line)


def parse_policy(text: str, all_sentences: bool = False, min_words: int = 5) -> list:
    """Return policy statements.

    By default only sentences containing an obligation word
    (shall/must/will/should/required...) are kept, since those are the
    ones a control can actually be mapped to.
    """
    statements = []
    section = "Preamble"
    paragraph = []

    def flush():
        if not paragraph:
            return
        joined = " ".join(paragraph)
        paragraph.clear()
        for sentence in SENTENCE_SPLIT.split(joined):
            sentence = sentence.strip()
            if len(sentence.split()) < min_words:
                continue
            if all_sentences or OBLIGATION.search(sentence):
                statements.append(
                    Statement(f"S{len(statements) + 1:03d}", section, sentence)
                )

    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            flush()
            continue
        if HEADING.match(line) and not OBLIGATION.search(line):
            flush()
            section = re.sub(r"^#{1,6}\s+", "", line).strip()
            continue
        if BULLET.match(line):
            flush()
            paragraph.append(_clean(line))
            flush()
            continue
        paragraph.append(_clean(line))
    flush()
    return statements
