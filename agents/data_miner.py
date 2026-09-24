"""
╔══════════════════════════════════════════╗
║          AGENT 1 — DATA MINER           ║
╚══════════════════════════════════════════╝
Responsibilities:
  - Receive raw data
  - Validate & clean
  - Normalize structure
  - Output clean dataset + quality report
"""

import json
import pandas as pd
from datetime import datetime
from typing import Any


def run(raw_data: list[dict]) -> dict:
    """
    Entry point for the Data Miner agent.

    Args:
        raw_data: List of raw records (dicts).

    Returns:
        {
            "clean_data": list[dict],
            "quality_report": dict,
            "metadata": dict
        }
    """
    print("\n[DATA MINER] ▶ Starting data mining phase...")

    # ── 1. Load into DataFrame ────────────────────────────────────────────────
    df = pd.DataFrame(raw_data)
    original_shape = df.shape
    print(f"[DATA MINER] Loaded {original_shape[0]} rows × {original_shape[1]} columns.")

    # ── 2. Quality checks ─────────────────────────────────────────────────────
    missing = df.isnull().sum().to_dict()
    duplicates = int(df.duplicated().sum())

    # ── 3. Cleaning steps ─────────────────────────────────────────────────────
    df.drop_duplicates(inplace=True)

    # Only fill N/A for non-numeric (object) columns; keep numeric NaN
    str_cols = df.select_dtypes(include=["object", "string"]).columns
    for col in str_cols:
        df[col] = df[col].fillna("N/A").astype(str).str.strip()

    clean_shape = df.shape
    print(f"[DATA MINER] Clean dataset: {clean_shape[0]} rows × {clean_shape[1]} columns.")

    # ── 4. Quality Report ─────────────────────────────────────────────────────
    quality_report = {
        "original_rows": original_shape[0],
        "original_columns": original_shape[1],
        "clean_rows": clean_shape[0],
        "clean_columns": clean_shape[1],
        "duplicates_removed": duplicates,
        "missing_values_per_column": missing,
        "columns": list(df.columns),
        "dtypes": df.dtypes.astype(str).to_dict(),
    }

    # ── 5. Output ─────────────────────────────────────────────────────────────
    output = {
        "clean_data": df.to_dict(orient="records"),
        "quality_report": quality_report,
        "metadata": {
            "agent": "Data Miner",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "status": "success",
        },
    }

    print("[DATA MINER] ✔ Done.\n")
    return output
