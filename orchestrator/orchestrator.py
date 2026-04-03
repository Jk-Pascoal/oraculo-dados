"""
╔══════════════════════════════════════════════════════════╗
║        ORCHESTRATOR — Oráculo de Dados Pipeline         ║
║                                                          ║
║  Coordinates:                                            ║
║    1. Data Miner       → cleans raw data                ║
║    2. Analyst          → extracts insights              ║
║    3. Critical Thinker → questions validity             ║
║    4. Narrator         → generates the final report     ║
╚══════════════════════════════════════════════════════════╝
"""

import json
import sys
import io
from pathlib import Path
from typing import Union

# ── Make the agents package importable ───────────────────────────────────────
_PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(_PROJECT_ROOT))

from agents import data_miner, analyst, critical_thinker, narrator


# ──────────────────────────────────────────────────────────────────────────────
# SAMPLE DATA  (fallback when no data is provided)
# ──────────────────────────────────────────────────────────────────────────────
SAMPLE_RAW_DATA = [
    {"name": "Alice",  "age": 29, "salary": 72000,  "department": "Engineering", "years": 4},
    {"name": "Bob",    "age": 34, "salary": 85000,  "department": "Marketing",   "years": 7},
    {"name": "Carol",  "age": 29, "salary": 72000,  "department": "Engineering", "years": 4},
    {"name": "David",  "age": 45, "salary": 120000, "department": "Engineering", "years": 15},
    {"name": "Eva",    "age": 31, "salary": 68000,  "department": "HR",          "years": 3},
    {"name": "Frank",  "age": 38, "salary": 95000,  "department": "Marketing",   "years": 9},
    {"name": "Grace",  "age": None,"salary": 77000, "department": "Engineering", "years": 5},
    {"name": "Henry",  "age": 27, "salary": 61000,  "department": "HR",          "years": 1},
    {"name": "Iris",   "age": 52, "salary": 210000, "department": "Engineering", "years": 22},
    {"name": "Jack",   "age": 33, "salary": 88000,  "department": "Marketing",   "years": 8},
    {"name": "Karen",  "age": 41, "salary": 105000, "department": "Engineering", "years": 12},
    {"name": "Leo",    "age": 28, "salary": 64000,  "department": "HR",          "years": 2},
]


def load_data(source: Union[list, str, None] = None) -> list[dict]:
    """
    Load raw data from:
      - A list[dict]  → use directly (from Streamlit upload or API)
      - A str path    → load from JSON file
      - None          → fall back to built-in sample data
    """
    if isinstance(source, list):
        return source
    if isinstance(source, str) and Path(source).exists():
        with open(source, "r", encoding="utf-8") as f:
            return json.load(f)
    return SAMPLE_RAW_DATA


def validate_agent_output(output: dict, agent_name: str) -> None:
    """Raise if an agent returned a non-success payload."""
    if not isinstance(output, dict):
        raise TypeError(f"[ORCHESTRATOR] {agent_name} returned non-dict output.")
    status = output.get("metadata", {}).get("status")
    if status != "success":
        raise RuntimeError(
            f"[ORCHESTRATOR] {agent_name} reported status='{status}'. Pipeline halted."
        )


def save_report(report_md: str, output_dir: Path | None = None) -> None:
    """Persist the Markdown report and JSON payload to disk."""
    out = output_dir or (_PROJECT_ROOT / "reports")
    out.mkdir(parents=True, exist_ok=True)
    (out / "final_report.md").write_text(report_md, encoding="utf-8")


def run_pipeline(
    data: Union[list, str, None] = None,
    *,
    save_to_disk: bool = True,
    capture_logs: bool = False,
) -> dict:
    """
    Execute the full multi-agent pipeline.

    Args:
        data:         Raw data as list[dict], a JSON file path, or None (uses sample data).
        save_to_disk: If True, write final_report.md and pipeline_output.json.
        capture_logs: If True, capture agent stdout into the returned dict.

    Returns:
        {
            "pipeline_status": str,
            "data_miner":       dict,
            "analyst":          dict,
            "critical_thinker": dict,
            "narrator":         dict,
            "logs":             str   (only when capture_logs=True)
        }
    """
    log_buf = io.StringIO() if capture_logs else None

    def _log(msg: str):
        print(msg)
        if log_buf:
            log_buf.write(msg + "\n")

    _log("=" * 60)
    _log("  🔮 ORÁCULO DE DADOS — MULTI-AGENT PIPELINE")
    _log("=" * 60)

    # ── Step 0: Load Raw Data ─────────────────────────────────────────────────
    raw_data = load_data(data)
    _log(f"\n[ORCHESTRATOR] Loaded {len(raw_data)} raw record(s).")

    # ── Step 1: DATA MINER ────────────────────────────────────────────────────
    _log("\n[ORCHESTRATOR] → AGENT 1: Data Miner")
    miner_output = data_miner.run(raw_data)
    validate_agent_output(miner_output, "Data Miner")
    _log(f"[ORCHESTRATOR] ✔ Data Miner — clean rows: {miner_output['quality_report']['clean_rows']}")

    # ── Step 2: ANALYST ───────────────────────────────────────────────────────
    _log("[ORCHESTRATOR] → AGENT 2: Analyst")
    analyst_output = analyst.run(miner_output)
    validate_agent_output(analyst_output, "Analyst")
    n_findings = len(analyst_output["insights"]["key_findings"])
    _log(f"[ORCHESTRATOR] ✔ Analyst — findings: {n_findings}")

    # ── Step 3: CRITICAL THINKER ──────────────────────────────────────────────
    _log("[ORCHESTRATOR] → AGENT 3: Critical Thinker")
    critic_output = critical_thinker.run(analyst_output, miner_output)
    validate_agent_output(critic_output, "Critical Thinker")
    n_flaws = len(critic_output["critique"]["flaws"])
    conf = critic_output["critique"]["overall_confidence"]
    _log(f"[ORCHESTRATOR] ✔ Critical Thinker — flaws: {n_flaws} | confidence: {conf}")

    # ── Step 4: NARRATOR ──────────────────────────────────────────────────────
    _log("[ORCHESTRATOR] → AGENT 4: Narrator")
    narrator_output = narrator.run(analyst_output, miner_output, critic_output)
    validate_agent_output(narrator_output, "Narrator")
    _log("[ORCHESTRATOR] ✔ Narrator — report ready.")

    # ── Persist ───────────────────────────────────────────────────────────────
    if save_to_disk:
        save_report(narrator_output["report_markdown"])

    combined = {
        "pipeline_status":  "success",
        "data_miner":       miner_output,
        "analyst":          analyst_output,
        "critical_thinker": critic_output,
        "narrator":         narrator_output,
    }
    if capture_logs:
        combined["logs"] = log_buf.getvalue()

    _log("\n" + "=" * 60)
    _log("  ✅ PIPELINE COMPLETE")
    _log("=" * 60)
    return combined


# ──────────────────────────────────────────────────────────────────────────────
# CLI entry point
# ──────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys as _sys
    src = _sys.argv[1] if len(_sys.argv) > 1 else None
    result = run_pipeline(src)
    print("\n" + "─" * 60)
    print(result["narrator"]["report_markdown"])
