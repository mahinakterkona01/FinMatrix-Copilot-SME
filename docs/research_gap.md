# FinMatrix Copilot — Research Gap & Architectural Innovations

**Author/Team:** Team FinMatrixDUO  
**Competition:** 2026 Shenzhen International FinTech Competition (Topic E: SME Finance Copilot)  

---

## 1. Context & Existing Solution Gaps

When analyzing traditional SME financial software and generic conversational AI assistants, we identified three core structural gaps that our project, **FinMatrix Copilot**, addresses:

1. **Arithmetic & Forecast Instability:** Standard LLM wrappers tend to hallucinate numerical values during dynamic financial reasoning. We resolve this by decoupling raw math execution from the LLM and delegating arithmetic tasks to deterministic Python modules.
2. **Temporal Data Leakage in Forecasting:** Conventional ML code frequently splits time-series data at random, causing lookahead bias. We strictly enforce a chronological Level 1 Temporal Validation pipeline using historical-only lag features ($t-1$, $t-7$).
3. **Regulatory Citation Deficiency:** Generic financial assistants often issue advice without verifying underlying policy guidelines. We build a Retrieval-Augmented Generation (RAG) framework that grounds all policy queries directly in ingested central bank circulars with precise section citations.

---

## 2. Our System Innovations vs. Baseline Approaches

| Core Module | Standard Baseline | Our FinMatrix Copilot Implementation | Architectural Scope |
| :--- | :--- | :--- | :--- |
| **Numeric Calculation** | Generative LLM Reasoning | Deterministic Python Engines | Zero Arithmetic Hallucination |
| **Cash Flow Model** | Linear Lag Regression | Ensembled Random Forest Forecaster | +13.69% MAE Accuracy Gain |
| **Policy Search** | Keyword String Matching | Vectorized TF-IDF Cosine Retrieval | Grounded Regulatory Citations |
| **Input Security** | Unfiltered Text Inputs | Adversarial Structural Guardrails | Blocks SQL/Prompt Hijacking |
