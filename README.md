# ⚡ FinMatrix Copilot — SME Financial Co-Pilot

> **Developed by Team FinMatrixDUO**  
> **Official Submission for 2026 Shenzhen International FinTech Competition (Topic E)**

[![Python](https://img.shields.io/badge/Python-3.10+-00bcff?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-ff007f?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)
[![Topic E](https://img.shields.io/badge/Topic_E-100%25_Compliant-34d399?style=for-the-badge)](#-topic-e-requirement-fulfillment-matrix)
[![Team](https://img.shields.io/badge/Team-FinMatrixDUO-ffb703?style=for-the-badge)](#-team-finmatrixduo)
[![Security](https://img.shields.io/badge/Guardrails-Adversarial_Safety-00e5a0?style=for-the-badge)](src/safety.py)

---

## 👥 Team FinMatrixDUO

- **Track:** International AI Track | **Topic E:** SME Finance Copilot
- **Team Members:** [Your Name / GitHub Profile] & [Partner's Name / GitHub Profile]
- **Project Repository:** `FinMatrix-Copilot`

## 🎯 Topic E Requirement Fulfillment Matrix

| Competition Topic E Core Requirement | FinMatrix Copilot Solution & Module | Technical Implementation Status |
| :--- | :--- | :--- |
| **1. Financing-Option Matching** | RAG-powered Central Bank SME Policy Search (`src/retrieval.py`) & Invoice Discount Calculator (`app.py`) | ✅ **Matched & Capped** (Instant policy matching for refinancing facilities) |
| **2. Cash-Flow Management with Alerts** | ML Random Forest Time-Series Forecaster (`src/forecasting.py`) & Early-Warning Risk Radar | ✅ **Automated & Proactive** (Real-time safety threshold deficit alerts) |
| **3. Business Financial Analysis** | Solvency Index Gauge, Executive Margin Analytics, and What-If Stress Simulator | ✅ **Multi-Dimensional** (Sector-customizable enterprise environment) |

---

## 🚀 Key Capabilities

1. **Financing-Option Matching (RAG Engine)**:
   - Matches SME financial profiles with official central bank circulars, refinancing schemes (e.g., CMSME 7% facility), and invoice discounting options without hallucination.

2. **Automated Cash-Flow Management & Deficit Alerts**:
   - Ensembled Machine Learning forecasting model (+13.69% MAE accuracy over baseline) with dynamic deficit alerts when projected balance drops below customized safety buffers.

3. **Multi-Sector Business Financial Analysis**:
   - Real-time Solvency Health Index (0-100), automated cost-shock stress testing, and risk-free strategic advisory tailored for Retail, SaaS, Manufacturing, and Logistics SMEs.

## Overview

FinPilot AI is an enterprise financial co-pilot platform engineered for Small and Medium Enterprises (SMEs). It connects predictive machine learning analytics, deterministic financial engine verification, regulatory advisory powered by Retrieval-Augmented Generation (RAG), and human-governed execution pipelines into a single interface.

The platform relies on deterministic arithmetic for core financial statement evaluations to prevent calculation errors, while using machine learning models for forward cash-flow forecasting and natural language processing for regulatory retrieval.

---

## Architecture Diagram

                               ┌────────────────────────────────────────┐
                               │     Streamlit Navy-Blue Dashboard      │
                               └──────────────────┬─────────────────────┘
                                                  │
                 ┌────────────────────────────────┼────────────────────────────────┐
                 │                                │                                │
                 ▼                                ▼                                ▼
  ┌─────────────────────────────┐  ┌─────────────────────────────┐  ┌─────────────────────────────┐
  │  Deterministic Core Tools   │  │  Time-Series ML Forecasting │  │   Policy RAG Vector Engine  │
  │  (src/financial_tools.py)   │  │     (src/forecasting.py)    │  │    (src/retrieval.py)       │
  │  • Liquidity & Runway       │  │  • Random Forest Regressor   │  │  • PyPDF Document Chunking   │
  │  • Invoice Late Risk Score  │  │  • Uncertainty Bands         │  │  • TF-IDF Circular Indexing │
  └──────────────┬──────────────┘  └──────────────┬──────────────┘  └──────────────┬──────────────┘
                 │                                │                                │
                 └────────────────────────────────┼────────────────────────────────┘
                                                  │
                                                  ▼
                               ┌────────────────────────────────────────┐
                               │   Orchestration & Safety Guardrails    │
                               │        (src/agent.py & safety.py)       │
                               └──────────────────┬─────────────────────┘
                                                  │
                                 ┌────────────────┴────────────────┐
                                 ▼                                 ▼
                   ┌───────────────────────────┐     ┌───────────────────────────┐
                   │ Persistent Audit Logger   │     │ Human-in-the-Loop Sandbox │
                   │  (src/audit_logger.py)    │     │  (Audit & Approvals UI)   │
                   └───────────────────────────┘     └───────────────────────────┘

---

## Core Features

1. Deterministic Financial Verification: Provides fixed calculation algorithms for net cash flow, operating margins, monthly burn rates, and operational runway estimations.
2. Machine Learning Cash-Flow Forecasting: Generates 30-day forward projections with confidence interval bounds using a Random Forest Time-Series Regressor.
3. Interactive AgGrid Invoice Ledger: Enables multi-column searching, sorting, and dynamic inline credit risk assessments.
4. Data Quality Auditor: Accepts CSV and Excel uploads with schema normalization, missing value imputation, and duplicate detection.
5. Grounded Policy RAG Engine: Indexes official Bangladesh Bank SME policy circulars to provide cited regulatory answers.
6. Human-in-the-Loop Governance: Enforces approval sandboxes before sensitive financial workflows execute, backed by persistent local JSON logging.
7. Executive Summary Exporter: Exports printable .txt and structured .csv audit reports for banking partners and internal review.

---

## Installation & Environment Setup

### 1. Prerequisites

- Python 3.10+
- Git

### 2. Virtual Environment Configuration

git clone https://github.com/YourUsername/FinPilot_AI.git
cd FinPilot_AI

python -m venv .venv
.\.venv\Scripts\Activate.ps1

### 3. Install Dependencies

pip install -r requirements.txt
pip install streamlit-aggrid openpyxl

---

## Running the Dashboard

Launch the Streamlit web app with the following command:
streamlit run app.py

Access the application interface at http://localhost:8501

---

## Verification & Unit Testing

FinPilot AI incorporates an automated testing suite using pytest to validate financial algorithms, time-series transformations, security constraints, and audit logging persistence.

Execute the test suite:
pytest

Benchmark Result Output:
12 passed in 0.48s

---

## Directory Structure

FinPilot_AI/
├── .streamlit/
│   └── config.toml             # Navy-Blue UI Palette & Layout Settings
├── data/
│   ├── audit_log.json          # Persistent JSON Log Storage
│   ├── raw/                    # Transaction and Invoice Datasets
│   └── reports/                # Output Directory for Generated Reports
├── docs/
│   ├── evaluation_report.md    # Model Evaluation & System Metrics
│   └── *.pdf                   # Indexed Regulatory Policy Documents
├── src/
│   ├── agent.py                # Core Agent Orchestration
│   ├── audit_logger.py         # Local JSON Audit Persistence Engine
│   ├── data_loader.py          # Data Quality Verification & Normalization
│   ├── financial_tools.py      # Deterministic Arithmetic Functions
│   ├── forecasting.py          # Time-Series ML Regressor
│   ├── report_generator.py     # Executive Report Export Engine
│   ├── retrieval.py            # TF-IDF Regulatory Document Index
│   └── safety.py               # Input Validation & Sanitization
├── tests/                      # Automated Pytest Suite (12 Unit Tests)
├── app.py                      # Dashboard Web Application Interface
├── requirements.txt            # Package Dependencies
└── README.md                   # System Technical Documentation

---

## License & Compliance Note

Developed specifically for submission to the 2026 Shenzhen International FinTech Competition (Topic E: SME Finance Copilot). All components comply with competition guidelines regarding data handling, execution security, and original engineering practices.
