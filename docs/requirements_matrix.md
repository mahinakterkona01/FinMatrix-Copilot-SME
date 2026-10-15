# FinMatrix Copilot — Competition Problem Statement & Requirements Matrix

**Target Competition:** 2026 Shenzhen International FinTech Competition (FinTechathon 2026)  
**Track / Topic:** Topic E — SME Finance Copilot  
**Team:** Team FinMatrixDUO  

---

## 1. Core Problem Statement

Small and Medium Enterprises (SMEs) face critical operational hurdles:

1. **Volatile Cash-Flow Visibility:** Sudden liquidity drop-offs due to unpredictable revenue collection cycles.
2. **Invoice Late-Payment Risk:** Customer payment delays causing operational cash-burn.
3. **Policy Information Asymmetry:** Difficulty in discovering and qualifying for official government refinance funds and bank credit schemes.

---

## 2. Multi-Dataset Architecture & Scope

To address these challenges under strict validation rules, FinMatrix Copilot integrates multiple datasets:

| Dataset Name | Domain / Format | Primary Utility in FinMatrix Copilot |
| :--- | :--- | :--- |
| **UCI Online Retail II** | Real E-commerce Transactions | Task A: Cash-Flow Time-Series Forecasting |
| **UK Barnet Council Invoices** | Real Public Invoice Records | Task B: External Late-Payment Analysis & Working Capital Stress |
| **Central Bank SME Policy Corpus** | Official Circulars & Guidelines | Task C: RAG Policy Retrieval & Loan Matching |

---

## 3. Topic E Requirement Fulfillment Matrix

| Competition Topic E Core Requirement | FinMatrix Copilot Feature & Architecture | Implementation Status |
| :--- | :--- | :--- |
| **Financing-Option Matching** | RAG-powered Policy Search Engine (`src/retrieval.py`) & Working Capital Calculator | ✅ **Matched & Grounded** |
| **Cash-Flow Management with Alerts** | Ensembled ML Random Forest Forecaster (`src/forecasting.py`) & Safety Threshold Alerts | ✅ **Automated & Proactive** |
| **Business Financial Analysis** | Solvency Index Gauge, Multi-Sector Environment, and What-If Stress Simulator | ✅ **Enterprise Analytics** |
| **Security & System Safety** | Structural Injection & SQL Risk Guardrails (`src/safety.py`) | ✅ **Adversarial Safety** |
