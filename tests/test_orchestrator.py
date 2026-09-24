"""Integration tests for the orchestrator pipeline."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from orchestrator.orchestrator import run_pipeline, load_data, validate_agent_output


class TestLoadData:
    def test_returns_list_when_given_list(self):
        data = [{"a": 1}]
        assert load_data(data) == data

    def test_returns_sample_when_none(self):
        result = load_data(None)
        assert isinstance(result, list)
        assert len(result) > 0

    def test_returns_sample_for_nonexistent_path(self):
        result = load_data("/nonexistent/path.json")
        assert isinstance(result, list)


class TestValidateAgentOutput:
    def test_passes_on_success(self):
        validate_agent_output({"metadata": {"status": "success"}}, "TestAgent")

    def test_raises_on_wrong_type(self):
        with pytest.raises(TypeError):
            validate_agent_output("not a dict", "TestAgent")

    def test_raises_on_non_success_status(self):
        with pytest.raises(RuntimeError):
            validate_agent_output({"metadata": {"status": "error"}}, "TestAgent")


class TestRunPipeline:
    def test_full_pipeline_with_sample_data(self):
        result = run_pipeline(data=None, save_to_disk=False, capture_logs=False)
        assert result["pipeline_status"] == "success"
        assert "data_miner" in result
        assert "analyst" in result
        assert "critical_thinker" in result
        assert "narrator" in result

    def test_pipeline_with_custom_data(self):
        data = [
            {"x": 1, "y": 10, "cat": "A"},
            {"x": 2, "y": 20, "cat": "B"},
            {"x": 3, "y": 30, "cat": "A"},
        ]
        result = run_pipeline(data=data, save_to_disk=False)
        assert result["pipeline_status"] == "success"
        assert result["data_miner"]["quality_report"]["clean_rows"] == 3

    def test_pipeline_captures_logs(self):
        result = run_pipeline(data=None, save_to_disk=False, capture_logs=True)
        assert "logs" in result
        assert "ORÁCULO DE DADOS" in result["logs"]
        assert "Narrator — report ready" in result["logs"]

    def test_narrator_report_is_markdown(self):
        result = run_pipeline(data=None, save_to_disk=False)
        report = result["narrator"]["report_markdown"]
        assert isinstance(report, str)
        assert "#" in report
