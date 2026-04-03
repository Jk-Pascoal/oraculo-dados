"""
╔══════════════════════════════════════════════════════════╗
║        ORCHESTRATOR — Oráculo de Dados Pipeline         ║
║                                                          ║
║  Coordinates:                                            ║
║    1. Data Miner      → cleans raw data                  ║
║    2. Analyst         → extracts insights                ║
║    3. Critical Thinker → questions validity, detects bias ║
║    4. Narrator        → generates the final report       ║
╚══════════════════════════════════════════════════════════╝
"""

import json
import sys
import os
from pathlib import Path

# Add agents directory to path
sys.path.insert(0, str(Path(__file__).parent / "agents"))

import data_miner
import analyst
import critical_thinker
import narrator


# ──────────────────────────────────────────────────────────────────────────────
# SAMPLE DATA  (replace with your own data source)
# ──────────────────────────────────────────────────────────────────────────────
SAMPLE_RAW_DATA = [
    {"name": "Alice",   "age": 29, "salary": 72000, "department": "Engineering", "years": 4},
    {"name": "Bob",     "age": 34, "salary": 85000, "department": "Marketing",   "years": 7},
    {"name": "Carol",   "age": 29, "salary": 72000, "department": "Engineering", "years": 4},  # duplicate
    {"name": "David",   "age": 45, "salary": 120000,"department": "Engineering", "years": 15},
    {"name": "Eva",     "age": 31, "salary": 68000, "department": "HR",          "years": 3},
    {"name": "Frank",   "age": 38, "salary": 95000, "department": "Marketing",   "years": 9},
    {"name": "Grace",   "age": None,"salary": 77000,"department": "Engineering", "years": 5},
    {"name": "Henry",   "age": 27, "salary": 61000, "department": "HR",          "years": 1},
    {"name": "Iris",    "age": 52, "salary": 210000,"department": "Engineering", "years": 22}, # outlier salary
    {"name": "Jack",    "age": 33, "salary": 88000, "department": "Marketing",   "years": 8},
    {"name": "Karen",   "age": 41, "salary": 105000,"department": "Engineering", "years": 12},
    {"name": "Leo",     "age": 28, "salary": 64000, "department": "HR",          "years": 2},
]


def load_data(source: str | None = None) -> list[dict]:
    """
    Load raw data from a JSON file or fall back to sample data.

    Args:
        source: Path to a .json file (list of records) or None for sample data.
    """
    if source and Path(source).exists():
        with open(source, "r", encoding="utf-8") as f:
            data = json.load(f)
        print(f"[ORCHESTRATOR] Loaded {len(data)} records from '{source}'.")
        return data
    else:
        print("[ORCHESTRATOR] No external data source provided. Using built-in sample data.")
        return SAMPLE_RAW_DATA


def validate_agent_output(output: dict, agent_name: str) -> None:
    """Raise an error if the agent output is invalid or failed."""
    if not isinstance(output, dict):
        raise TypeError(f"[ORCHESTRATOR] {agent_name} returned non-dict output.")
    status = output.get("metadata", {}).get("status")
    if status != "success":
        raise RuntimeError(
            f"[ORCHESTRATOR] {agent_name} reported status='{status}'. Pipeline halted."
        )


def save_report(report_md: str, output_path: str = "reports/final_report.md") -> None:
    """Save the Markdown report to disk."""
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report_md)
    print(f"[ORCHESTRATOR] Report saved → {output_path}")


def run_pipeline(data_source: str | None = None) -> dict:
    """
    Execute the full multi-agent pipeline.

    Args:
        data_source: Optional path to a JSON file with raw data.

    Returns:
        Final combined output dict.
    """
    print("=" * 60)
    print("  🔮 ORÁCULO DE DADOS — MULTI-AGENT PIPELINE")
    print("=" * 60)

    # ── Step 0: Load Raw Data ─────────────────────────────────────────────────
    raw_data = load_data(data_source)

    # ── Step 1: DATA MINER ────────────────────────────────────────────────────
    print("\n[ORCHESTRATOR] → Dispatching to AGENT 1: Data Miner")
    miner_output = data_miner.run(raw_data)
    validate_agent_output(miner_output, "Data Miner")
    print(f"[ORCHESTRATOR] ✔ Data Miner complete. "
          f"Clean records: {miner_output['quality_report']['clean_rows']}")

    # ── Step 2: ANALYST ───────────────────────────────────────────────────────
    print("[ORCHESTRATOR] → Dispatching to AGENT 2: Analyst")
    analyst_output = analyst.run(miner_output)
    validate_agent_output(analyst_output, "Analyst")
    findings_count = len(analyst_output["insights"]["key_findings"])
    print(f"[ORCHESTRATOR] ✔ Analyst complete. Key findings: {findings_count}")

    # ── Step 3: CRITICAL THINKER ──────────────────────────────────────────────
    print("[ORCHESTRATOR] → Dispatching to AGENT 3: Critical Thinker")
    critic_output = critical_thinker.run(analyst_output, miner_output)
    validate_agent_output(critic_output, "Critical Thinker")
    flaw_count = len(critic_output["critique"]["flaws"])
    overall_conf = critic_output["critique"]["overall_confidence"]
    print(f"[ORCHESTRATOR] ✔ Critical Thinker complete. Flaws: {flaw_count} | Confidence: {overall_conf}")

    # ── Step 4: NARRATOR ──────────────────────────────────────────────────────
    print("[ORCHESTRATOR] → Dispatching to AGENT 4: Narrator")
    narrator_output = narrator.run(analyst_output, miner_output, critic_output)
    validate_agent_output(narrator_output, "Narrator")
    print("[ORCHESTRATOR] ✔ Narrator complete. Report generated.")

    # ── Step 4: Save Report ───────────────────────────────────────────────────
    save_report(narrator_output["report_markdown"])

    # ── Step 5: Combined Output ───────────────────────────────────────────────
    combined = {
        "pipeline_status": "success",
        "data_miner":      miner_output,
        "analyst":         analyst_output,
        "critical_thinker": critic_output,
        "narrator":        narrator_output,
    }

    # Save full JSON payload
    Path("reports").mkdir(parents=True, exist_ok=True)
    with open("reports/pipeline_output.json", "w", encoding="utf-8") as f:
        json.dump(combined, f, indent=2, default=str)
    print("[ORCHESTRATOR] Full pipeline output saved → reports/pipeline_output.json")

    print("\n" + "=" * 60)
    print("  ✅ PIPELINE COMPLETE — All agents succeeded.")
    print("=" * 60)
    return combined


# ──────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Optional: pass a JSON file as command-line argument
    source = sys.argv[1] if len(sys.argv) > 1 else None
    result = run_pipeline(source)

    # Print the final Markdown report to the terminal
    print("\n" + "─" * 60)
    print(result["narrator"]["report_markdown"])
