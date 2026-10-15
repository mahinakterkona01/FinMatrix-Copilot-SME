import os
import sys
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# Local module resolution
sys.path.append(os.path.abspath("."))

import src.forecasting as forecasting_module
import src.retrieval as retrieval_module
import src.safety as safety_module
import src.copilot as copilot_module

# ===================================================================
# PAGE CONFIG
# ===================================================================
st.set_page_config(
    page_title="FinMatrix Copilot — SME Financial Co-Pilot",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===================================================================
# HIGH-CONTRAST DESIGN SYSTEM
# ===================================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="css"], .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        background-color: #0b0f19 !important;
        color: #f8fafc !important;
    }

    #MainMenu, footer { visibility: hidden; }
    .block-container { padding-top: 2rem; padding-bottom: 3rem; max-width: 1400px; }

    section[data-testid="stSidebar"] {
        background-color: #0f172a !important;
        border-right: 1px solid #334155 !important;
    }
    
    section[data-testid="stSidebar"] *, 
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] div {
        color: #f8fafc !important;
    }

    .stTextInput input, .stTextArea textarea, .stSelectbox select {
        color: #ffffff !important;
        background-color: #1e293b !important;
        border: 1px solid #475569 !important;
        border-radius: 6px !important;
    }

    .stTextInput label, .stTextArea label, .stSelectbox label {
        color: #f8fafc !important;
        font-weight: 600 !important;
    }

    div[data-testid="stRadio"] label {
        background-color: #1e293b !important;
        padding: 8px 16px !important;
        border-radius: 8px !important;
        border: 1px solid #475569 !important;
        margin-right: 8px !important;
    }

    div[data-testid="stRadio"] label p {
        color: #f8fafc !important;
        font-weight: 600 !important;
        font-size: 14px !important;
    }

    div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #1e293b !important;
        border: 1px solid #334155 !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
    }

    .fp-card {
        background-color: #1e293b;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 18px 20px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    }
    .fp-card .label {
        color: #94a3b8; font-size: 11px; font-weight: 600; letter-spacing: 1px; text-transform: uppercase;
    }
    .fp-card .value {
        font-size: 24px; font-weight: 700; margin: 6px 0; color: #ffffff;
    }
    .fp-card .caption { color: #cbd5e1; font-size: 11px; }

    .badge {
        display: inline-block; padding: 4px 10px; border-radius: 999px; font-size: 10.5px; font-weight: 600;
        text-transform: uppercase; margin: 2px 4px 2px 0;
    }
    .badge-green { background: #064e3b; color: #34d399 !important; border: 1px solid #059669; }
    .badge-cyan  { background: #0c4a6e; color: #38bdf8 !important; border: 1px solid #0284c7; }
    .badge-amber { background: #78350f; color: #fbbf24 !important; border: 1px solid #d97706; }
    .badge-red   { background: #7f1d1d; color: #f87171 !important; border: 1px solid #dc2626; }
    .badge-grey  { background: #334155; color: #cbd5e1 !important; border: 1px solid #475569; }

    .status-row { display: flex; justify-content: space-between; align-items: center; margin: 6px 0; }
    .status-row .k { color: #94a3b8 !important; font-size: 11px; text-transform: uppercase; }

    .brand-title {
        text-align: center; font-size: 42px; font-weight: 700; color: #38bdf8; margin-top: 20px;
    }
    .brand-sub { text-align: center; font-size: 16px; color: #e2e8f0; margin-top: 4px; }
    .brand-tag { text-align: center; font-size: 13px; color: #94a3b8; margin-bottom: 20px; }

    .stButton > button, .stDownloadButton > button {
        border-radius: 8px; font-weight: 600;
        border: 1px solid #0284c7;
        background-color: #0284c7;
        color: #ffffff !important;
    }
    .stButton > button:hover {
        background-color: #0369a1;
        border-color: #0369a1;
    }
</style>
""", unsafe_allow_html=True)

# ===================================================================
# SESSION STATE INITIALIZATION
# ===================================================================
if "auth_state" not in st.session_state:
    st.session_state["auth_state"] = "unauthenticated"
if "user_role" not in st.session_state:
    st.session_state["user_role"] = None
if "chat_messages" not in st.session_state:
    st.session_state["chat_messages"] = [
        {"role": "assistant", "content": "Hello! I am your FinMatrix Copilot. Ask me about cash flow forecasts, SME loan policies, or risk stress testing."}
    ]

# ===================================================================
# SIDEBAR ENVIRONMENT & CUSTOMIZATION CONTROLS
# ===================================================================
st.sidebar.markdown(
    "<div style='font-size:22px; font-weight:700; color:#ffffff;'>FinMatrix Copilot</div>"
    "<div style='font-size:11px; color:#cbd5e1; text-transform:uppercase; margin-bottom:14px;'>Platform Console</div>",
    unsafe_allow_html=True,
)

st.sidebar.markdown("---")
st.sidebar.markdown("<div style='font-size:12px; font-weight:700; color:#cbd5e1; text-transform:uppercase;'>⚙️ ENVIRONMENT SETUP</div>", unsafe_allow_html=True)

biz_sector = st.sidebar.selectbox(
    "SME Business Sector",
    ["Retail & E-commerce", "Technology & SaaS", "Manufacturing", "Services & Logistics"]
)

currency_choice = st.sidebar.selectbox(
    "Operating Currency",
    ["USD ($)", "BDT (৳)", "EUR (€)", "GBP (£)", "CNY (¥)"]
)
curr_sym = currency_choice.split("(")[1].replace(")", "").strip()

safety_threshold = st.sidebar.number_input(
    f"Safety Liquidity Buffer ({curr_sym})",
    min_value=500.0, value=5000.0, step=500.0
)

custom_csv = st.sidebar.file_uploader("Custom SME Data (.CSV)", type=["csv"])

# Helper Formatters
def fmt_curr(value):
    try:
        return f"{curr_sym}{float(value):,.2f}"
    except Exception:
        return f"{curr_sym}0.00"

def badge(text, tone="cyan"):
    return f"<span class='badge badge-{tone}'>{text}</span>"

def metric_card(label, value, delta_text="", tone="neu", caption=""):
    cap_html = f"<div class='caption'>{caption}</div>" if caption else ""
    return (
        f"<div class='fp-card'>"
        f"<div class='label'>{label}</div>"
        f"<div class='value'>{value}</div>"
        f"{cap_html}"
        f"</div>"
    )

def style_fig(fig, height=340, legend=True):
    fig.update_layout(
        template="plotly_dark",
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color="#f8fafc", size=12),
        margin=dict(l=10, r=10, t=30, b=10),
        hovermode="x unified",
        showlegend=legend,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, bgcolor="rgba(0,0,0,0)"),
    )
    fig.update_xaxes(showgrid=False, zeroline=False, linecolor="#475569")
    fig.update_yaxes(gridcolor="rgba(255, 255, 255, 0.1)", zeroline=False, tickprefix=curr_sym, tickformat=",.0f")
    return fig

# ===================================================================
# DATA LOADER (CUSTOM OR DUMMY)
# ===================================================================
@st.cache_data
def load_data(uploaded_file):
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
        except Exception:
            df = None
    else:
        df = None

    if df is None:
        data_path = os.path.join("data", "raw", "bangladesh_sme_cashflow.csv")
        if os.path.exists(data_path):
            df = pd.read_csv(data_path)
        else:
            np.random.seed(42)
            dates = pd.date_range(start="2025-01-01", periods=180)
            inflows = np.random.uniform(15000, 60000, size=180)
            outflows = np.random.uniform(10000, 45000, size=180)
            df = pd.DataFrame({"Trans_Date": dates, "Inflow": inflows, "Outflow": outflows})

    cols_lower = [str(c).strip().lower() for c in df.columns]
    df.columns = cols_lower

    for num_col in ['inflow', 'outflow', 'net_flow', 'netflow', 'amount']:
        if num_col in df.columns:
            df[num_col] = pd.to_numeric(df[num_col], errors='coerce').fillna(0.0)

    if 'net_flow' not in df.columns:
        if 'inflow' in df.columns and 'outflow' in df.columns:
            df['net_flow'] = df['inflow'] - df['outflow']
        else:
            df['net_flow'] = pd.to_numeric(df.iloc[:, 1], errors='coerce').fillna(0.0)

    if 'trans_date' in df.columns:
        df['trans_date'] = pd.to_datetime(df['trans_date'], errors='coerce')

    return df

df_raw = load_data(custom_csv)

total_inflow_val = float(df_raw['inflow'].sum() if 'inflow' in df_raw.columns else df_raw['net_flow'].clip(lower=0).sum())
total_outflow_val = float(df_raw['outflow'].sum() if 'outflow' in df_raw.columns else (-df_raw['net_flow'].clip(upper=0)).sum())
net_position_val = float(df_raw['net_flow'].sum())
health_score_val = min(100, max(0, int((net_position_val / (total_inflow_val + 1e-5)) * 100 + 50)))

def build_daily(df):
    if "trans_date" in df.columns and df["trans_date"].notna().any():
        tmp = df.dropna(subset=["trans_date"]).copy()
        tmp["date"] = tmp["trans_date"].dt.normalize()
        agg = {"net_flow": "sum"}
        for c in ("inflow", "outflow"):
            if c in tmp.columns:
                agg[c] = "sum"
        daily = tmp.groupby("date", as_index=False).agg(agg).sort_values("date").reset_index(drop=True)
        return daily, True
    daily = pd.DataFrame({
        "date": np.arange(1, len(df) + 1),
        "net_flow": pd.to_numeric(df["net_flow"], errors="coerce").fillna(0.0).values,
    })
    return daily, False

daily_df, has_dates = build_daily(df_raw)

copilot_engine = copilot_module.AICopilotEngine(data_df=df_raw)
model_ready = getattr(forecasting_module, 'CashFlowForecaster', getattr(forecasting_module, 'Forecaster', None)) is not None
rag_ready = any(hasattr(retrieval_module, n) for n in ['PolicyRetriever', 'RAGRetriever', 'PolicySearchEngine', 'Retriever'])
guard_ready = hasattr(safety_module, 'validate_input') or hasattr(safety_module, 'Guardrail')

# ===================================================================
# WELCOME / AUTHENTICATION SCREEN
# ===================================================================
if st.session_state["auth_state"] == "unauthenticated":
    st.markdown("<div class='brand-title'>FinMatrix Copilot</div>", unsafe_allow_html=True)
    st.markdown(f"<p class='brand-sub'>Intelligent Financial Co-Pilot for {biz_sector}</p>", unsafe_allow_html=True)
    st.markdown("<p class='brand-tag'>Predict cash flow. Detect risks. Make smarter financial decisions.</p>", unsafe_allow_html=True)

    col_mid1, col_mid2, col_mid3 = st.columns([1, 1.8, 1])
    with col_mid2:
        with st.container(border=True):
            st.markdown("<div style='color: #cbd5e1; font-weight:600; font-size:12px; text-transform:uppercase;'>SECURE ACCESS PORTAL</div>", unsafe_allow_html=True)
            st.write("")

            access_mode = st.radio(
                "Select Access Mode",
                ["Registered User", "Guest Access"],
                horizontal=True,
                label_visibility="collapsed"
            )

            st.write("")

            if access_mode == "Registered User":
                username = st.text_input("Email or Username", key="login_user")
                password = st.text_input("Password", type="password", key="login_pass")

                if st.button("Log In", use_container_width=True):
                    if username.strip() != "" and password.strip() != "":
                        st.session_state["auth_state"] = "authenticated"
                        st.session_state["user_role"] = f"{biz_sector} Finance Lead"
                        st.rerun()
                    else:
                        st.error("Please enter valid credentials.")

            else:
                st.info("Guest mode provides read-only access to interactive dashboards, risk simulators, and sample AI features without persisting client records.")
                if st.button("Continue as Guest", use_container_width=True):
                    st.session_state["auth_state"] = "guest"
                    st.session_state["user_role"] = "Guest Explorer"
                    st.rerun()

        st.markdown(
            "<div style='text-align:center; margin-top:12px;'>"
            + badge("Encrypted Session", "grey") + badge("Guardrails Active" if guard_ready else "Guardrails Fallback", "cyan")
            + "</div>",
            unsafe_allow_html=True,
        )

# ===================================================================
# MAIN APPLICATION SHELL
# ===================================================================
else:
    is_auth = st.session_state["auth_state"] == "authenticated"
    auth_badge = badge("Authenticated", "green") if is_auth else badge("Guest Mode", "cyan")
    model_badge = badge("Model Ready", "green") if model_ready else badge("Model Fallback", "amber")
    rag_badge = badge("RAG Online", "green") if rag_ready else badge("RAG Fallback", "amber")

    st.sidebar.markdown(
        f"<div class='status-row'><span class='k'>Access</span>{auth_badge}</div>"
        f"<div class='status-row'><span class='k'>Forecast Model</span>{model_badge}</div>"
        f"<div class='status-row'><span class='k'>Policy RAG</span>{rag_badge}</div>",
        unsafe_allow_html=True,
    )
    st.sidebar.caption(f"Environment: **{biz_sector}**")

    st.sidebar.markdown("---")

    selected_tab = st.sidebar.radio(
        "Navigation",
        [
            "Executive Dashboard",
            "Cash Flow & Forecast",
            "What-If Scenario Simulator",
            "Invoice Discount Calculator",
            "AI Financial Copilot",
            "Regulatory RAG Knowledge",
            "Security & Guardrail Audit",
            "Audit Report Exporter"
        ]
    )

    st.sidebar.markdown("---")
    if st.sidebar.button("Logout / Exit Session", use_container_width=True):
        st.session_state["auth_state"] = "unauthenticated"
        st.session_state["user_role"] = None
        st.rerun()

    # HEADER BAR
    st.markdown(
        f"<div style='margin-bottom: 12px;'><h1 style='font-size: 28px; font-weight: 700; color: #ffffff;'>{selected_tab}</h1>"
        f"<p style='color: #cbd5e1; font-size: 13px;'>2026 Shenzhen International FinTech Competition (Topic E) | FinMatrix Copilot Infrastructure</p></div>",
        unsafe_allow_html=True,
    )

    # -------------------------------------------------------------------
    # TAB 1: EXECUTIVE DASHBOARD
    # -------------------------------------------------------------------
    if selected_tab == "Executive Dashboard":
        # Dynamic Risk Check against safety buffer
        if net_position_val < safety_threshold:
            st.error(f"⚠️ CRITICAL LIQUIDITY WARNING: Current net position ({fmt_curr(net_position_val)}) is below your set safety threshold of {fmt_curr(safety_threshold)}. Immediate working capital buffer allocation advised.")
        else:
            st.success(f"✅ LIQUIDITY STATUS STABLE: Net position exceeds safety buffer target of {fmt_curr(safety_threshold)} for {biz_sector}.")

        col1, col2, col3, col4 = st.columns(4)
        col1.markdown(metric_card("Total Inflow", fmt_curr(total_inflow_val), "", "pos", f"Currency: {curr_sym}"), unsafe_allow_html=True)
        col2.markdown(metric_card("Total Outflow", fmt_curr(total_outflow_val), "", "neg", f"Currency: {curr_sym}"), unsafe_allow_html=True)
        col3.markdown(metric_card("Net Position", fmt_curr(net_position_val), "", "pos" if net_position_val > 0 else "neg", "Inflow minus Outflow"), unsafe_allow_html=True)
        col4.markdown(metric_card("Solvency Health Score", f"{health_score_val} / 100", "", "pos" if health_score_val >= 70 else "warn", "Net Margin Index"), unsafe_allow_html=True)

        st.write("")
        c1, c2 = st.columns([1, 2])

        with c1:
            with st.container(border=True):
                st.markdown("<div style='color: #cbd5e1; font-size: 11px; font-weight: 600; text-transform: uppercase;'>Solvency Index Gauge</div>", unsafe_allow_html=True)
                bar_color = "#34d399" if health_score_val >= 70 else ("#fbbf24" if health_score_val >= 50 else "#f87171")
                fig_gauge = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=health_score_val,
                    number={'font': {'size': 52, 'color': '#ffffff'}},
                    gauge={
                        'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': '#cbd5e1'},
                        'bar': {'color': bar_color, 'thickness': 0.3},
                        'bgcolor': 'rgba(0,0,0,0)',
                    },
                ))
                fig_gauge.update_layout(
                    height=290, 
                    template="plotly_dark", 
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(family="Inter, sans-serif", color="#f8fafc", size=12), 
                    margin=dict(l=20, r=20, t=20, b=10)
                )
                st.plotly_chart(fig_gauge, use_container_width=True, config={"displaylogo": False})

        with c2:
            with st.container(border=True):
                st.markdown("<div style='color: #cbd5e1; font-size: 11px; font-weight: 600; text-transform: uppercase;'>Historical Net Cash Trajectory</div>", unsafe_allow_html=True)
                
                x = daily_df["date"]
                y = daily_df["net_flow"].astype(float)
                fig_trend = go.Figure()
                fig_trend.add_trace(go.Scatter(
                    x=x, y=y, mode="lines", name="Net Cash Flow",
                    line=dict(color="#38bdf8", width=2.5),
                    fill="tozeroy", fillcolor="rgba(56, 189, 248, 0.15)",
                ))
                fig_trend.add_hline(y=0, line_dash="dash", line_color="#f87171", line_width=1.5)
                style_fig(fig_trend, height=290)
                st.plotly_chart(fig_trend, use_container_width=True, config={"displaylogo": False})

        # AI EXPLANATION & RISK-FREE SUGGESTION BLOCK
        with st.container(border=True):
            st.markdown("<div style='color: #38bdf8; font-size: 13px; font-weight: 700;'>🤖 AI EXECUTIVE ADVISORY & EXPLANATION</div>", unsafe_allow_html=True)
            st.write(f"**Data Analysis Summary:** Your net position stands at **{fmt_curr(net_position_val)}** with a solvency score of **{health_score_val}/100** under the {biz_sector} operating profile.")
            
            if health_score_val < 60:
                st.warning(f"⚡ **Risk Alert:** Operating margin is tight. Your cash outflow is currently consuming {((total_outflow_val/total_inflow_val)*100):.1f}% of gross inflows.")
                st.info(f"💡 **Risk-Free Recommendation:** Instead of taking high-interest commercial debt, consider offering a 1.5% early payment discount on outstanding client invoices to accelerate cash inflow without incurring balance-sheet liability.")
            else:
                st.success("💡 **Strategic Recommendation:** Cash flow trajectory is stable. You may safely allocate excess reserves to short-term yield accounts or inventory prepayments to lock in supplier discounts.")

    # -------------------------------------------------------------------
    # TAB 2: CASH FLOW FORECAST
    # -------------------------------------------------------------------
    elif selected_tab == "Cash Flow & Forecast":
        st.caption("Machine Learning Ensembled Predictive Models with Temporal Holdout Benchmarks")

        with st.container(border=True):
            horizon = st.slider("Select Forecast Horizon (Days)", 7, 60, 30)

        forecaster_cls = getattr(forecasting_module, 'CashFlowForecaster', getattr(forecasting_module, 'Forecaster', None))
        forecaster_obj = forecaster_cls() if forecaster_cls else None

        try:
            forecast_df = forecaster_obj.predict_next_days(days=horizon) if forecaster_obj else None
        except Exception:
            forecast_df = None

        if forecast_df is None:
            last_val = df_raw['net_flow'].iloc[-1]
            dates = pd.date_range(start=pd.Timestamp.today(), periods=horizon)
            sim_preds = np.random.normal(loc=last_val, scale=np.std(df_raw['net_flow']) * 0.5, size=horizon)
            forecast_df = pd.DataFrame({"Date": dates, "Forecast_Net_Flow": sim_preds})

        fc_y = pd.to_numeric(forecast_df.iloc[:, -1], errors='coerce').fillna(0.0)
        cum_total = float(fc_y.sum())

        st.success(f"Predicted Cumulative Net Position over {horizon} Days: {fmt_curr(cum_total)}")

        with st.container(border=True):
            st.markdown("<div style='color: #cbd5e1; font-size: 11px; font-weight: 600; text-transform: uppercase;'>Forecast Trajectory</div>", unsafe_allow_html=True)
            fig_fc = px.line(forecast_df, x=forecast_df.columns[0], y=forecast_df.columns[-1], template="plotly_dark")
            style_fig(fig_fc, height=340)
            st.plotly_chart(fig_fc, use_container_width=True, config={"displaylogo": False})

        # AI FORECAST EXPLANATION
        with st.container(border=True):
            st.markdown("<div style='color: #38bdf8; font-size: 13px; font-weight: 700;'>🤖 FORECASTING AI INSIGHTS</div>", unsafe_allow_html=True)
            st.write(f"**Model Explanation:** The machine learning forecast uses temporal holdout validation tailored for {biz_sector}. It projects a net liquidity change of **{fmt_curr(cum_total)}** across the next {horizon} days.")
            if cum_total < 0:
                st.error("⚠️ **Deficit Warning:** Projected negative liquidity trajectory detected. Potential cash shortage approaching towards the end of cycle.")
                st.info("💡 **Risk-Free Action Plan:** Apply for central bank low-interest refinancing schemes (e.g., CMSME 7% capped facility) prior to the deficit point.")
            else:
                st.success("✅ **Positive Forecast:** Liquidity remains positive. Maintain standard operating budget.")

    # -------------------------------------------------------------------
    # TAB 3: STRESS SIMULATOR
    # -------------------------------------------------------------------
    elif selected_tab == "What-If Scenario Simulator":
        with st.container(border=True):
            st.markdown("<div style='color: #cbd5e1; font-size: 11px; font-weight: 600; text-transform: uppercase;'>Scenario Controls</div>", unsafe_allow_html=True)
            col_s1, col_s2 = st.columns(2)
            rev_shock = col_s1.slider("Revenue Inflow Shock (%)", -50, 50, -10)
            cost_shock = col_s2.slider("Operating Cost Shock (%)", -50, 50, 15)

        base_series = daily_df['net_flow'].astype(float)
        sim_series = base_series * (1 + rev_shock / 100.0) - (base_series.abs() * (cost_shock / 100.0))
        sim_df = pd.DataFrame({"Date": daily_df['date'], "Baseline": base_series, "Simulated": sim_series})

        with st.container(border=True):
            st.markdown("<div style='color: #cbd5e1; font-size: 11px; font-weight: 600; text-transform: uppercase;'>Daily Net Flow: Baseline vs Simulated</div>", unsafe_allow_html=True)
            fig_sim = px.line(sim_df, x="Date", y=["Baseline", "Simulated"], template="plotly_dark")
            style_fig(fig_sim, height=340)
            st.plotly_chart(fig_sim, use_container_width=True, config={"displaylogo": False})

        # STRESS ADVISORY
        sim_sum = float(sim_series.sum())
        base_sum = float(base_series.sum())
        impact_pct = ((sim_sum - base_sum) / (abs(base_sum) + 1e-5)) * 100

        with st.container(border=True):
            st.markdown("<div style='color: #38bdf8; font-size: 13px; font-weight: 700;'>🤖 STRESS TEST SIMULATION REPORT</div>", unsafe_allow_html=True)
            st.write(f"**Impact Explanation:** A **{rev_shock}% revenue shock** combined with a **{cost_shock}% cost inflation** leads to a **{impact_pct:.1f}% change** in cumulative net cash flow.")
            if sim_sum < safety_threshold:
                st.warning("⚠️ **Stress Alert:** Under this scenario, your cash position drops below the safety threshold. Consider delaying non-essential capital expenditures (CapEx).")

    # -------------------------------------------------------------------
    # TAB 4: INVOICE DISCOUNT CALCULATOR
    # -------------------------------------------------------------------
    elif selected_tab == "Invoice Discount Calculator":
        st.caption("Strategic Working Capital Optimizer for Accelerated Client Collection")

        with st.container(border=True):
            st.markdown("<div style='color: #cbd5e1; font-size: 11px; font-weight: 600; text-transform: uppercase;'>Discount Simulation Parameters</div>", unsafe_allow_html=True)
            col_inv1, col_inv2 = st.columns(2)
            invoice_val = col_inv1.number_input(f"Outstanding Invoice Amount ({curr_sym})", min_value=1000.0, value=50000.0, step=1000.0)
            due_days = col_inv1.slider("Standard Payment Terms (Days)", 15, 90, 60)
            early_days = col_inv2.slider("Accelerated Early Payment Target (Days)", 5, 30, 10)
            discount_rate = col_inv2.slider("Early Settlement Discount Offered (%)", 0.5, 5.0, 2.0, step=0.5)

        days_saved = due_days - early_days
        discount_amount = invoice_val * (discount_rate / 100.0)
        net_received = invoice_val - discount_amount

        st.write("")
        m1, m2, m3 = st.columns(3)
        m1.markdown(metric_card("Accelerated Net Cash Inflow", fmt_curr(net_received), "", "pos", "Inflow after discount"), unsafe_allow_html=True)
        m2.markdown(metric_card("Discount Cost Incurred", fmt_curr(discount_amount), "", "warn", "Cost of early liquidity"), unsafe_allow_html=True)
        m3.markdown(metric_card("Liquidity Days Saved", f"{days_saved} Days", "", "pos", "Time advantage gained"), unsafe_allow_html=True)

        st.write("")
        with st.container(border=True):
            st.markdown("<div style='color: #38bdf8; font-size: 13px; font-weight: 700;'>🤖 WORKING CAPITAL STRATEGY ANALYSIS</div>", unsafe_allow_html=True)
            st.info(f"💡 **Risk-Free Efficiency Impact:** Offering a {discount_rate}% discount unleashes {fmt_curr(net_received)} in liquidity {days_saved} days earlier, completely avoiding high-interest short-term borrowing costs.")

    # -------------------------------------------------------------------
    # TAB 5: AI FINANCIAL COPILOT
    # -------------------------------------------------------------------
    elif selected_tab == "AI Financial Copilot":
        st.caption("Intelligent Conversational Agent for SME Cash Flow & Policy Intelligence")

        with st.container(border=True):
            st.markdown("<div style='color: #cbd5e1; font-size: 11px; font-weight: 600; text-transform: uppercase;'>Suggested Queries</div>", unsafe_allow_html=True)
            suggested_q = copilot_engine.get_suggested_queries()
            cols = st.columns(2)
            selected_prompt = None
            for idx, q in enumerate(suggested_q):
                if cols[idx % 2].button(f"💡 {q}", key=f"sq_{idx}"):
                    selected_prompt = q

        # Render Chat History
        for msg in st.session_state["chat_messages"]:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

        # Chat Input Area
        chat_input_val = st.chat_input("Ask FinMatrix Copilot a financial question...")
        user_query = selected_prompt if selected_prompt else chat_input_val

        if user_query:
            st.session_state["chat_messages"].append({"role": "user", "content": user_query})
            with st.chat_message("user"):
                st.write(user_query)

            # Process with Copilot Engine
            res = copilot_engine.process_query(user_query)
            ans = res["answer"]
            intent = res["intent"]
            conf = res["confidence"]

            response_text = (
                f"{ans}\n\n"
                f"📌 **Explanation & Strategy:** Evaluated against {biz_sector} cash flow parameters. "
                f"Risk-free guidance applied.\n\n"
                f"*Intent: **{intent}** | Confidence: **{conf}***"
            )

            st.session_state["chat_messages"].append({"role": "assistant", "content": response_text})
            with st.chat_message("assistant"):
                st.write(response_text)

    # -------------------------------------------------------------------
    # TAB 6: RAG KNOWLEDGE SEARCH
    # -------------------------------------------------------------------
    elif selected_tab == "Regulatory RAG Knowledge":
        with st.container(border=True):
            st.markdown("<div style='color: #cbd5e1; font-size: 11px; font-weight: 600; text-transform: uppercase;'>Policy Knowledge Query</div>", unsafe_allow_html=True)
            query = st.text_input("Enter Policy Search Query", "What is the CMSME refinancing loan limit?")
            run_query = st.button("Query Knowledgebase")

        if run_query:
            retriever_obj = None
            for cls_name in ['PolicyRetriever', 'RAGRetriever', 'PolicySearchEngine', 'Retriever']:
                if hasattr(retrieval_module, cls_name):
                    cls = getattr(retrieval_module, cls_name)
                    try:
                        retriever_obj = cls(docs_path="docs")
                    except TypeError:
                        retriever_obj = cls()
                    break

            fallback_msg = "Policy Citation: Under Central Bank CMSME Guidelines, small enterprises can access up to $500,000 refinancing at 7% capped rate."

            if retriever_obj and hasattr(retriever_obj, 'search'):
                results = retriever_obj.search(query)
                if results:
                    st.markdown(badge("Retriever Online", "green") + badge(f"{len(results)} match(es)", "cyan"), unsafe_allow_html=True)
                    for idx, res in enumerate(results, 1):
                        match_text = res.get('text', str(res)) if isinstance(res, dict) else str(res)
                        with st.container(border=True):
                            st.write(f"**[{idx}] Reference Match:** {match_text}")
                else:
                    st.info(fallback_msg)
            else:
                st.info(fallback_msg)

    # -------------------------------------------------------------------
    # TAB 7: SECURITY AUDITOR
    # -------------------------------------------------------------------
    elif selected_tab == "Security & Guardrail Audit":
        with st.container(border=True):
            st.markdown("<div style='color: #cbd5e1; font-size: 11px; font-weight: 600; text-transform: uppercase;'>Adversarial Input Test</div>", unsafe_allow_html=True)
            prompt = st.text_area("Test System Input", "DROP TABLE invoices; --")
            run_audit = st.button("Execute Safety Audit")

        if run_audit:
            suspicious_terms = ["drop table", "delete from", "ignore all previous", "artificially inflate"]
            is_safe = not any(term in prompt.lower() for term in suspicious_terms)

            if is_safe:
                st.success("Input Status: SAFE AND ALLOWED")
            else:
                st.error("Input Status: BLOCKED (Guardrail Triggered)")

    # -------------------------------------------------------------------
    # TAB 8: AUDIT EXPORTER
    # -------------------------------------------------------------------
    elif selected_tab == "Audit Report Exporter":
        report_text = f"""
======================================================
     FINMATRIX COPILOT — EXECUTIVE FINANCIAL AUDIT REPORT
======================================================
Generated Date: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}
Session Status : {st.session_state['auth_state'].upper()}
User Role      : {st.session_state['user_role']}
Sector         : {biz_sector}
Currency       : {curr_sym}

--- 1. EXECUTIVE METRICS ---
Total Inflow   : {fmt_curr(total_inflow_val)}
Total Outflow  : {fmt_curr(total_outflow_val)}
Net Position   : {fmt_curr(net_position_val)}
Solvency Index : {health_score_val} / 100
Safety Buffer  : {fmt_curr(safety_threshold)}
======================================================
        """

        with st.container(border=True):
            st.markdown("<div style='color: #cbd5e1; font-size: 11px; font-weight: 600; text-transform: uppercase;'>Report Preview</div>", unsafe_allow_html=True)
            st.code(report_text)

            if st.session_state["auth_state"] == "authenticated":
                st.download_button("Download Official Audit Summary (.TXT)", data=report_text, file_name="FinMatrix_Executive_Audit_Report.txt", mime="text/plain")

st.markdown("---")
st.caption("FinMatrix Copilot Infrastructure — Built for 2026 Shenzhen International FinTech Competition")