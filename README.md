# 🔮 Oráculo de Dados — Pipeline Multi-Agente Autônomo

> Plataforma de análise de dados com 4 agentes IA coordenados: **Data Miner → Analyst → Critical Thinker → Narrator**

![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32+-red?logo=streamlit)
![Pandas](https://img.shields.io/badge/Pandas-2.0+-green?logo=pandas)

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
├── app.py                        # Streamlit UI
├── pipeline_cli.py               # Entrada via linha de comando
├── requirements.txt
├── orchestrator/
│   ├── __init__.py
│   └── orchestrator.py           # Coordenador do pipeline
└── agents/
    ├── data_miner.py
    ├── analyst.py
    ├── critical_thinker.py
    └── narrator.py
```

## 🚀 Como Executar

### 1. Clonar e instalar dependências

```bash
git clone https://github.com/<seu-usuario>/oraculo-dados.git
cd oraculo-dados
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

### 2. Rodar a interface web

```bash
streamlit run app.py
```

Acesse em `http://localhost:8501`

### 3. Rodar via linha de comando

```bash
# Com dados de exemplo embutidos
python pipeline_cli.py

# Com seu próprio arquivo JSON
python pipeline_cli.py meus_dados.json
```

O arquivo JSON deve ser uma lista de registros:
```json
[
  {"nome": "Alice", "idade": 29, "salário": 72000},
  {"nome": "Bob",   "idade": 34, "salário": 85000}
]
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
- **Coluna Insights** — relatório completo com download
- **Coluna Interpretação** — 3 abas: Padrões / Riscos / Recomendações

## 📄 Licença

MIT
