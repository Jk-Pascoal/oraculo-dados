"""
╔══════════════════════════════════════════╗
║      AGENT 4 — CRITICAL THINKER        ║
╚══════════════════════════════════════════╝
Responsibilities:
  - Receive Analyst insights
  - Question validity of conclusions
  - Detect sampling bias, confounders, spurious correlations
  - Flag misleading statistics (e.g., mean skewed by outliers)
  - Suggest additional data needed
  - Assign confidence levels to each insight

Output:
  {
    "flaws":               list[dict]   – detected methodological problems
    "alternative_interps": list[dict]   – alternative explanations
    "data_gaps":           list[str]    – what additional data is needed
    "confidence_scores":   dict         – per-finding confidence (0–1)
    "overall_confidence":  str          – LOW / MEDIUM / HIGH
    "verdict":             str          – narrative summary of critique
  }
"""

from datetime import datetime
import math
from typing import Any


# ─────────────────────────────────────────────────────────────────────────────
# Internal helpers
# ─────────────────────────────────────────────────────────────────────────────

def _confidence_label(score: float) -> str:
    if score >= 0.75:
        return "HIGH"
    elif score >= 0.45:
        return "MEDIUM"
    return "LOW"


def _sample_size_penalty(n: int) -> float:
    """
    Returns a penalty factor (0–1) based on sample size.
    < 30  → severe penalty
    30–100 → moderate penalty
    > 100 → minimal penalty
    """
    if n < 10:
        return 0.20
    if n < 30:
        return 0.45
    if n < 100:
        return 0.70
    return 0.95


def _check_sample_size(n: int) -> dict | None:
    """Flag small sample sizes as a methodological flaw."""
    if n < 100:
        severity = "CRITICAL" if n < 30 else "WARNING"
        return {
            "type": "Small Sample Size",
            "severity": severity,
            "description": (
                f"The dataset contains only {n} record(s). Statistical conclusions drawn from "
                f"fewer than {'30' if n < 30 else '100'} observations are highly unreliable. "
                f"Effect sizes, correlations and outlier labels may not generalize."
            ),
            "affected_insights": ["all"],
        }
    return None


def _check_correlation_causation(correlation_matrix: dict, n: int) -> list[dict]:
    """
    Flag strong correlations that are likely spurious or confounded,
    especially with small samples.
    """
    flaws = []
    cols = list(correlation_matrix.keys())
    for i, c1 in enumerate(cols):
        for c2 in cols[i + 1:]:
            r = correlation_matrix[c1].get(c2)
            if r is None:
                continue
            r = float(r)
            if abs(r) > 0.85 and n < 50:
                flaws.append({
                    "type": "Spurious Correlation Risk",
                    "severity": "WARNING",
                    "description": (
                        f"`{c1}` ↔ `{c2}` shows r={round(r, 4)}, but with only {n} observations "
                        f"a correlation this strong can easily arise by chance "
                        f"(sampling artifact). This does NOT imply causation."
                    ),
                    "affected_insights": [f"correlation:{c1}:{c2}"],
                })
            elif abs(r) > 0.70:
                flaws.append({
                    "type": "Correlation ≠ Causation",
                    "severity": "INFO",
                    "description": (
                        f"`{c1}` ↔ `{c2}` (r={round(r, 4)}) — a strong correlation exists, "
                        f"but unmeasured confounders (e.g., industry, role level, tenure policy) "
                        f"may fully explain this relationship."
                    ),
                    "affected_insights": [f"correlation:{c1}:{c2}"],
                })
    return flaws


def _check_outlier_impact(numeric_stats: dict, anomalies: dict) -> list[dict]:
    """
    Detect when outliers drastically skew the mean vs. median,
    making the mean a misleading summary.
    """
    flaws = []
    for col, stats in numeric_stats.items():
        mean = stats.get("mean", 0)
        median = stats.get("median", 0)
        if median == 0:
            continue
        skew_ratio = abs(mean - median) / abs(median)
        outlier_count = anomalies.get(col, {}).get("outlier_count", 0)
        if skew_ratio > 0.15 and outlier_count > 0:
            flaws.append({
                "type": "Mean Skewed by Outliers",
                "severity": "WARNING",
                "description": (
                    f"`{col}`: mean={round(mean, 2)} vs. median={round(median, 2)} "
                    f"({round(skew_ratio * 100, 1)}% divergence). "
                    f"The mean is inflated by {outlier_count} outlier(s). "
                    f"The median is a more robust central tendency measure here."
                ),
                "affected_insights": [f"numeric_stats:{col}"],
            })
    return flaws


def _check_cv_interpretation(numeric_stats: dict) -> list[dict]:
    """
    High CV (>70%) is often misread as 'the data is diverse' when it may
    signal heterogeneous subpopulations that should be analyzed separately.
    """
    flaws = []
    for col, stats in numeric_stats.items():
        mean = stats.get("mean", 0)
        std = stats.get("std", 0)
        if mean == 0:
            continue
        cv = abs(std / mean) * 100
        if cv > 70:
            flaws.append({
                "type": "High Variance — Possible Subgroups",
                "severity": "INFO",
                "description": (
                    f"`{col}` has CV={round(cv, 1)}%. This extreme variability suggests "
                    f"the data may contain distinct subpopulations (e.g., junior vs. senior "
                    f"employees). Aggregate statistics mask these groups — "
                    f"a segmented analysis is strongly recommended."
                ),
                "affected_insights": [f"numeric_stats:{col}"],
            })
    return flaws


def _check_categorical_dominance(categorical_stats: dict, n: int) -> list[dict]:
    """
    Warn when one category dominates (>60%) — insights about minority
    categories are unreliable.
    """
    flaws = []
    for col, stats in categorical_stats.items():
        top_10 = stats.get("top_10", {})
        if not top_10:
            continue
        top_count = list(top_10.values())[0]
        dominance = top_count / n if n > 0 else 0
        if dominance > 0.60:
            top_val = list(top_10.keys())[0]
            flaws.append({
                "type": "Category Dominance Bias",
                "severity": "INFO",
                "description": (
                    f"`{col}`: '{top_val}' accounts for {round(dominance * 100, 1)}% of records. "
                    f"Statistics for minority categories (< 10 samples each) are unreliable. "
                    f"Do not generalize findings across all categories equally."
                ),
                "affected_insights": [f"categorical:{col}"],
            })
    return flaws


def _build_alternative_interpretations(
    numeric_stats: dict,
    correlation_matrix: dict,
    anomalies: dict,
    n: int,
) -> list[dict]:
    """Generate alternative explanations for key statistical findings."""
    alternatives = []

    # Correlation alternatives
    cols = list(correlation_matrix.keys())
    for i, c1 in enumerate(cols):
        for c2 in cols[i + 1:]:
            r = float(correlation_matrix[c1].get(c2, 0))
            if abs(r) > 0.70:
                alternatives.append({
                    "finding": f"Strong correlation between `{c1}` and `{c2}` (r={round(r,4)})",
                    "alternative": (
                        f"A hidden third variable (e.g., job level, education, location) "
                        f"could independently drive both `{c1}` and `{c2}`, "
                        f"making the direct relationship spurious."
                    ),
                    "test_to_resolve": (
                        f"Partial correlation controlling for potential confounders; "
                        f"or multivariate regression with control variables."
                    ),
                })

    # Outlier alternatives
    for col, info in anomalies.items():
        if info.get("outlier_count", 0) > 0:
            vals = info.get("outlier_values", [])
            alternatives.append({
                "finding": f"Outlier(s) detected in `{col}`: {vals[:3]}",
                "alternative": (
                    f"These values may represent a legitimate sub-segment "
                    f"(e.g., executives, long-tenure specialists) rather than data errors. "
                    f"Removing them without domain validation would distort the analysis."
                ),
                "test_to_resolve": (
                    f"Domain expert review; check if outliers cluster in a specific category "
                    f"(e.g., same department or role)."
                ),
            })

    # Small-n alternative
    if n < 50:
        alternatives.append({
            "finding": f"All statistical insights (n={n})",
            "alternative": (
                f"With only {n} records, random sampling error alone could produce "
                f"all observed patterns. A completely different random sample of the "
                f"same size might yield opposite conclusions."
            ),
            "test_to_resolve": (
                "Bootstrap resampling (1000+ iterations) to assess stability of estimates; "
                "collect more data before drawing firm conclusions."
            ),
        })

    return alternatives


def _suggest_data_gaps(
    numeric_cols: list,
    categorical_cols: list,
    n: int,
    correlation_matrix: dict,
) -> list[str]:
    """Identify what data would materially improve the analysis."""
    gaps = []

    if n < 100:
        gaps.append(
            f"**More observations:** Current n={n} is insufficient for robust inference. "
            f"At minimum, collect n≥100 for basic statistical validity; n≥300 for reliable correlations."
        )

    if "department" in categorical_cols and "salary" in numeric_cols:
        gaps.append(
            "**Job level / seniority tier:** Without role level (junior/mid/senior/lead), "
            "salary comparisons across departments are confounded by role mix."
        )

    if "age" in numeric_cols and "salary" in numeric_cols:
        gaps.append(
            "**Education level & field:** Age–salary correlation may be entirely explained "
            "by education credentials, which is not captured in this dataset."
        )

    if "years" in numeric_cols:
        gaps.append(
            "**Performance ratings & promotion history:** Years-of-tenure without performance "
            "data cannot distinguish high-performers from low-performers with long tenure."
        )

    gaps.append(
        "**Geographic / regional data:** Salary ranges vary dramatically by location. "
        "Absence of location data makes salary comparisons potentially misleading."
    )

    gaps.append(
        "**Time dimension:** A single cross-sectional snapshot cannot reveal trends. "
        "Longitudinal data (e.g., annual snapshots) would allow causal inference."
    )

    if len(categorical_cols) < 3:
        gaps.append(
            "**Richer categorical features:** Gender, contract type (full-time/part-time), "
            "and employment status are standard HR variables that could reveal important subgroup effects."
        )

    return gaps


def _compute_confidence_scores(
    n: int,
    numeric_stats: dict,
    anomalies: dict,
    correlation_matrix: dict,
) -> dict[str, float]:
    """Assign a confidence score (0–1) to each key finding."""
    base = _sample_size_penalty(n)
    scores = {}

    for col, stats in numeric_stats.items():
        mean = stats.get("mean", 0)
        median = stats.get("median", 0)
        skew = abs(mean - median) / abs(median) if median != 0 else 0
        outliers = anomalies.get(col, {}).get("outlier_count", 0)
        # Penalize for skew and outliers
        penalty = min(skew * 0.3 + outliers * 0.05, 0.4)
        scores[f"mean_{col}"] = round(max(base - penalty, 0.1), 2)
        scores[f"outlier_detection_{col}"] = round(base * (0.7 if outliers > 0 else 0.9), 2)

    cols = list(correlation_matrix.keys())
    for i, c1 in enumerate(cols):
        for c2 in cols[i + 1:]:
            r = float(correlation_matrix[c1].get(c2, 0))
            # Correlations need larger n to be trustworthy
            corr_confidence = base * (0.6 if n < 30 else 0.85)
            scores[f"correlation_{c1}_{c2}"] = round(corr_confidence, 2)

    return scores


def run(analyst_output: dict, miner_output: dict) -> dict:
    """
    Entry point for the Critical Thinker agent.

    Args:
        analyst_output: Output dict from analyst.run()
        miner_output:   Output dict from data_miner.run()

    Returns:
        {
            "critique": {
                "flaws", "alternative_interps",
                "data_gaps", "confidence_scores",
                "overall_confidence", "verdict"
            },
            "metadata": dict
        }
    """
    print("[CRITICAL THINKER] ▶ Starting critical analysis phase...")

    if analyst_output.get("metadata", {}).get("status") != "success":
        raise ValueError("[CRITICAL THINKER] ✖ Received failed output from Analyst. Halting.")

    insights    = analyst_output["insights"]
    quality     = miner_output["quality_report"]
    n           = quality["clean_rows"]
    numeric_stats    = insights.get("numeric_stats", {})
    categorical_stats = insights.get("categorical_stats", {})
    correlation_matrix = insights.get("correlation_matrix", {})
    anomalies   = insights.get("anomalies", {})
    overview    = insights.get("overview", {})

    # ── Run all checks ────────────────────────────────────────────────────────
    flaws = []

    sample_flaw = _check_sample_size(n)
    if sample_flaw:
        flaws.append(sample_flaw)

    flaws += _check_correlation_causation(correlation_matrix, n)
    flaws += _check_outlier_impact(numeric_stats, anomalies)
    flaws += _check_cv_interpretation(numeric_stats)
    flaws += _check_categorical_dominance(categorical_stats, n)

    # ── Alternative interpretations ───────────────────────────────────────────
    alternatives = _build_alternative_interpretations(
        numeric_stats, correlation_matrix, anomalies, n
    )

    # ── Data gaps ─────────────────────────────────────────────────────────────
    data_gaps = _suggest_data_gaps(
        overview.get("numeric_columns", []),
        overview.get("categorical_columns", []),
        n,
        correlation_matrix,
    )

    # ── Confidence scores ─────────────────────────────────────────────────────
    confidence_scores = _compute_confidence_scores(n, numeric_stats, anomalies, correlation_matrix)

    # ── Overall confidence ────────────────────────────────────────────────────
    critical_count = sum(1 for f in flaws if f["severity"] == "CRITICAL")
    warning_count  = sum(1 for f in flaws if f["severity"] == "WARNING")
    avg_conf       = sum(confidence_scores.values()) / len(confidence_scores) if confidence_scores else 0.5

    if critical_count > 0 or avg_conf < 0.45:
        overall = "LOW"
    elif warning_count > 2 or avg_conf < 0.65:
        overall = "MEDIUM"
    else:
        overall = "HIGH"

    # ── Verdict narrative ─────────────────────────────────────────────────────
    verdict_parts = [
        f"This analysis is based on {n} records, which is "
        f"{'critically insufficient' if n < 30 else 'insufficient' if n < 100 else 'acceptable'} "
        f"for robust statistical inference.",
    ]
    if critical_count:
        verdict_parts.append(
            f"{critical_count} critical flaw(s) severely undermine the reliability of all conclusions."
        )
    if warning_count:
        verdict_parts.append(
            f"{warning_count} warning(s) indicate that specific insights require additional validation."
        )
    verdict_parts.append(
        f"Overall confidence in the reported insights: **{overall}**. "
        f"{'Do not use these findings for strategic decisions without collecting more data.' if overall == 'LOW' else ''}"
        f"{'Treat conclusions as directional signals, not established facts.' if overall == 'MEDIUM' else ''}"
        f"{'Findings are reasonably reliable, but independent validation is still advised.' if overall == 'HIGH' else ''}"
    )
    verdict = " ".join(verdict_parts)

    print(
        f"[CRITICAL THINKER] ✔ Found {len(flaws)} flaw(s), "
        f"{len(alternatives)} alternative interpretation(s). "
        f"Overall confidence: {overall}.\n"
    )

    return {
        "critique": {
            "flaws":                flaws,
            "alternative_interps":  alternatives,
            "data_gaps":            data_gaps,
            "confidence_scores":    confidence_scores,
            "overall_confidence":   overall,
            "verdict":              verdict,
        },
        "metadata": {
            "agent":     "Critical Thinker",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "status":    "success",
        },
    }
