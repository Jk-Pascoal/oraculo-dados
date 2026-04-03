"""
╔══════════════════════════════════════════╗
║          AGENT 2 — ANALYST              ║
╚══════════════════════════════════════════╝
Responsibilities:
  - Receive clean data from Data Miner
  - Compute descriptive statistics
  - Detect patterns, correlations, anomalies
  - Output structured insights
"""

import json
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Any


def run(miner_output: dict) -> dict:
    """
    Entry point for the Analyst agent.

    Args:
        miner_output: Output dict from data_miner.run().

    Returns:
        {
            "insights": dict,
            "metadata": dict
        }
    """
    print("[ANALYST] ▶ Starting analysis phase...")

    # ── Validate input ────────────────────────────────────────────────────────
    if miner_output.get("metadata", {}).get("status") != "success":
        raise ValueError("[ANALYST] ✖ Received failed output from Data Miner. Halting.")

    df = pd.DataFrame(miner_output["clean_data"])
    quality = miner_output["quality_report"]

    # Re-coerce columns that should be numeric (handles 'N/A' string in otherwise numeric cols)
    for col in df.columns:
        converted = pd.to_numeric(df[col], errors='coerce')
        # Only adopt the conversion if most values are numeric (< 30% lost)
        if converted.notna().sum() >= 0.7 * len(df):
            df[col] = converted
    print(f"[ANALYST] Working on {len(df)} clean records across {len(df.columns)} columns.")

    # ── Numeric analysis ──────────────────────────────────────────────────────
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    numeric_stats = {}
    for col in numeric_cols:
        series = df[col]
        numeric_stats[col] = {
            "mean":   round(float(series.mean()), 4),
            "median": round(float(series.median()), 4),
            "std":    round(float(series.std()), 4),
            "min":    round(float(series.min()), 4),
            "max":    round(float(series.max()), 4),
            "q25":    round(float(series.quantile(0.25)), 4),
            "q75":    round(float(series.quantile(0.75)), 4),
        }

    # ── Categorical analysis ──────────────────────────────────────────────────
    cat_cols = df.select_dtypes(include="object").columns.tolist()
    categorical_stats = {}
    for col in cat_cols:
        value_counts = df[col].value_counts().head(10).to_dict()
        categorical_stats[col] = {
            "unique_values": int(df[col].nunique()),
            "top_10": value_counts,
            "mode": str(df[col].mode()[0]) if not df[col].mode().empty else "N/A",
        }

    # ── Correlation matrix (numeric only) ────────────────────────────────────
    correlation = {}
    if len(numeric_cols) > 1:
        corr_matrix = df[numeric_cols].corr().round(4)
        correlation = corr_matrix.to_dict()

    # ── Anomaly detection (simple IQR method) ────────────────────────────────
    anomalies = {}
    for col in numeric_cols:
        q1 = df[col].quantile(0.25)
        q3 = df[col].quantile(0.75)
        iqr = q3 - q1
        lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
        outliers = df[(df[col] < lower) | (df[col] > upper)][col].tolist()
        anomalies[col] = {
            "outlier_count": len(outliers),
            "outlier_values": outliers[:10],  # cap at 10
        }

    # ── Key findings summary ──────────────────────────────────────────────────
    key_findings = []
    for col, stats in numeric_stats.items():
        if stats["std"] > 0:
            cv = round(stats["std"] / abs(stats["mean"]) * 100, 2) if stats["mean"] != 0 else 0
            key_findings.append(f"'{col}' has a coefficient of variation of {cv}%.")
        outlier_n = anomalies.get(col, {}).get("outlier_count", 0)
        if outlier_n > 0:
            key_findings.append(f"'{col}' contains {outlier_n} potential outlier(s).")

    for col, stats in categorical_stats.items():
        key_findings.append(
            f"'{col}' has {stats['unique_values']} unique values; most common: '{stats['mode']}'."
        )

    # ── Output ────────────────────────────────────────────────────────────────
    output = {
        "insights": {
            "overview": {
                "total_records": len(df),
                "numeric_columns": numeric_cols,
                "categorical_columns": cat_cols,
            },
            "numeric_stats": numeric_stats,
            "categorical_stats": categorical_stats,
            "correlation_matrix": correlation,
            "anomalies": anomalies,
            "key_findings": key_findings,
        },
        "metadata": {
            "agent": "Analyst",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "status": "success",
        },
    }

    print(f"[ANALYST] ✔ Generated {len(key_findings)} key findings.\n")
    return output
