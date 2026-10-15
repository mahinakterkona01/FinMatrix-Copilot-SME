# ⚡ FinMatrix Copilot — SME Financial Co-Pilot

**Official Submission for 2026 Shenzhen International FinTech Competition (FinTechathon 2026)**  
**Track / Topic:** Topic E — SME Finance Copilot  
**Team Identity:** `Team FinMatrixDUO`  

---

## 📌 Executive Overview

**FinMatrix Copilot** is an enterprise-grade AI financial decision-support and liquidity intelligence engine designed for Small and Medium Enterprises (SMEs). Standard conversational financial assistants often suffer from arithmetic hallucinations and lookahead data leakage in forecasting. 

FinMatrix Copilot addresses these gaps by decoupling deterministic numerical execution from language models, enforcing strict Level 1 Temporal Holdout Validation for time-series forecasting, and embedding an adversarial guardrail layer for input security.

---

## 🚀 Key Functional Modules

1. **📊 Executive Financial Dashboard:** Multi-currency ($/৳/€/£/¥) and multi-sector operating environment with real-time liquidity safety threshold alerts and solvency gauge.
2. **📈 ML Cash-Flow Forecaster:** Time-series forecasting using historical lag features ($t-1, t-7$) to project net liquidity trends without future lookahead bias.
3. **🧪 What-If Stress Simulator:** Independent macro shock simulation evaluating revenue contractions and expense inflation on net liquidity.
4. **🧾 Working Capital & Invoice Discounting:** Accelerated invoice settlement calculator providing effective annualized cost rate analysis for early liquidity.
5. **📚 Policy Retrieval Engine (RAG):** Grounded policy search engine retrieving central bank SME circulars and financing guidelines with source citations.
6. **🤖 Interactive AI Copilot:** Natural language financial guidance powered by context-aware execution and safety validation.
7. **🛡️ Adversarial Security Guardrail:** Structural input filter intercepting prompt hijacking, SQL injection patterns, and unsafe commands.
8. **📑 Institutional Audit Exporter:** Automated generation and download of structured financial audit reports.

---

## 🛠️ System Architecture & Technology Stack

FinMatrix-Copilot-SME/
├── app.py                     # Streamlit High-Contrast Dashboard Interface
├── src/                       # Core Analytical & Intelligence Engines
│   ├── forecasting.py         # Time-Series ML Forecaster Engine
│   ├── retrieval.py           # TF-IDF Policy Knowledge Search (RAG)
│   ├── copilot.py             # Interactive Financial AI Engine
│   ├── safety.py              # Adversarial Security Guardrails
│   ├── financial_tools.py     # Solvency & Liquidity Metrics
│   └── data_loader.py         # SME Ledger Ingestion & Normalization
├── docs/                      # Research & Requirements Documentation
├── notebooks/                 # Temporal Validation & EDA Notebooks
├── data/raw/                  # Verified Primary SME Cash Flow Datasets
├── requirements.txt           # Python Environment Dependencies
└── LICENSE                    # MIT Open-Source License

* **Frontend & Dashboard:** Streamlit (High-Contrast Custom CSS Interface)
* **Data Processing & Analytics:** Pandas, NumPy, Plotly Express
* **Machine Learning & Time-Series:** Scikit-Learn (Random Forest Forecaster)
* **Retrieval Engine (RAG):** TF-IDF Vectorization & Cosine Similarity
* **Security & Testing:** Regex Pattern Matching Guardrails & Pytest Framework

---

## 💻 Quick Start & Local Execution Guide

### 1. Repository Cloning & Environment Setup

```powershell
git clone [https://github.com/mahinakterkona01/FinMatrix-Copilot-SME.git](https://github.com/mahinakterkona01/FinMatrix-Copilot-SME.git)
cd FinMatrix-Copilot-SME

Research & Validation Methodology
FinMatrix Copilot enforces a 3-Level Evaluation Framework:

Level 1 (Temporal Validation): Time-series data is split strictly chronologically to eliminate data leakage.

Level 2 (Business-Level Validation): Evaluated across 4 distinct SME sectors (Retail, Technology/SaaS, Manufacturing, Logistics).

Level 3 (External Policy Consistency): Grounded in official central bank SME working capital circulars and refinancing guidelines.

License & Copyright Notice
Distributed under the MIT License. See LICENSE for full details.

Copyright (c) 2026 Team FinMatrixDUO.