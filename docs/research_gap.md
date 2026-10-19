# FinMatrix Copilot — Problem Motivation and Research Gap

**Team Name:** FinMatrixDUO  
**Project Name:** FinMatrix Copilot  
**Competition:** Shenzhen FinTechathon 2026 — International Track  
**Theme:** AI as a Financial Participant

## 1. Background

Small and medium-sized businesses need to monitor income, expenses, outstanding payments, and available cash to make informed financial decisions.

However, financial information may be spread across spreadsheets, reports, and transaction records. Understanding these records and turning them into practical decisions can require time, financial knowledge, and repeated manual analysis.

AI-based assistants offer a potential way to make financial information easier to explore. Yet, a useful financial assistant needs more than natural-language responses. Its outputs should be connected to the underlying data, supported by appropriate calculations, and presented with clear limitations.

FinMatrix Copilot explores this approach through a Streamlit-based financial decision-support prototype.

## 2. The Problem We Address

The project focuses on three related challenges.

### 2.1 Understanding financial data

Users may need to review financial records before they can identify changes, inconsistencies, or potential cash-flow concerns. The usefulness of an assistant depends on whether it can process the available information correctly and present the results clearly.

### 2.2 Turning analysis into practical insights

Numerical results alone may not explain why a change matters or what a business should investigate next. Users need understandable explanations that remain consistent with the data and assumptions used in the analysis.

### 2.3 Maintaining reliability in AI-assisted decisions

Language models can produce convincing but incorrect answers. Financial applications therefore need to distinguish verified calculations from forecasts, retrieved information, and AI-generated explanations.

These challenges motivate our focus on combining financial analysis with accessible, AI-assisted interaction.

## 3. Research Gap

Existing spreadsheet tools, accounting platforms, financial dashboards, and AI assistants address different parts of the financial workflow. Their capabilities vary by product, configuration, and subscription.

The project is motivated by an integration question:

**How can a lightweight financial assistant combine structured financial analysis with AI-assisted explanations while making the source, assumptions, and limitations of its outputs understandable to the user?**

We explore this question through the following areas:

- Connecting supported financial calculations with natural-language interaction.
- Making financial outputs easier to interpret.
- Exploring document retrieval as a way to provide context for financial questions, where supported.
- Communicating uncertainty and limitations instead of treating every generated answer as verified.
- Designing a prototype that can be demonstrated and evaluated using defined financial scenarios.

These are the project's design objectives, not claims that existing commercial systems cannot perform these tasks.

## 4. Proposed Approach

FinMatrix Copilot is being developed as a Streamlit-based prototype with modular components for financial processing and AI-assisted functionality.

The intended approach is to:

1. Accept supported financial inputs.
2. Validate and normalize the available data.
3. Perform the financial operations supported by the implementation.
4. Use retrieval or language-model assistance where configured.
5. Present relevant outputs and explanations through the application interface.
6. Evaluate the behavior through defined test cases and documented limitations.

The actual capabilities available in the current version should be confirmed against the source code and test results.

## 5. What Makes the Approach Worth Exploring?

The project emphasizes the relationship between financial calculations and natural-language explanations rather than treating a chatbot as the complete solution.

Three design considerations guide the work:

**Calculation awareness:** Financial values should come from supported application logic where possible, rather than relying exclusively on language-model generation.

**Interpretability:** Users should be able to understand the information and assumptions behind an output.

**Responsible assistance:** AI-generated content should be treated as decision support, with uncertainty and limitations communicated appropriately.

The value of these design choices must be demonstrated through implementation and evaluation. They should not be interpreted as proof of superior accuracy, performance, or security without comparative evidence.

## 6. Evaluation Direction

To assess whether the approach is useful, future evaluation can focus on:

- Accuracy of supported financial calculations.
- Reliability of data validation and normalization.
- Relevance and factual consistency of AI-generated explanations.
- Quality of retrieved context, if retrieval is enabled.
- Handling of missing data and uncertain outcomes.
- Usability when completing representative financial tasks.

Where suitable datasets and baselines are available, comparative experiments can help determine whether the approach provides measurable benefits over simpler alternatives.

Any reported result should identify the dataset, evaluation procedure, baseline, and limitations. No performance improvement should be claimed without supporting evidence.

## 7. Limitations

FinMatrix Copilot is a prototype, not a validated financial advisory service.

Its usefulness depends on the quality of the input data, the reliability of implemented calculations, the configuration of optional AI services, and the evaluation evidence available.

The project does not claim that its approach is unique across the financial technology industry. A more specific novelty claim would require a systematic review of relevant research and existing products.

## 8. Conclusion

FinMatrix Copilot explores how structured financial analysis and AI-assisted explanations can work together in a lightweight financial decision-support application.

The central goal is to make financial information easier to understand without hiding the uncertainty and limitations of automated outputs.

For Team FinMatrixDUO, the next step is to demonstrate the value of this approach through a working prototype, transparent testing, and evidence-based evaluation.

**Team:** FinMatrixDUO  
**Project:** FinMatrix Copilot
