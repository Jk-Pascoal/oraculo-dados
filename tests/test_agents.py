"""Unit tests for the four pipeline agents."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from agents import data_miner, analyst, critical_thinker, narrator

# ── Shared fixtures ──────────────────────────────────────────────────────────

SAMPLE = [
    {"name": "Alice",  "age": 29, "salary": 72000,  "dept": "Eng", "years": 4},
    {"name": "Bob",    "age": 34, "salary": 85000,  "dept": "Mkt", "years": 7},
    {"name": "Alice",  "age": 29, "salary": 72000,  "dept": "Eng", "years": 4},  # exact duplicate
    {"name": "David",  "age": 45, "salary": 120000, "dept": "Eng", "years": 15},
    {"name": "Eva",    "age": 31, "salary": 68000,  "dept": "HR",  "years": 3},
    {"name": "Iris",   "age": 52, "salary": 210000, "dept": "Eng", "years": 22},
]


@pytest.fixture(scope="module")
def miner_out():
    return data_miner.run(SAMPLE)


@pytest.fixture(scope="module")
def analyst_out(miner_out):
    return analyst.run(miner_out)


@pytest.fixture(scope="module")
def critic_out(analyst_out, miner_out):
    return critical_thinker.run(analyst_out, miner_out)


@pytest.fixture(scope="module")
def narrator_out(analyst_out, miner_out, critic_out):
    return narrator.run(analyst_out, miner_out, critic_out)


# ── Data Miner tests ─────────────────────────────────────────────────────────

class TestDataMiner:
    def test_returns_dict_with_required_keys(self, miner_out):
        assert {"clean_data", "quality_report", "metadata"} <= miner_out.keys()

    def test_status_success(self, miner_out):
        assert miner_out["metadata"]["status"] == "success"

    def test_duplicate_removed(self, miner_out):
        q = miner_out["quality_report"]
        assert q["duplicates_removed"] == 1
        assert q["clean_rows"] == q["original_rows"] - 1

    def test_clean_data_is_list_of_dicts(self, miner_out):
        data = miner_out["clean_data"]
        assert isinstance(data, list)
        assert all(isinstance(r, dict) for r in data)

    def test_quality_report_columns(self, miner_out):
        q = miner_out["quality_report"]
        assert "original_rows" in q
        assert "columns" in q
        assert len(q["columns"]) > 0

    def test_empty_input_handled(self):
        result = data_miner.run([])
        assert result["metadata"]["status"] == "success"
        assert result["quality_report"]["clean_rows"] == 0


# ── Analyst tests ────────────────────────────────────────────────────────────

class TestAnalyst:
    def test_returns_dict_with_required_keys(self, analyst_out):
        assert {"insights", "metadata"} <= analyst_out.keys()

    def test_status_success(self, analyst_out):
        assert analyst_out["metadata"]["status"] == "success"

    def test_numeric_stats_present(self, analyst_out):
        stats = analyst_out["insights"]["numeric_stats"]
        assert isinstance(stats, dict)
        assert len(stats) > 0

    def test_numeric_stats_has_expected_fields(self, analyst_out):
        stats = analyst_out["insights"]["numeric_stats"]
        for col_stats in stats.values():
            assert {"mean", "median", "std", "min", "max"} <= col_stats.keys()

    def test_key_findings_non_empty(self, analyst_out):
        findings = analyst_out["insights"]["key_findings"]
        assert isinstance(findings, list)
        assert len(findings) > 0

    def test_anomalies_dict(self, analyst_out):
        anomalies = analyst_out["insights"]["anomalies"]
        assert isinstance(anomalies, dict)

    def test_raises_on_failed_miner_input(self):
        bad_input = {"metadata": {"status": "error"}, "clean_data": []}
        with pytest.raises(ValueError):
            analyst.run(bad_input)


# ── Critical Thinker tests ───────────────────────────────────────────────────

class TestCriticalThinker:
    def test_returns_dict_with_required_keys(self, critic_out):
        assert {"critique", "metadata"} <= critic_out.keys()

    def test_status_success(self, critic_out):
        assert critic_out["metadata"]["status"] == "success"

    def test_critique_structure(self, critic_out):
        c = critic_out["critique"]
        assert "flaws" in c
        assert "overall_confidence" in c
        assert "verdict" in c

    def test_confidence_valid_values(self, critic_out):
        level = critic_out["critique"]["overall_confidence"]
        assert level in {"LOW", "MEDIUM", "HIGH"}

    def test_flaws_are_list_of_dicts(self, critic_out):
        flaws = critic_out["critique"]["flaws"]
        assert isinstance(flaws, list)
        for flaw in flaws:
            assert {"type", "description", "severity"} <= flaw.keys()


# ── Narrator tests ───────────────────────────────────────────────────────────

class TestNarrator:
    def test_returns_dict_with_required_keys(self, narrator_out):
        assert {"report_markdown", "metadata"} <= narrator_out.keys()

    def test_status_success(self, narrator_out):
        assert narrator_out["metadata"]["status"] == "success"

    def test_report_is_non_empty_string(self, narrator_out):
        report = narrator_out["report_markdown"]
        assert isinstance(report, str)
        assert len(report) > 100

    def test_report_has_markdown_headers(self, narrator_out):
        report = narrator_out["report_markdown"]
        assert "#" in report
