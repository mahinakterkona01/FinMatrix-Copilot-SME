import os
import pandas as pd
import numpy as np
from src.forecasting import CashFlowForecaster
from src.safety import sanitize_text_input
from src.retrieval import PolicyRAGEngine

class AICopilotEngine:
    def __init__(self, data_df=None):
        self.df = data_df

    def get_suggested_queries(self):
        return [
            "What is our projected liquidity for the next 30 days?",
            "What is the CMSME refinancing loan limit and interest rate?",
            "How does a 15% operational cost shock affect our net cash flow?",
            "Are there any prompt injection or security threats detected?"
        ]

    def _generate_forecast(self, horizon=30):
        """Generate a forecast only when valid historical data is available."""
        if self.df is None or self.df.empty:
            return None, "No financial data is loaded."

        work = self.df.copy()

        if "trans_date" in work.columns:
            date_col = "trans_date"
        elif "date" in work.columns:
            date_col = "date"
        else:
            return None, "A transaction date column is required for forecasting."

        work[date_col] = pd.to_datetime(work[date_col], errors="coerce")
        work = work.dropna(subset=[date_col]).copy()

        if "net_flow" not in work.columns:
            if {"inflow", "outflow"}.issubset(work.columns):
                work["net_flow"] = (
                    pd.to_numeric(work["inflow"], errors="coerce")
                    - pd.to_numeric(work["outflow"], errors="coerce")
                )
            else:
                return None, "Data must contain net_flow or both inflow and outflow."

        work["net_flow"] = pd.to_numeric(work["net_flow"], errors="coerce")
        work = work.dropna(subset=["net_flow"])
        work = work[
            work["net_flow"].map(lambda value: pd.notna(value) and abs(value) != float("inf"))
        ]
        work = work.sort_values(date_col)

        if len(work) < 14:
            return None, "At least 14 valid historical records are required."

        # Aggregate transactions by date so the model receives daily cash flow.
        daily = (
            work.groupby(date_col, as_index=False)["net_flow"]
            .sum()
            .sort_values(date_col)
        )
        daily = daily.rename(columns={date_col: "trans_date"})

        if len(daily) < 14:
            return None, "At least 14 distinct dates are required for forecasting."

        try:
            model = CashFlowForecaster()
            predictions = model.predict_next_days(df=daily, days=horizon)

            if (
                not isinstance(predictions, pd.DataFrame)
                or predictions.empty
                or "Predicted_Net_Flow" not in predictions.columns
            ):
                return None, "The forecasting model returned no usable predictions."

            values = pd.to_numeric(
                predictions["Predicted_Net_Flow"], errors="coerce"
            )
            values = values[values.map(
                lambda value: pd.notna(value) and abs(value) != float("inf")
            )]

            if values.empty:
                return None, "The model returned no valid numeric predictions."

            return {
                "forecast_days": len(values),
                "forecast_net_flow": float(values.sum()),
                "average_daily_net_flow": float(values.mean()),
                "last_historical_date": daily["trans_date"].max().date().isoformat(),
            }, None
        except Exception:
            return None, "Forecast generation failed due to an internal error."

    def process_query(self, query_text):
        sanitized_query, is_threat, triggered_rules = sanitize_text_input(query_text)

        if is_threat:
            return {
                "answer": (
                    "I can't process this request because it matches a potential "
                    "prompt-injection pattern. Please rephrase it as a normal "
                    "financial question."
                ),
                "intent": "Security Guardrail",
                "confidence": None,
                "security": {
                    "blocked": True,
                    "triggered_rules": triggered_rules,
                },
            }

        query_lower = sanitized_query.lower()

        # Explicit cost-shock routing precedes broad cash-flow matching.
        cost_shock_request = (
            any(w in query_lower for w in ("shock", "stress"))
            and any(w in query_lower for w in ("cost", "expense", "operational"))
        )
        if cost_shock_request:
            import re

            match = re.search(r"(\d+(?:\.\d+)?)\s*%", sanitized_query)
            try:
                if match is None:
                    raise ValueError("Missing percentage")
                shock_pct = float(match.group(1))
                if not 0 <= shock_pct <= 500:
                    raise ValueError("Percentage out of range")
                if (
                    self.df is None
                    or self.df.empty
                    or not {"inflow", "outflow"}.issubset(self.df.columns)
                ):
                    raise ValueError("Required columns unavailable")

                work = self.df[["inflow", "outflow"]].copy()
                for col in ("inflow", "outflow"):
                    work[col] = pd.to_numeric(work[col], errors="coerce")
                work = work.replace([np.inf, -np.inf], np.nan).dropna()
                work = work[
                    (work["inflow"] >= 0) & (work["outflow"] >= 0)
                ]
                if work.empty:
                    raise ValueError("No valid records")

                inflow = float(work["inflow"].sum())
                outflow = float(work["outflow"].sum())
                if not np.isfinite(inflow) or not np.isfinite(outflow):
                    raise ValueError("Invalid totals")

                baseline = inflow - outflow
                extra_cost = outflow * shock_pct / 100.0
                scenario_net = baseline - extra_cost

                return {
                    "answer": (
                        f"Deterministic cost-shock calculation using {len(work)} "
                        f"valid uploaded record(s): total inflow = {inflow:,.2f}; "
                        f"baseline outflow = {outflow:,.2f}; baseline net flow = "
                        f"{baseline:,.2f}. A {shock_pct:g}% increase in recorded "
                        f"outflows adds {extra_cost:,.2f}, resulting in scenario "
                        f"net flow of {scenario_net:,.2f}. Currency is unspecified. "
                        "This is a what-if calculation on uploaded records, not a "
                        "forecast; it assumes inflows stay unchanged and does not "
                        "model timing or behavioral changes."
                    ),
                    "intent": "Risk & Stress Simulation",
                    "confidence": None,
                    "stress_scenario": {
                        "valid_records": len(work),
                        "shock_percent": shock_pct,
                        "total_inflow": inflow,
                        "baseline_outflow": outflow,
                        "baseline_net_flow": baseline,
                        "additional_cost": extra_cost,
                        "scenario_net_flow": scenario_net,
                        "currency": None,
                    },
                }
            except (ValueError, TypeError, OverflowError):
                return {
                    "answer": (
                        "I cannot calculate this cost-shock scenario from the "
                        "current data. Provide a percentage from 0% to 500% and "
                        "valid non-negative inflow and outflow columns. No impact "
                        "estimate has been assumed."
                    ),
                    "intent": "Risk & Stress Simulation",
                    "confidence": None,
                }

        # Intent 1: Cash Flow & Liquidity
        elif any(w in query_lower for w in [
            "liquidity", "cash flow", "forecast", "projection", "balance"
        ]):
            forecast, error = self._generate_forecast(horizon=30)

            if forecast is None:
                return {
                    "answer": (
                        "I cannot provide a reliable liquidity forecast yet. "
                        + error
                        + " Please check the uploaded data and try again."
                    ),
                    "intent": "Forecasting & Cash Flow",
                    "confidence": None,
                }

            net_flow = forecast["forecast_net_flow"]
            direction = (
                "positive cumulative net flow"
                if net_flow >= 0
                else "negative cumulative net flow"
            )

            return {
                "answer": (
                    f"The configured forecasting model generated "
                    f"{forecast['forecast_days']} daily predictions, based on "
                    f"historical data through {forecast['last_historical_date']}. "
                    f"The sum of predicted daily net flows is "
                    f"{net_flow:,.2f} in the dataset's unspecified currency "
                    f"({direction}). The average predicted daily net flow is "
                    f"{forecast['average_daily_net_flow']:,.2f}. "
                    "These are model estimates, not guaranteed outcomes; "
                    "forecast accuracy has not been established by this response."
                ),
                "intent": "Forecasting & Cash Flow",
                "confidence": None,
                "forecast": forecast,
            }

        # Intent 2: Regulatory Policy retrieval with explicit evidence limits.
        elif any(w in query_lower for w in [
            "policy", "refinancing", "loan", "cmsme", "rate", "circular"
        ]):
            try:
                rag = getattr(self, "rag_engine", None)
                if rag is None:
                    rag = PolicyRAGEngine()
                    self.rag_engine = rag
                retrieved = rag.query_policy(sanitized_query, top_k=2)
            except Exception:
                retrieved = []

            if not retrieved:
                return {
                    "answer": (
                        "I could not find a relevant excerpt in the configured "
                        "local policy knowledge base. I cannot confirm the "
                        "current CMSME loan limit or interest rate. Consult the "
                        "applicable Bangladesh Bank circular and verify its "
                        "effective date and later amendments."
                    ),
                    "intent": "Regulatory Policy RAG",
                    "confidence": None,
                    "policy_evidence": [],
                }

            evidence_lines = []
            evidence = []
            for item in retrieved:
                source = str(item.get("source") or "Source unavailable")
                section = str(item.get("section") or "Section unavailable")
                excerpt = str(item.get("text") or "").strip()
                if not excerpt:
                    continue
                evidence.append({
                    "source": source,
                    "section": section,
                    "excerpt": excerpt,
                    "relevance_score": item.get("relevance_score"),
                    "effective_date": item.get("effective_date"),
                })
                evidence_lines.append(
                    f"[{source} | {section}] {excerpt}"
                )

            if not evidence:
                return {
                    "answer": (
                        "The local retrieval system returned no usable policy "
                        "excerpts. I cannot confirm the requested policy details."
                    ),
                    "intent": "Regulatory Policy RAG",
                    "confidence": None,
                    "policy_evidence": [],
                }

            answer = (
                "I cannot confirm the current CMSME loan limit or interest rate from these retrieved excerpts. I found the following excerpts in FinMatrix's local policy "
                "knowledge base. Retrieval relevance does not establish that a "
                "document is official, current, or legally applicable. Verify "
                "the original circular, effective date, and amendments before "
                "making a financial decision.\n\n"
                + "\n\n".join(evidence_lines)
            )
            return {
                "answer": answer,
                "intent": "Regulatory Policy RAG",
                "confidence": None,
                "policy_evidence": evidence,
            }

        # Intent 3: Risk & Stress Testing
        elif any(w in query_lower for w in [
            "shock", "stress", "cost", "risk", "delay"
        ]):
            return {
                "answer": (
                    "I cannot quantify this stress scenario yet because a "
                    "validated stress-test calculation is not configured. "
                    "No impact estimate has been calculated."
                ),
                "intent": "Risk & Stress Simulation",
                "confidence": None,
            }

        # Fallback General Assistant Response
        return {
            "answer": (
                "I am your FinMatrix AI Copilot. I can help analyze cash-flow "
                "forecasts and search for policy evidence when a verified "
                "retrieval source is configured. Stress-test calculations and "
                "security audits are not automatically performed by this reply."
            ),
            "intent": "General Assistance",
            "confidence": None,
        }
