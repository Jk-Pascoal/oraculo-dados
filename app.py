"""
🔮 Oráculo de Dados — Streamlit UI
Multi-Agent Autonomous Data Analysis Platform
"""

import streamlit as st
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from orchestrator.orchestrator import run_pipeline

# ─────────────────────────────────────────────────────────────────────────────
# Page config
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Oráculo de Dados",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# Premium CSS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">

<style>
*, *::before, *::after { box-sizing: border-box; }

html, body, [data-testid="stAppViewContainer"] {
    background: #080c14 !important;
    font-family: 'Inter', sans-serif;
}
[data-testid="stSidebar"] {
    background: #0d1117 !important;
    border-right: 1px solid rgba(99,102,241,0.2);
}
[data-testid="stSidebar"] h2 {
    color: #a78bfa !important;
    font-size: 1rem !important;
    letter-spacing: 1px;
    text-transform: uppercase;
}

/* ── Title ─────────────────────────────────────────────────────────────────── */
.oracle-header {
    padding: 2rem 0 1.25rem;
    background: linear-gradient(135deg, #0f0c29, #24243e, #0f0c29);
    border-radius: 18px;
    border: 1px solid rgba(124,58,237,0.3);
    margin-bottom: 1.5rem;
    text-align: center;
    position: relative;
    overflow: hidden;
}
.oracle-header::before {
    content: '';
    position: absolute; inset: 0;
    background: radial-gradient(ellipse at 50% 0%, rgba(124,58,237,0.15) 0%, transparent 70%);
}
.oracle-title {
    font-size: 2.4rem;
    font-weight: 700;
    background: linear-gradient(135deg, #a78bfa, #60a5fa, #34d399);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0;
    letter-spacing: -1px;
}
.oracle-caption {
    color: rgba(148,163,184,0.65);
    font-size: 0.85rem;
    font-weight: 300;
    margin-top: 0.4rem;
    letter-spacing: 2px;
    text-transform: uppercase;
}

/* ── Metric strip ──────────────────────────────────────────────────────────── */
.metric-strip {
    display: flex;
    gap: 0.75rem;
    flex-wrap: wrap;
    margin-bottom: 1.5rem;
}
.metric-pill {
    background: rgba(15,20,35,0.9);
    border: 1px solid rgba(99,102,241,0.25);
    border-radius: 10px;
    padding: 0.6rem 1rem;
    display: flex;
    align-items: center;
    gap: 0.6rem;
    flex: 1;
    min-width: 110px;
    transition: border-color 0.2s, transform 0.2s;
}
.metric-pill:hover { border-color: rgba(124,58,237,0.5); transform: translateY(-2px); }
.metric-num {
    font-size: 1.5rem;
    font-weight: 700;
    background: linear-gradient(135deg, #a78bfa, #60a5fa);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1;
}
.metric-lbl {
    font-size: 0.7rem;
    color: rgba(148,163,184,0.65);
    text-transform: uppercase;
    letter-spacing: 0.8px;
}

/* ── Section headings ──────────────────────────────────────────────────────── */
.sec-title {
    font-size: 1rem;
    font-weight: 600;
    color: #e2e8f0;
    margin: 1.25rem 0 0.75rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}
.sec-title::after {
    content: '';
    flex: 1;
    height: 1px;
    background: linear-gradient(to right, rgba(124,58,237,0.35), transparent);
}

/* ── Confidence banner ─────────────────────────────────────────────────────── */
.conf-banner {
    border-radius: 12px;
    padding: 1rem 1.25rem;
    margin-bottom: 1.25rem;
    border: 1px solid;
}
.conf-banner.low    { background: rgba(239,68,68,0.07);  border-color: rgba(239,68,68,0.25); }
.conf-banner.medium { background: rgba(245,158,11,0.07); border-color: rgba(245,158,11,0.25); }
.conf-banner.high   { background: rgba(52,211,153,0.07); border-color: rgba(52,211,153,0.25); }
.conf-label {
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 1px;
    color: rgba(148,163,184,0.6);
    margin-bottom: 0.4rem;
}
.conf-badge {
    display: inline-block;
    padding: 0.2rem 0.9rem;
    border-radius: 50px;
    font-weight: 700;
    font-size: 0.85rem;
}
.conf-badge.low    { background: rgba(239,68,68,0.15);  color: #f87171; border: 1px solid rgba(239,68,68,0.4); }
.conf-badge.medium { background: rgba(245,158,11,0.15); color: #fbbf24; border: 1px solid rgba(245,158,11,0.4); }
.conf-badge.high   { background: rgba(52,211,153,0.15); color: #34d399; border: 1px solid rgba(52,211,153,0.4); }
.conf-verdict {
    margin-top: 0.7rem;
    font-size: 0.82rem;
    color: rgba(148,163,184,0.8);
    line-height: 1.6;
}

/* ── Flaw cards ────────────────────────────────────────────────────────────── */
.flaw {
    border-left: 3px solid;
    padding: 0.75rem 1rem;
    border-radius: 0 10px 10px 0;
    background: rgba(15,20,35,0.7);
    margin-bottom: 0.6rem;
}
.flaw.critical { border-color: #ef4444; background: rgba(239,68,68,0.06); }
.flaw.warning  { border-color: #f59e0b; background: rgba(245,158,11,0.06); }
.flaw.info     { border-color: #3b82f6; background: rgba(59,130,246,0.06); }
.flaw-type { font-size: 0.8rem; font-weight: 600; color: #e2e8f0; margin-bottom: 0.3rem; }
.flaw-desc { font-size: 0.78rem; color: rgba(148,163,184,0.8); line-height: 1.55; }
.sev-badge {
    display: inline-block;
    padding: 0.1rem 0.5rem;
    border-radius: 50px;
    font-size: 0.65rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-left: 0.4rem;
    vertical-align: middle;
}
.sev-badge.critical { background: rgba(239,68,68,0.15); color: #f87171; }
.sev-badge.warning  { background: rgba(245,158,11,0.15); color: #fbbf24; }
.sev-badge.info     { background: rgba(59,130,246,0.15); color: #60a5fa; }

/* ── Pattern item ──────────────────────────────────────────────────────────── */
.pattern {
    display: flex;
    gap: 0.6rem;
    padding: 0.6rem 0.75rem;
    background: rgba(15,20,35,0.6);
    border: 1px solid rgba(99,102,241,0.15);
    border-radius: 9px;
    margin-bottom: 0.5rem;
    font-size: 0.8rem;
    color: rgba(148,163,184,0.85);
    line-height: 1.5;
    align-items: flex-start;
}
.pattern-icon { flex-shrink: 0; }

/* ── Recommendation ────────────────────────────────────────────────────────── */
.rec {
    display: flex;
    gap: 0.6rem;
    padding: 0.7rem 0.9rem;
    background: rgba(15,20,35,0.6);
    border: 1px solid rgba(52,211,153,0.15);
    border-radius: 9px;
    margin-bottom: 0.5rem;
    font-size: 0.8rem;
    color: rgba(148,163,184,0.85);
    line-height: 1.5;
}

/* ── Alt interpretation ────────────────────────────────────────────────────── */
.alt {
    background: rgba(15,20,35,0.7);
    border: 1px solid rgba(99,102,241,0.2);
    border-radius: 10px;
    padding: 0.75rem 1rem;
    margin-bottom: 0.6rem;
}
.alt-finding { font-size: 0.78rem; color: #a78bfa; font-weight: 500; margin-bottom: 0.35rem; }
.alt-body    { font-size: 0.77rem; color: rgba(148,163,184,0.8); line-height: 1.5; }
.alt-test    { font-size: 0.75rem; color: #60a5fa; margin-top: 0.3rem; font-style: italic; }

/* ── Report container ──────────────────────────────────────────────────────── */
.report-wrap {
    background: rgba(15,20,35,0.6);
    border: 1px solid rgba(99,102,241,0.15);
    border-radius: 14px;
    padding: 1.5rem;
}
.report-wrap h1, .report-wrap h2, .report-wrap h3 { color: #e2e8f0 !important; }
.report-wrap p, .report-wrap li { color: rgba(148,163,184,0.85) !important; font-size: 0.88rem !important; }
.report-wrap table { border-collapse: collapse; width: 100%; font-size: 0.82rem; }
.report-wrap td, .report-wrap th {
    border: 1px solid rgba(99,102,241,0.2);
    padding: 0.4rem 0.75rem;
    color: rgba(148,163,184,0.85);
}
.report-wrap th { background: rgba(99,102,241,0.1); color: #a78bfa; }
.report-wrap code { color: #a78bfa; background: rgba(124,58,237,0.1); padding: 0.1rem 0.4rem; border-radius: 4px; }
.report-wrap blockquote {
    border-left: 3px solid rgba(124,58,237,0.4);
    padding-left: 1rem;
    color: rgba(148,163,184,0.7) !important;
    margin: 0.5rem 0;
}

/* ── Pipeline flow ─────────────────────────────────────────────────────────── */
.flow {
    display: flex;
    gap: 0.4rem;
    align-items: center;
    flex-wrap: wrap;
    justify-content: center;
    margin: 1rem 0 0.5rem;
}
.flow-step {
    padding: 0.35rem 0.9rem;
    border: 1px solid rgba(99,102,241,0.25);
    border-radius: 50px;
    font-size: 0.75rem;
    color: rgba(148,163,184,0.7);
    background: rgba(15,20,35,0.8);
}
.flow-step.done { border-color: rgba(52,211,153,0.4); color: #34d399; background: rgba(52,211,153,0.06); }
.flow-arrow { color: rgba(99,102,241,0.4); font-size: 0.9rem; }

/* ── Sidebar controls ──────────────────────────────────────────────────────── */
[data-testid="stFileUploader"] > div {
    border: 2px dashed rgba(124,58,237,0.35) !important;
    background: rgba(15,20,35,0.5) !important;
    border-radius: 12px !important;
}
button[kind="primary"] {
    background: linear-gradient(135deg, #7c3aed, #4f46e5) !important;
    border: none !important; border-radius: 10px !important;
    font-weight: 600 !important;
    transition: all 0.2s !important;
    width: 100% !important;
}
button[kind="primary"]:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(124,58,237,0.4) !important;
}

/* ── Scrollbar ─────────────────────────────────────────────────────────────── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(124,58,237,0.4); border-radius: 10px; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def flow_html(done: bool = False) -> str:
    steps = [("🧹","Data Miner"),("📈","Analyst"),("🧠","Crítico"),("📝","Narrador")]
    parts = []
    for i, (icon, lbl) in enumerate(steps):
        cls = "flow-step done" if done else "flow-step"
        parts.append(f'<div class="{cls}">{icon} {lbl}</div>')
        if i < len(steps) - 1:
            parts.append('<span class="flow-arrow">→</span>')
    return f'<div class="flow">{"".join(parts)}</div>'


def metric_strip_html(result: dict) -> str:
    q  = result["data_miner"]["quality_report"]
    ins = result["analyst"]["insights"]
    cr  = result["critical_thinker"]["critique"]
    items = [
        ("📋", q["clean_rows"],                                           "Registros"),
        ("📊", q["original_columns"],                                     "Colunas"),
        ("💡", len(ins.get("key_findings", [])),                          "Achados"),
        ("⚠️", len(cr.get("flaws", [])),                                  "Falhas"),
        ("🚨", sum(v.get("outlier_count",0) for v in ins.get("anomalies",{}).values()), "Outliers"),
        ("🗂️", len(cr.get("data_gaps", [])),                              "Lacunas"),
    ]
    pills = "".join(
        f'<div class="metric-pill">'
        f'<div><div class="metric-num">{v}</div><div class="metric-lbl">{lbl}</div></div>'
        f'</div>'
        for icon, v, lbl in items
    )
    return f'<div class="metric-strip">{pills}</div>'


def conf_banner_html(critique: dict) -> str:
    level   = critique.get("overall_confidence", "MEDIUM")
    cls     = level.lower()
    emoji   = {"LOW": "🔴", "MEDIUM": "🟡", "HIGH": "🟢"}.get(level, "⚪")
    verdict = critique.get("verdict", "")
    return f"""
    <div class="conf-banner {cls}">
        <div class="conf-label">Confiança geral da análise</div>
        <span class="conf-badge {cls}">{emoji} {level}</span>
        <div class="conf-verdict">{verdict}</div>
    </div>"""


def render_flaws(flaws: list):
    sev_order = {"CRITICAL": 0, "WARNING": 1, "INFO": 2}
    for flaw in sorted(flaws, key=lambda f: sev_order.get(f["severity"], 9)):
        sev  = flaw["severity"].lower()
        icon = {"critical":"🔴","warning":"🟡","info":"🔵"}.get(sev,"⚪")
        st.markdown(f"""
        <div class="flaw {sev}">
            <div class="flaw-type">
                {icon} {flaw['type']}
                <span class="sev-badge {sev}">{flaw['severity']}</span>
            </div>
            <div class="flaw-desc">{flaw['description']}</div>
        </div>""", unsafe_allow_html=True)


def render_patterns(insights: dict):
    numeric  = insights.get("numeric_stats", {})
    corr     = insights.get("correlation_matrix", {})
    findings = insights.get("key_findings", [])
    anomalies = insights.get("anomalies", {})

    # Key findings
    if findings:
        st.markdown('<div class="sec-title">💡 Achados</div>', unsafe_allow_html=True)
        for f in findings[:6]:
            st.markdown(f'<div class="pattern"><span class="pattern-icon">→</span><span>{f}</span></div>', unsafe_allow_html=True)

    # Outliers
    any_out = any(v.get("outlier_count", 0) > 0 for v in anomalies.values())
    if any_out:
        st.markdown('<div class="sec-title">🚨 Anomalias</div>', unsafe_allow_html=True)
        for col, info in anomalies.items():
            if info.get("outlier_count", 0) > 0:
                vals = info["outlier_values"][:3]
                st.markdown(
                    f'<div class="pattern"><span class="pattern-icon">⚡</span>'
                    f'<span><code style="color:#a78bfa">{col}</code>: {info["outlier_count"]} outlier(s) → {vals}</span></div>',
                    unsafe_allow_html=True,
                )

    # Strong correlations
    cols = list(corr.keys())
    strong = []
    for i, c1 in enumerate(cols):
        for c2 in cols[i+1:]:
            r = float(corr[c1].get(c2, 0) or 0)
            if abs(r) > 0.7:
                strong.append((c1, c2, r))
    if strong:
        st.markdown('<div class="sec-title">🔗 Correlações Fortes</div>', unsafe_allow_html=True)
        for c1, c2, r in strong:
            arrow = "↑" if r > 0 else "↓"
            st.markdown(
                f'<div class="pattern"><span class="pattern-icon">{arrow}</span>'
                f'<span><code style="color:#a78bfa">{c1}</code> ↔ <code style="color:#60a5fa">{c2}</code>'
                f' &nbsp; r = <strong>{round(r,4)}</strong></span></div>',
                unsafe_allow_html=True,
            )


def render_recommendations(critique: dict):
    gaps  = critique.get("data_gaps", [])
    alts  = critique.get("alternative_interps", [])

    if gaps:
        st.markdown('<div class="sec-title">🗂️ Dados Adicionais Necessários</div>', unsafe_allow_html=True)
        for gap in gaps[:5]:
            st.markdown(f'<div class="rec"><span>📌</span><span>{gap}</span></div>', unsafe_allow_html=True)

    if alts:
        st.markdown('<div class="sec-title">🔄 Interpretações Alternativas</div>', unsafe_allow_html=True)
        for i, alt in enumerate(alts[:4], 1):
            st.markdown(f"""
            <div class="alt">
                <div class="alt-finding">#{i} · {alt['finding']}</div>
                <div class="alt-body"><strong style="color:#e2e8f0">Alternativa:</strong> {alt['alternative']}</div>
                <div class="alt-test">🔬 {alt['test_to_resolve']}</div>
            </div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# Header
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="oracle-header">
    <div class="oracle-title">🔮 Oráculo de Dados Autônomo</div>
    <div class="oracle-caption">Transformando dados em insight, narrativa e crítica</div>
</div>
""", unsafe_allow_html=True)

st.markdown(flow_html(done=False), unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# ===== SIDEBAR — INPUT =====
# ─────────────────────────────────────────────────────────────────────────────
st.sidebar.markdown("""
<div style="text-align:center; padding:0.75rem 0 1rem;">
    <div style="font-size:2rem;">🔮</div>
    <div style="color:#a78bfa; font-weight:700; font-size:1rem;">Oráculo de Dados</div>
    <div style="color:rgba(148,163,184,0.5); font-size:0.7rem; margin-top:0.2rem; letter-spacing:1px;">
        MULTI-AGENT PIPELINE v2
    </div>
</div>
<hr style="border-color:rgba(99,102,241,0.2); margin-bottom:1rem;">
""", unsafe_allow_html=True)

st.sidebar.header("📥 Entrada de Dados")

uploaded_file = st.sidebar.file_uploader(
    "Upload JSON",
    type="json",
    help="Lista de registros: [{coluna: valor, ...}, ...]",
)

st.sidebar.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

run_sample = st.sidebar.button("🧪 Dados de Exemplo", use_container_width=True)

st.sidebar.markdown("<hr style='border-color:rgba(99,102,241,0.15);'>", unsafe_allow_html=True)
st.sidebar.markdown("**⚙️ Opções**")
save_disk = st.sidebar.toggle("Salvar relatório em disco", value=True)

st.sidebar.markdown("""
<hr style="border-color:rgba(99,102,241,0.15);">
<div style="font-size:0.72rem; color:rgba(148,163,184,0.4); line-height:1.6;">
<strong style="color:rgba(148,163,184,0.6);">Formato esperado</strong><br>
<code style="color:#a78bfa; font-size:0.7rem;">[ {"col": val, ...}, ... ]</code><br><br>
Colunas numéricas e categóricas são detectadas automaticamente.
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# ===== PROCESS =====
# ─────────────────────────────────────────────────────────────────────────────
data = None
if uploaded_file:
    try:
        data = json.load(uploaded_file)
        if not isinstance(data, list):
            st.error("❌ O JSON deve ser uma lista de registros (array de objetos).")
            data = None
        else:
            st.sidebar.success(f"✅ {len(data)} registros carregados")
    except json.JSONDecodeError as e:
        st.sidebar.error(f"❌ JSON inválido: {e}")

trigger = (uploaded_file and st.sidebar.button("🚀 Executar Análise", type="primary", use_container_width=True)) \
          or run_sample

if trigger:
    input_data = data if (uploaded_file and data is not None and not run_sample) else None

    with st.spinner("Os agentes estão trabalhando..."):
        result = run_pipeline(
            data=input_data,
            save_to_disk=save_disk,
            capture_logs=False,
        )

    st.session_state["result"] = result
    st.success("✅ Análise concluída! Todos os agentes executaram com sucesso.")


# ─────────────────────────────────────────────────────────────────────────────
# ===== OUTPUT =====
# ─────────────────────────────────────────────────────────────────────────────
if "result" in st.session_state:
    result   = st.session_state["result"]
    insights = result["analyst"]["insights"]
    critique = result["critical_thinker"]["critique"]
    report   = result["narrator"]["report_markdown"]
    quality  = result["data_miner"]["quality_report"]

    # ── Metric strip ──────────────────────────────────────────────────────────
    st.markdown(metric_strip_html(result), unsafe_allow_html=True)

    # ── Confidence banner ─────────────────────────────────────────────────────
    st.markdown(conf_banner_html(critique), unsafe_allow_html=True)

    st.markdown("---")

    # ── Two-column layout ─────────────────────────────────────────────────────
    col1, col2 = st.columns([1.1, 0.9], gap="large")

    # ─── LEFT: Insights ───────────────────────────────────────────────────────
    with col1:
        st.markdown('<div class="sec-title">📊 Insights — Relatório Completo</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="report-wrap">{report}</div>', unsafe_allow_html=True)
        st.download_button(
            "⬇️ Baixar Relatório (.md)",
            data=report,
            file_name="oraculo_report.md",
            mime="text/markdown",
            use_container_width=True,
        )

    # ─── RIGHT: Interpretação ─────────────────────────────────────────────────
    with col2:
        st.markdown('<div class="sec-title">🧠 Interpretação</div>', unsafe_allow_html=True)

        tab_pat, tab_risk, tab_rec = st.tabs([
            "🔍 Padrões",
            "⚠️ Riscos",
            "💊 Recomendações",
        ])

        with tab_pat:
            render_patterns(insights)

        with tab_risk:
            flaws = critique.get("flaws", [])
            if flaws:
                render_flaws(flaws)
            else:
                st.success("Nenhuma falha metodológica detectada.")

            # Confidence per metric
            conf_scores = critique.get("confidence_scores", {})
            if conf_scores:
                st.markdown('<div class="sec-title">📉 Confiança por Métrica</div>', unsafe_allow_html=True)
                import pandas as pd
                rows = []
                for metric, score in conf_scores.items():
                    level = "🟢 HIGH" if score >= 0.75 else ("🟡 MEDIUM" if score >= 0.45 else "🔴 LOW")
                    rows.append({"Métrica": metric, "Score": score, "Nível": level})
                st.dataframe(
                    pd.DataFrame(rows).set_index("Métrica"),
                    use_container_width=True,
                    height=min(35 * len(rows) + 38, 320),
                )

        with tab_rec:
            render_recommendations(critique)

    # ── Pipeline completion ───────────────────────────────────────────────────
    st.markdown("---")
    st.markdown(flow_html(done=True), unsafe_allow_html=True)
    st.markdown(
        '<p style="text-align:center; color:rgba(148,163,184,0.3); font-size:0.75rem;">'
        'Oráculo de Dados · Pipeline Multi-Agente Autônomo</p>',
        unsafe_allow_html=True,
    )
