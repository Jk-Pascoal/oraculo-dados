"""
╔══════════════════════════════════════════╗
║          AGENT 3 — NARRATOR             ║
╚══════════════════════════════════════════╝
Responsibilities:
  - Receive analyst insights
  - Translate statistics into human language
  - Structure a readable narrative report (Markdown)
  - Output final formatted report
"""

from datetime import datetime
from typing import Any


def run(analyst_output: dict, miner_output: dict, critic_output: dict | None = None) -> dict:
    """
 Entry point for the Narrator agent.

 Args:
     analyst_output:  Output dict from analyst.run().
     miner_output:    Output dict from data_miner.run() (for quality context).
     critic_output:   Optional output dict from critical_thinker.run().

 Returns:
     {
         "report_markdown": str,
         "metadata": dict
     }
 """
    print("[NARRATOR] ▶ Starting narrative generation phase...")

    # ── Validate input ────────────────────────────────────────────────────────
    if analyst_output.get("metadata", {}).get("status") != "success":
        raise ValueError("[NARRATOR] ✖ Received failed output from Analyst. Halting.")

    insights = analyst_output["insights"]
    quality  = miner_output["quality_report"]
    ts       = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

    # ── Build Markdown Report ─────────────────────────────────────────────────
    lines = []

    # Header
    lines += [
        "# 📊 Relatório Final — Oráculo de Dados",
        f"> Gerado automaticamente em {ts} pelo pipeline multi-agente.\n",
        "---",
    ]

    # Section 1 – Data Quality
    lines += [
        "## 🧹 Fase 1 · Data Miner — Qualidade dos Dados",
        "",
        f"| Métrica | Valor |",
        f"|---------|-------|",
        f"| Linhas originais | {quality['original_rows']} |",
        f"| Linhas após limpeza | {quality['clean_rows']} |",
        f"| Colunas | {quality['original_columns']} |",
        f"| Duplicatas removidas | {quality['duplicates_removed']} |",
        "",
        "**Colunas detectadas:** " + ", ".join(f"`{c}`" for c in quality["columns"]),
        "",
    ]

    # Missing values
    missing = {k: v for k, v in quality["missing_values_per_column"].items() if v > 0}
    if missing:
        lines.append("**Valores ausentes encontrados:**\n")
        for col, count in missing.items():
            lines.append(f"- `{col}`: {count} ausente(s)")
    else:
        lines.append("✅ Nenhum valor ausente encontrado após limpeza.")
    lines.append("")

    # Section 2 – Numeric Analysis
    lines += [
        "---",
        "## 📈 Fase 2 · Analista — Análise Numérica",
        "",
    ]
    numeric_stats = insights.get("numeric_stats", {})
    if numeric_stats:
        for col, stats in numeric_stats.items():
            lines += [
                f"### `{col}`",
                f"| Estatística | Valor |",
                f"|-------------|-------|",
                f"| Média       | {stats['mean']} |",
                f"| Mediana     | {stats['median']} |",
                f"| Desvio Padrão| {stats['std']} |",
                f"| Mínimo      | {stats['min']} |",
                f"| Máximo      | {stats['max']} |",
                f"| Q1 (25%)    | {stats['q25']} |",
                f"| Q3 (75%)    | {stats['q75']} |",
                "",
            ]
    else:
        lines.append("_Nenhuma coluna numérica encontrada._\n")

    # Section 3 – Categorical Analysis
    lines += [
        "---",
        "## 🏷️ Fase 2 · Analista — Análise Categórica",
        "",
    ]
    cat_stats = insights.get("categorical_stats", {})
    if cat_stats:
        for col, stats in cat_stats.items():
            lines += [
                f"### `{col}`",
                f"- **Valores únicos:** {stats['unique_values']}",
                f"- **Moda (mais frequente):** `{stats['mode']}`",
                "- **Top valores:**",
            ]
            for val, cnt in list(stats["top_10"].items())[:5]:
                lines.append(f"  - `{val}` → {cnt} ocorrência(s)")
            lines.append("")
    else:
        lines.append("_Nenhuma coluna categórica encontrada._\n")

    # Section 4 – Anomalies
    lines += [
        "---",
        "## ⚠️ Fase 2 · Analista — Anomalias Detectadas (IQR)",
        "",
    ]
    anomalies = insights.get("anomalies", {})
    any_anomaly = False
    for col, info in anomalies.items():
        if info["outlier_count"] > 0:
            any_anomaly = True
            lines.append(
                f"- **`{col}`**: {info['outlier_count']} outlier(s) → valores: {info['outlier_values']}"
            )
    if not any_anomaly:
        lines.append("✅ Nenhuma anomalia significativa detectada.")
    lines.append("")

    # Section 5 – Key Findings (Narrative)
    lines += [
        "---",
        "## 💡 Fase 3 · Narrador — Descobertas Principais",
        "",
    ]
    findings = insights.get("key_findings", [])
    if findings:
        for i, finding in enumerate(findings, 1):
            lines.append(f"{i}. {finding}")
    else:
        lines.append("_Nenhuma descoberta destacada._")
    lines.append("")

    # Section 6 – Correlation
    corr = insights.get("correlation_matrix", {})
    if corr:
        lines += [
            "---",
            "## 🔗 Fase 2 · Analista — Correlações",
            "",
            "High positive or negative correlations (|r| > 0.7):",
            "",
        ]
        found_corr = False
        cols = list(corr.keys())
        for i, c1 in enumerate(cols):
            for c2 in cols[i+1:]:
                r = corr[c1].get(c2, 0)
                if r is not None and abs(r) > 0.7:
                    found_corr = True
                    direction = "positiva" if r > 0 else "negativa"
                    lines.append(f"- `{c1}` ↔ `{c2}`: r = {round(r, 4)} ({direction})")
        if not found_corr:
            lines.append("_Nenhuma correlação forte detectada entre variáveis numéricas._")
        lines.append("")

    # Section 7 – Critical Thinker
    if critic_output and critic_output.get("metadata", {}).get("status") == "success":
        critique = critic_output["critique"]
        overall_conf = critique.get("overall_confidence", "N/A")
        conf_emoji = {"HIGH": "🟢", "MEDIUM": "🟡", "LOW": "🔴"}.get(overall_conf, "⚪")

        lines += [
            "---",
            f"## 🧠 Fase 4 · Pensador Crítico — Revisão Analítica",
            "",
            f"### Confiança Geral: {conf_emoji} {overall_conf}",
            "",
            f"> {critique.get('verdict', '')}",
            "",
        ]

        # Flaws
        flaws = critique.get("flaws", [])
        if flaws:
            lines += [
                "### ⚠️ Falhas e Problemas Metodológicos",
                "",
            ]
            severity_emoji = {"CRITICAL": "🔴", "WARNING": "🟡", "INFO": "🔵"}
            for flaw in flaws:
                emoji = severity_emoji.get(flaw["severity"], "⚪")
                lines += [
                    f"#### {emoji} {flaw['type']} `[{flaw['severity']}]`",
                    f"{flaw['description']}",
                    "",
                ]

        # Confidence scores
        conf_scores = critique.get("confidence_scores", {})
        if conf_scores:
            lines += [
                "### 📊 Confiança por Métrica",
                "",
                "| Métrica | Score | Nível |",
                "|---------|-------|-------|",
            ]
            for metric, score in conf_scores.items():
                level = "🟢 HIGH" if score >= 0.75 else "🟡 MEDIUM" if score >= 0.45 else "🔴 LOW"
                lines.append(f"| `{metric}` | {score} | {level} |")
            lines.append("")

        # Alternative interpretations
        alts = critique.get("alternative_interps", [])
        if alts:
            lines += [
                "### 🔄 Interpretações Alternativas",
                "",
            ]
            for i, alt in enumerate(alts, 1):
                lines += [
                    f"**{i}. Achado:** {alt['finding']}",
                    f"- **Alternativa:** {alt['alternative']}",
                    f"- **Como resolver:** {alt['test_to_resolve']}",
                    "",
                ]

        # Data gaps
        gaps = critique.get("data_gaps", [])
        if gaps:
            lines += [
                "### 🗂️ Dados Adicionais Necessários",
                "",
            ]
            for gap in gaps:
                lines.append(f"- {gap}")
            lines.append("")

    # Footer
    lines += [
        "---",
        "## 🤖 Pipeline Multi-Agente",
        "",
        "| Agente | Status | Timestamp |",
        "|--------|--------|-----------|",
        f"| Data Miner     | ✅ | {miner_output['metadata']['timestamp']} |",
        f"| Analyst        | ✅ | {analyst_output['metadata']['timestamp']} |",
        f"| Critical Thinker | {'✅' if critic_output else '⏭️ skipped'} | {critic_output['metadata']['timestamp'] if critic_output else 'N/A'} |",
        f"| Narrator       | ✅ | {ts} |",
        "",
        "> _Relatório gerado pelo Oráculo de Dados — pipeline de análise autônoma._",
    ]

    report_md = "\n".join(lines)

    output = {
        "report_markdown": report_md,
        "metadata": {
            "agent": "Narrator",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "status": "success",
        },
    }

    print("[NARRATOR] ✔ Report generated.\n")
    return output
