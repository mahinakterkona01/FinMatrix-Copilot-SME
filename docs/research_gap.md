# FinPilot AI — Research Gap & Architectural Innovations

**Author/Team:** FinPilot AI Development Team  
**Competition:** 2026 Shenzhen International FinTech Competition (Topic E: SME Finance Copilot)

---

## 1. Context & Existing Solution Gaps

When analyzing traditional SME financial software and generic conversational AI assistants, we identified three core structural gaps that our project, **FinPilot AI**, addresses:

1. **Arithmetic & Forecast Instability:** Standard LLM wrappers tend to hallucinate numerical values during dynamic financial reasoning. We resolve this by decoupling raw math execution from the LLM and delegating arithmetic tasks to deterministic Python modules.
2. **Temporal Data Leakage in Forecasting:** Conventional ML code frequently splits time-series data at random, causing lookahead bias. We strictly enforce a chronological Level 1 Temporal Validation pipeline using historical-only lag features ($t-1$, $t-7$).
3. **Regulatory Citation Deficiency:** Generic financial assistants often issue advice without verifying underlying policy guidelines. We build a Retrieval-Augmented Generation (RAG) framework that grounds all policy queries directly in ingested Bangladesh Bank circulars with precise section citations.

---

## 2. Our System Innovations vs. Baseline Approaches

| Core Module | Standard Baseline | Our FinPilot AI Implementation | Architectural Scope |
| :--- | :--- | :--- | :--- |
| **Financial Calculations** | Generative LLM numerical inference | Deterministic Python Tool Layer (`src/financial_tools.py`) | Guarantees exact mathematical outputs for ledger and cash-flow logic. |
| **Cash-Flow Forecasting** | Standard models prone to lookahead bias | Level 1 Temporal ML Engine with historical rolling medians | Eliminates temporal leakage and mitigates extreme single-day transaction spikes. |
| **Policy Advisory** | Uncited generative text responses | Citation-Grounded RAG Pipeline (`src/retrieval.py`) | Restricts policy answers to ingested regulatory PDFs (`data/rag_docs/`). |
| **Model Validation** | Single-dataset train-test split | Three-Level Framework (Temporal, Group Holdout, Out-of-Domain) | Evaluates baseline performance across synthetic BDT logs and public invoice datasets. |

---

## 3. Evaluation Scope & Boundaries

To maintain technical honesty for competition evaluation:

- **Data Realities:** Our local currency validation uses simulated BDT transaction structures (`bangladesh_sme_cashflow.csv`) designed to test pipeline execution. Production deployment in Bangladesh requires real-time core banking or ERP API integration.
- **Out-of-Domain Transferability:** Our Level 3 external testing uses UK Barnet Council public invoices (`barnet_invoices.csv`) to test schema adaptability, acknowledging domain shift between public sector and private enterprise transactions.
