"""Command line interface."""

import argparse
import json
import sys
from pathlib import Path

from .gaps import analyze
from .mapper import ControlMapper, apply_decisions
from .parser import parse_policy
from .report import to_json, to_markdown


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="controlmapper",
        description="Map a security policy to NIST 800-53 controls and find gaps.",
    )
    p.add_argument("policy", help="Path to a policy file (.txt or .md)")
    p.add_argument("-o", "--out", default="reports", help="Output folder (default: reports)")
    p.add_argument("--baseline", help="Text file with one control ID per line to scope the gap analysis")
    p.add_argument("--decisions", help="JSON file of analyst accept/reject decisions")
    p.add_argument("--all-sentences", action="store_true", help="Map every sentence, not only obligations")
    p.add_argument("--top-k", type=int, default=3, help="Max controls per statement (default: 3)")
    p.add_argument("--llm", action="store_true", help="Add an LLM second opinion (needs ANTHROPIC_API_KEY)")
    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    path = Path(args.policy)
    if not path.is_file():
        print(f"error: policy file not found: {path}", file=sys.stderr)
        return 2

    statements = parse_policy(path.read_text(encoding="utf-8"), all_sentences=args.all_sentences)
    if not statements:
        print("error: no policy statements found. Try --all-sentences.", file=sys.stderr)
        return 2

    reviewer = None
    if args.llm:
        from .llm_reviewer import AnthropicReviewer
        reviewer = AnthropicReviewer()

    results = ControlMapper(top_k=args.top_k).map_all(statements, reviewer)
    if args.decisions:
        results = apply_decisions(results, json.loads(Path(args.decisions).read_text()))

    baseline = None
    if args.baseline:
        baseline = [l.strip() for l in Path(args.baseline).read_text().splitlines()
                    if l.strip() and not l.startswith("#")]
    try:
        coverage = analyze(results, baseline)
    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    stem = path.stem
    (out / f"{stem}_report.md").write_text(to_markdown(results, coverage, path.name), encoding="utf-8")
    (out / f"{stem}_report.json").write_text(to_json(results, coverage, path.name), encoding="utf-8")
    print(f"{len(statements)} statements | coverage {coverage.percent}% | "
          f"{len(coverage.gaps)} gaps | wrote {out}/{stem}_report.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
