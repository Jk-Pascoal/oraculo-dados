# 🔮 Oráculo de Dados — Pipeline Multi-Agente Autônomo

> Plataforma de análise de dados com 4 agentes IA coordenados: **Data Miner → Analyst → Critical Thinker → Narrator**

![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32+-red?logo=streamlit)
![Pandas](https://img.shields.io/badge/Pandas-2.0+-green?logo=pandas)
![CI](https://github.com/jk-pascoal/oraculo-dados/actions/workflows/ci.yml/badge.svg)

---

## 🧠 Arquitetura

```
Raw Data
  └─▶ [1] Data Miner       → Limpeza, deduplicação, validação
         └─▶ [2] Analyst   → Estatísticas, correlações, anomalias
                └─▶ [3] Critical Thinker → Falhas, vieses, confiança
                       └─▶ [4] Narrator → Relatório Markdown final
```

## 📦 Estrutura do Projeto

```
oraculo-dados/
├── app.py                        # Streamlit UI (entrada principal)
├── requirements.txt              # Dependências de produção
├── requirements-dev.txt          # Dependências de desenvolvimento
├── .streamlit/
│   └── config.toml               # Configuração de tema e servidor
├── .github/
│   └── workflows/
│       └── ci.yml                # GitHub Actions CI
├── orchestrator/
│   ├── __init__.py
│   └── orchestrator.py           # Coordenador do pipeline
├── agents/
│   ├── data_miner.py
│   ├── analyst.py
│   ├── critical_thinker.py
│   └── narrator.py
└── tests/
    ├── test_agents.py
    └── test_orchestrator.py
```

## 🚀 Deploy no Streamlit Community Cloud

1. Faça um fork ou push deste repositório para o seu GitHub
2. Acesse [share.streamlit.io](https://share.streamlit.io) e clique em **New app**
3. Selecione o repositório, branch `main` e arquivo principal `app.py`
4. Clique em **Deploy** — o app estará disponível em alguns minutos

> **Nota:** O toggle "Salvar relatório em disco" está desativado por padrão para compatibilidade com ambientes cloud.

## 💻 Executar Localmente

### 1. Clonar e instalar dependências

```bash
git clone https://github.com/jk-pascoal/oraculo-dados.git
cd oraculo-dados
python -m venv .venv
source .venv/bin/activate        # Linux/Mac
.venv\Scripts\activate           # Windows
pip install -r requirements.txt
```

### 2. Rodar a interface web

```bash
streamlit run app.py
```

Acesse em `http://localhost:8501`

### 3. Rodar via orchestrator (linha de comando)

```bash
# Com dados de exemplo embutidos
python -c "from orchestrator.orchestrator import run_pipeline; r=run_pipeline(save_to_disk=False); print(r['narrator']['report_markdown'])"

# Com seu próprio arquivo JSON
python -c "from orchestrator.orchestrator import run_pipeline; r=run_pipeline('meus_dados.json', save_to_disk=True)"
```

O arquivo JSON deve ser uma lista de registros:
```json
[
  {"nome": "Alice", "idade": 29, "salario": 72000},
  {"nome": "Bob",   "idade": 34, "salario": 85000}
]
```

## 🧪 Testes

```bash
pip install -r requirements-dev.txt
pytest tests/ -v
```

## 🤖 Agentes

| Agente | Responsabilidade | Output |
|--------|-----------------|--------|
| **Data Miner** | Limpa e valida os dados brutos | Dataset limpo + relatório de qualidade |
| **Analyst** | Estatísticas descritivas, correlações, anomalias IQR | Insights estruturados |
| **Critical Thinker** | Detecta vieses, correlações espúrias, atribui confiança | Falhas, alternativas, lacunas |
| **Narrator** | Traduz tudo em linguagem natural | Relatório Markdown completo |

## 📊 Features da UI

- **Upload JSON** ou **Dados de Exemplo** integrados
- **Métricas** em tempo real (registros, achados, falhas, outliers)
- **Banner de confiança** 🔴/🟡/🟢 com veredito do Critical Thinker
- **Coluna Insights** — relatório completo com download `.md`
- **Coluna Interpretação** — 3 abas: Padrões / Riscos / Recomendações

## 📄 Licença

MIT
