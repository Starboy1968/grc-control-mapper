import json
from pathlib import Path

import pytest

from controlmapper.catalog import BY_ID, CATALOG, FAMILIES
from controlmapper.cli import main
from controlmapper.gaps import analyze, priority
from controlmapper.llm_reviewer import AnthropicReviewer
from controlmapper.mapper import (
    STRONG, ControlMapper, Mapping, apply_decisions, tokenize,
)
from controlmapper.parser import Statement, parse_policy
from controlmapper.report import to_json, to_markdown

SAMPLE = Path(__file__).parent.parent / "samples" / "acme_infosec_policy.md"


@pytest.fixture(scope="module")
def mapper():
    return ControlMapper()


# ---------- catalog ----------

def test_catalog_ids_unique_and_well_formed():
    ids = [c.id for c in CATALOG]
    assert len(ids) == len(set(ids))
    for c in CATALOG:
        assert c.family in FAMILIES
        assert c.id.startswith(c.family + "-")
        assert c.csf and c.description and c.keywords


# ---------- parser ----------

def test_parser_keeps_obligations_and_skips_filler():
    text = "# Policy\n\nThis document describes our approach to security.\n\nUsers must use strong passwords at all times."
    out = parse_policy(text)
    assert len(out) == 1
    assert "strong passwords" in out[0].text
    assert out[0].section == "Policy"


def test_parser_tracks_sections_and_ids():
    text = "## A\n\nStaff shall lock their screens when away.\n\n## B\n\nBackups must be tested every quarter."
    out = parse_policy(text)
    assert [s.id for s in out] == ["S001", "S002"]
    assert [s.section for s in out] == ["A", "B"]


def test_parser_splits_bullets_and_sentences():
    text = "- Laptops must be encrypted at all times.\n- Visitors shall sign in at reception desk.\nAccess is logged. Logs must be reviewed weekly by security."
    out = parse_policy(text)
    assert len(out) == 3


def test_parser_all_sentences_mode():
    text = "Our company values security highly across everything."
    assert parse_policy(text) == []
    assert len(parse_policy(text, all_sentences=True)) == 1


def test_parser_empty_input():
    assert parse_policy("") == []


# ---------- mapper ----------

def test_tokenize_drops_stopwords_and_stems():
    toks = tokenize("The accounts are being reviewed")
    assert "the" not in toks and "are" not in toks
    assert "account" in toks and "review" in toks


@pytest.mark.parametrize("text,expected", [
    ("All employees must use multi-factor authentication to access systems.", "IA-2"),
    ("Backups must be taken daily and stored offsite.", "CP-9"),
    ("Customer data must be encrypted in transit using TLS.", "SC-8"),
    ("Data at rest shall be protected with disk encryption.", "SC-28"),
    ("Vulnerability scans shall be run monthly.", "RA-5"),
    ("The company must maintain an incident response plan.", "IR-8"),
    ("Security patches must be applied within 14 days.", "SI-2"),
    ("Background checks are required before hire.", "PS-3"),
])
def test_known_statements_map_to_expected_control_first(mapper, text, expected):
    result = mapper.map_statement(Statement("S001", "t", text))
    assert result.mappings, "expected at least one mapping"
    assert result.mappings[0].control_id == expected


def test_irrelevant_statement_has_no_strong_mapping(mapper):
    result = mapper.map_statement(
        Statement("S001", "t", "The cafeteria must serve lunch between noon and two."))
    assert all(m.score < STRONG for m in result.mappings)


def test_scores_are_bounded_and_sorted(mapper):
    r = mapper.map_statement(Statement("S001", "t", "Remote access must use the VPN with MFA."))
    scores = [m.score for m in r.mappings]
    assert scores == sorted(scores, reverse=True)
    assert all(0 <= s <= 1 for s in scores)
    assert len(r.mappings) <= mapper.top_k


def test_low_scores_are_flagged_for_review(mapper):
    r = mapper.map_statement(Statement("S001", "t", "Accounts must be approved by a manager."))
    for m in r.mappings:
        assert m.needs_review == (m.score < STRONG)


def test_mapping_is_deterministic(mapper):
    s = Statement("S001", "t", "Logs must be retained for one year.")
    a, b = mapper.map_statement(s), mapper.map_statement(s)
    assert [(m.control_id, m.score) for m in a.mappings] == [(m.control_id, m.score) for m in b.mappings]


def test_matched_terms_explain_mapping(mapper):
    r = mapper.map_statement(Statement("S001", "t", "Employees must use multi-factor authentication."))
    assert r.mappings[0].matched_terms


# ---------- decisions ----------

def test_apply_decisions_accept_and_reject(mapper):
    s = Statement("S001", "t", "Passwords must be at least 14 characters.")
    results = [mapper.map_statement(s)]
    low = next((m for m in results[0].mappings if m.needs_review), None)
    assert low is not None
    decisions = {"S001": {low.control_id: "accept"}}
    apply_decisions(results, decisions)
    kept = next(m for m in results[0].mappings if m.control_id == low.control_id)
    assert kept.needs_review is False and kept.source == "analyst"

    apply_decisions(results, {"S001": {low.control_id: "reject"}})
    assert all(m.control_id != low.control_id for m in results[0].mappings)


# ---------- gaps ----------

def test_gap_analysis_on_sample(mapper):
    results = mapper.map_all(parse_policy(SAMPLE.read_text()))
    cov = analyze(results)
    assert "IA-2" in cov.covered and "CP-9" in cov.covered
    assert "AU-2" in cov.gaps and "SI-4" in cov.gaps
    assert set(cov.covered).isdisjoint(cov.gaps)
    assert 0 < cov.percent < 100


def test_low_confidence_counts_as_pending_not_covered(mapper):
    results = [mapper.map_statement(Statement("S001", "t", "Vendors that handle company data must be assessed."))]
    cov = analyze(results, ["SA-9"])
    assert "SA-9" not in cov.covered
    assert "SA-9" in cov.pending or "SA-9" in cov.covered
    assert cov.percent in (0.0, 100.0)


def test_custom_baseline_scopes_gaps(mapper):
    results = mapper.map_all(parse_policy(SAMPLE.read_text()))
    cov = analyze(results, ["IA-2", "AU-2"])
    assert cov.gaps == ["AU-2"]
    assert cov.percent == 50.0


def test_unknown_baseline_control_raises(mapper):
    with pytest.raises(ValueError, match="XX-99"):
        analyze([], ["XX-99"])


def test_priority_levels():
    assert priority("IA-2") == "High"
    assert priority("PE-2") == "Medium"


# ---------- report ----------

def test_markdown_report_has_required_sections(mapper):
    results = mapper.map_all(parse_policy(SAMPLE.read_text()))
    md = to_markdown(results, analyze(results), "sample.md")
    for heading in ["Executive summary", "Coverage by control family", "Gaps",
                    "Mapped statements", "Analyst review queue"]:
        assert heading in md
    assert "AU-2" in md


def test_json_report_roundtrips(mapper):
    results = mapper.map_all(parse_policy(SAMPLE.read_text()))
    data = json.loads(to_json(results, analyze(results), "sample.md"))
    assert data["statements"] and "gaps" in data
    assert data["statements"][0]["id"] == "S001"


# ---------- LLM reviewer (no network: fake client) ----------

class _FakeMessages:
    def __init__(self, text, boom=False):
        self.text, self.boom = text, boom

    def create(self, **kwargs):
        if self.boom:
            raise RuntimeError("network down")
        block = type("B", (), {"text": self.text})()
        return type("M", (), {"content": [block]})()


class _FakeClient:
    def __init__(self, text="", boom=False):
        self.messages = _FakeMessages(text, boom)


def _candidates():
    return [Mapping("AC-2", 0.6), Mapping("AC-7", 0.25, needs_review=True)]


def test_llm_reviewer_filters_unsupported_and_rescores():
    reply = json.dumps([
        {"control": "AC-2", "supported": True, "score": 0.9, "reason": "x"},
        {"control": "AC-7", "supported": False, "score": 0.1, "reason": "y"},
    ])
    rv = AnthropicReviewer(client=_FakeClient(reply))
    out = rv.review(Statement("S001", "t", "Accounts must be approved."), _candidates())
    assert [m.control_id for m in out] == ["AC-2"]
    assert out[0].score == 0.9 and out[0].source == "llm"


def test_llm_reviewer_falls_back_on_error():
    rv = AnthropicReviewer(client=_FakeClient(boom=True))
    cands = _candidates()
    assert rv.review(Statement("S001", "t", "x"), cands) == cands


def test_llm_reviewer_falls_back_on_bad_json():
    rv = AnthropicReviewer(client=_FakeClient("not json"))
    cands = _candidates()
    assert rv.review(Statement("S001", "t", "x"), cands) == cands


def test_llm_cannot_add_controls_outside_candidates():
    reply = json.dumps([{"control": "SI-4", "supported": True, "score": 1.0, "reason": "z"}])
    rv = AnthropicReviewer(client=_FakeClient(reply))
    out = rv.review(Statement("S001", "t", "x"), _candidates())
    assert {m.control_id for m in out} <= {"AC-2", "AC-7"}


# ---------- CLI ----------

def test_cli_end_to_end(tmp_path, capsys):
    code = main([str(SAMPLE), "-o", str(tmp_path)])
    assert code == 0
    assert (tmp_path / "acme_infosec_policy_report.md").exists()
    assert (tmp_path / "acme_infosec_policy_report.json").exists()
    assert "coverage" in capsys.readouterr().out


def test_cli_missing_file(tmp_path, capsys):
    assert main([str(tmp_path / "nope.md")]) == 2
    assert "not found" in capsys.readouterr().err


def test_cli_no_statements(tmp_path, capsys):
    f = tmp_path / "empty.md"
    f.write_text("Hello.")
    assert main([str(f), "-o", str(tmp_path)]) == 2


def test_cli_baseline_and_decisions(tmp_path):
    base = tmp_path / "base.txt"
    base.write_text("# starter\nIA-2\nAU-2\n")
    dec = tmp_path / "dec.json"
    dec.write_text(json.dumps({"S001": {"AC-2": "reject"}}))
    assert main([str(SAMPLE), "-o", str(tmp_path), "--baseline", str(base),
                 "--decisions", str(dec)]) == 0
    data = json.loads((tmp_path / "acme_infosec_policy_report.json").read_text())
    assert data["gaps"] == ["AU-2"]


def test_cli_bad_baseline(tmp_path, capsys):
    base = tmp_path / "base.txt"
    base.write_text("ZZ-1\n")
    assert main([str(SAMPLE), "-o", str(tmp_path), "--baseline", str(base)]) == 2
