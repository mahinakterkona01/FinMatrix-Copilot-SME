# FinPilot AI — Competition Problem Statement & Requirements Matrix

**Target Competition:** 2026 Shenzhen International FinTech Competition (FinTechathon 2026)
**Track / Topic:** Topic E — SME Finance Copilot

---

## 1. Core Problem Statement

Small and Medium Enterprises (SMEs) face critical operational hurdles:

1. **Volatile Cash-Flow Visibility:** Sudden liquidity drop-offs due to unpredictable revenue collection cycles.
2. **Invoice Late-Payment Risk:** Customer payment delays causing operational cash-burn.
3. **Policy Information Asymmetry:** Difficulty in discovering and qualifying for official government refinance funds and bank credit schemes.

---

## 2. Multi-Dataset Architecture & Scope

To address these challenges under strict validation rules, FinPilot AI integrates multiple datasets:

| Dataset Name | Domain / Format | Primary Utility in FinPilot AI |
| :--- | :--- | :--- |
| **UCI Online Retail II** | Real E-commerce Transactions | Task A: Cash-Flow Time-Series Forecasting |
| **UK Barnet Council Invoices** | Real Public Invoice Records | Task B: External Late-Payment Model Validation |
| **Bangladesh SME Synthetic** | Simulated Local BDT Records | Local Currency Testbed & Dashboard Demonstration |
| **Bangladesh Bank Circulars** | Official Policy PDFs | RAG Engine Grounded Knowledge Base |

---

## 3. Strict 3-Level Validation Safeguards

- **Level 1 (Temporal Validation):** Enforce strict chronological train-test splits on historical lags ($t-1$, $t-7$) to eliminate lookahead bias.
- **Level 2 (Business Holdout):** Cross-validate model generalization on unseen SME customer groups.
- **Level 3 (External Benchmark):** Test frozen models on out-of-domain public invoice records.
