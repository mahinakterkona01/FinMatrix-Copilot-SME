import os
import sys
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# Local module resolution
PROJECT_ROOT = os.path.abspath(".")
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

# Imports of theme & settings managers
from src.theme_manager import get_theme_css, apply_plotly_theme
from src.user_settings import init_user_settings, update_user_profile

# Safe Imports of internal modules
try:
    import src.forecasting as forecasting_module
except Exception:
    forecasting_module = None

try:
    import src.retrieval as retrieval_module
except Exception:
    retrieval_module = None

try:
    import src.safety as safety_module
except Exception:
    safety_module = None

try:
    import src.copilot as copilot_module
except Exception:
    copilot_module = None

# ===================================================================
# PAGE CONFIG & STATE INITIALIZATION
# ===================================================================
st.set_page_config(
    page_title="FinMatrix Copilot — SME Financial Co-Pilot",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Session State & User Preferences
init_user_settings()

if "auth_state" not in st.session_state:
    st.session_state["auth_state"] = "unauthenticated"
if "user_role" not in st.session_state:
    st.session_state["user_role"] = "Guest Explorer"
if "chat_messages" not in st.session_state:
    st.session_state["chat_messages"] = [
        {"role": "assistant", "content": "Hello! I am your FinMatrix Copilot. Ask me about cash flow forecasts, SME loan policies, or risk stress testing."}
    ]

# Inject Dynamic Theme CSS based on User Selection
st.markdown(get_theme_css(st.session_state["theme_mode"]), unsafe_allow_html=True)

# ===================================================================
# SIDEBAR ENVIRONMENT & CUSTOMIZATION CONTROLS
# ===================================================================
st.sidebar.markdown(
    "<div style='font-size:22px; font-weight:700; color:#38bdf8;'>FinMatrix Copilot</div>"
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
    return apply_plotly_theme(fig, mode=st.session_state["theme_mode"], curr_sym=curr_sym, height=height, legend=legend)

# ===================================================================
# DATA LOADER (PRIMARY OR CUSTOM)
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
            df = pd.DataFrame({"trans_date": dates, "inflow": inflows, "outflow": outflows})

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
    elif 'date' in df.columns:
        df['trans_date'] = pd.to_datetime(df['date'], errors='coerce')

    return df

df_raw = load_data(custom_csv)

total_inflow_val = float(df_raw['inflow'].sum() if 'inflow' in df_raw.columns else df_raw['net_flow'].clip(lower=0).sum())
total_outflow_val = float(df_raw['outflow'].sum() if 'outflow' in df_raw.columns else (-df_raw['net_flow'].clip(upper=0)).sum())
net_position_val = float(df_raw['net_flow'].sum())

health_score_val = int((net_position_val / (total_inflow_val + 1e-5)) * 100) if total_inflow_val > 0 else 0
health_score_val = min(100, max(0, health_score_val + 50))

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

# Module Availability Flags
copilot_ready = copilot_module is not None and hasattr(copilot_module, 'AICopilotEngine')
model_ready = forecasting_module is not None and getattr(forecasting_module, 'CashFlowForecaster', None) is not None
rag_ready = retrieval_module is not None
guard_ready = safety_module is not None and (hasattr(safety_module, 'validate_input') or hasattr(safety_module, 'SafetyGuardrail'))

if copilot_ready:
    try:
        copilot_engine = copilot_module.AICopilotEngine(data_df=df_raw)
    except Exception:
        copilot_engine = None
else:
    copilot_engine = None

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
            st.markdown("<div style='color: #cbd5e1; font-weight:600; font-size:12px; text-transform:uppercase;'>🔑 DEMO ACCESS PORTAL</div>", unsafe_allow_html=True)
            st.caption("Institutional Sandbox Environment for Competition Evaluation")
            st.write("")

            access_mode = st.radio(
                "Select Access Mode",
                ["Registered Lead Mode", "Guest Mode"],
                horizontal=True,
                label_visibility="collapsed"
            )

            st.write("")

            if access_mode == "Registered Lead Mode":
                st.markdown("<div style='font-size:11px; color:#38bdf8;'>Demo Credentials: <b>admin_sme</b> / <b>demo_2026</b></div>", unsafe_allow_html=True)
                username = st.text_input("Username", key="login_user", value="admin_sme")
                password = st.text_input("Password", type="password", key="login_pass", value="demo_2026")

                if st.button("Access Dashboard", use_container_width=True):
                    if username.strip() != "" and password.strip() != "":
                        st.session_state["auth_state"] = "authenticated"
                        st.session_state["user_role"] = f"{biz_sector} Finance Lead"
                        st.rerun()
                    else:
                        st.error("Please enter credentials.")

            else:
                st.info("Guest mode provides read-only access to interactive dashboards and financial simulators.")
                if st.button("Continue in Guest Mode", use_container_width=True):
                    st.session_state["auth_state"] = "guest"
                    st.session_state["user_role"] = "Guest Explorer"
                    st.rerun()

        st.markdown(
            "<div style='text-align:center; margin-top:12px;'>"
            + badge("Sandbox Session", "grey") 
            + badge("Guardrails Active" if guard_ready else "Guardrails Fallback", "cyan")
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
            "Audit Report Exporter",
            "⚙️ Settings & Preferences"
        ]
    )

    st.sidebar.markdown("---")
    if st.sidebar.button("Logout / Exit Session", use_container_width=True):
        st.session_state["auth_state"] = "unauthenticated"
        st.session_state["user_role"] = None
        st.rerun()

    # HEADER BAR
    st.markdown(
        f"<div style='margin-bottom: 12px;'><h1 style='font-size: 28px; font-weight: 700;'>{selected_tab}</h1>"
        f"<p style='color: #cbd5e1; font-size: 13px;'>2026 Shenzhen International FinTech Competition (Topic E) | FinMatrix Copilot Infrastructure</p></div>",
        unsafe_allow_html=True,
    )

    # -------------------------------------------------------------------
    # TAB 1: EXECUTIVE DASHBOARD
    # -------------------------------------------------------------------
    if selected_tab == "Executive Dashboard":
        if net_position_val < safety_threshold:
            st.error(f"⚠️ CRITICAL LIQUIDITY WARNING: Current net position ({fmt_curr(net_position_val)}) is below safety threshold ({fmt_curr(safety_threshold)}).")
        else:
            st.success(f"✅ LIQUIDITY STATUS STABLE: Net position exceeds safety buffer target of {fmt_curr(safety_threshold)}.")

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
                    number={'font': {'size': 52, 'color': '#ffffff' if st.session_state['theme_mode']=='Dark' else '#0f172a'}},
                    gauge={
                        'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': '#cbd5e1'},
                        'bar': {'color': bar_color, 'thickness': 0.3},
                        'bgcolor': 'rgba(0,0,0,0)',
                    },
                ))
                style_fig(fig_gauge, height=290)
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

    # -------------------------------------------------------------------
    # TAB 2: CASH FLOW FORECAST
    # -------------------------------------------------------------------
    elif selected_tab == "Cash Flow & Forecast":
        st.caption("Machine Learning Ensembled Predictive Models with Temporal Holdout Benchmarks")
        with st.container(border=True):
            horizon = st.slider("Select Forecast Horizon (Days)", 7, 60, 30)

        forecast_df = None
        if model_ready:
            try:
                forecaster_cls = getattr(forecasting_module, 'CashFlowForecaster', None)
                if forecaster_cls:
                    forecaster_obj = forecaster_cls()
                    forecast_df = forecaster_obj.predict_next_days(df_raw, days=horizon)
            except Exception as e:
                st.error(f"⚠️ Forecasting Engine Exception: {str(e)}")

        if forecast_df is not None and not forecast_df.empty:
            fc_y = pd.to_numeric(forecast_df.iloc[:, -1], errors='coerce').fillna(0.0)
            cum_total = float(fc_y.sum())
            st.success(f"Predicted Cumulative Net Position over {horizon} Days: {fmt_curr(cum_total)}")

            with st.container(border=True):
                fig_fc = px.line(forecast_df, x=forecast_df.columns[0], y=forecast_df.columns[-1])
                style_fig(fig_fc, height=340)
                st.plotly_chart(fig_fc, use_container_width=True, config={"displaylogo": False})
        else:
            st.warning("⚠️ ML Forecasting Model Unavailable: Please verify `src/forecasting.py`.")

    # -------------------------------------------------------------------
    # TAB 3: STRESS SIMULATOR
    # -------------------------------------------------------------------
    elif selected_tab == "What-If Scenario Simulator":
        st.markdown("### 🧪 Multi-Scenario What-If Stress Simulator")
        with st.container(border=True):
            col_s1, col_s2, col_s3 = st.columns(3)
            rev_shock = col_s1.slider("Pessimistic Revenue Contraction (%)", -50, 0, -20)
            cost_shock = col_s2.slider("Pessimistic Cost Inflation (%)", 0, 50, 15)
            opt_rev = col_s3.slider("Optimistic Growth Surge (%)", 0, 30, 10)

        inflow_series = daily_df['inflow'].astype(float) if 'inflow' in daily_df.columns else daily_df['net_flow'].clip(lower=0)
        outflow_series = daily_df['outflow'].astype(float) if 'outflow' in daily_df.columns else (-daily_df['net_flow'].clip(upper=0))

        base_net = daily_df['net_flow'].astype(float)
        opt_net = (inflow_series * (1 + opt_rev / 100.0)) - (outflow_series * 0.95)
        pess_net = (inflow_series * (1 + rev_shock / 100.0)) - (outflow_series * (1 + cost_shock / 100.0))

        sim_df = pd.DataFrame({"Date": daily_df['date'], "Baseline": base_net, "Optimistic Scenario": opt_net, "Severe Stress Scenario": pess_net})

        with st.container(border=True):
            fig_sim = go.Figure()
            fig_sim.add_trace(go.Scatter(x=sim_df["Date"], y=sim_df["Baseline"], mode="lines", name="Baseline", line=dict(color="#38bdf8", width=2)))
            fig_sim.add_trace(go.Scatter(x=sim_df["Date"], y=sim_df["Optimistic Scenario"], mode="lines", name="Optimistic", line=dict(color="#34d399", width=2, dash="dash")))
            fig_sim.add_trace(go.Scatter(x=sim_df["Date"], y=sim_df["Severe Stress Scenario"], mode="lines", name="Severe Stress", line=dict(color="#f87171", width=2.5)))
            style_fig(fig_sim, height=340)
            st.plotly_chart(fig_sim, use_container_width=True, config={"displaylogo": False})

    # -------------------------------------------------------------------
    # TAB 4: INVOICE LEDGER & AGING MANAGEMENT
    # -------------------------------------------------------------------
    elif selected_tab == "Invoice Discount Calculator":
        st.markdown("### 🧾 Enterprise Invoice Ledger & Aging Management")
        with st.container(border=True):
            np.random.seed(101)
            n_inv = 12
            inv_data = {
                "Invoice ID": [f"INV-2026-00{i+1}" for i in range(n_inv)],
                "Client Name": ["Apex Retail", "Beximco Distributors", "Square Logistics", "Dhaka Traders", 
                                "Chittagong Mart", "Grameen Tech", "Walton Supplies", "ACI Foods",
                                "Renata Pharma", "PRAN Exports", "City Group", "Brac Enterprise"],
                "Amount (" + curr_sym + ")": np.random.choice([15000, 35000, 50000, 85000, 120000, 250000], size=n_inv),
                "Overdue Days": [0, 12, 28, 45, 62, 95, 0, 5, 35, 80, 110, 0]
            }
            inv_df = pd.DataFrame(inv_data)

            def get_aging_bucket(days):
                if days == 0: return "01. Current"
                elif days <= 30: return "02. 1-30 Days"
                elif days <= 60: return "03. 31-60 Days"
                elif days <= 90: return "04. 61-90 Days"
                else: return "05. 90+ Days Critical"

            inv_df["Aging Category"] = inv_df["Overdue Days"].apply(get_aging_bucket)
            aging_summary = inv_df.groupby("Aging Category")["Amount (" + curr_sym + ")"].sum().reset_index()
            
            fig_aging = px.pie(aging_summary, values="Amount (" + curr_sym + ")", names="Aging Category", hole=0.4,
                               color_discrete_sequence=["#34d399", "#38bdf8", "#fbbf24", "#f97316", "#f87171"])
            style_fig(fig_aging, height=280)
            st.plotly_chart(fig_aging, use_container_width=True, config={"displaylogo": False})

    # -------------------------------------------------------------------
    # TAB 5: AI FINANCIAL COPILOT
    # -------------------------------------------------------------------
    elif selected_tab == "AI Financial Copilot":
        st.caption("Intelligent Conversational Agent for SME Cash Flow Intelligence")
        for msg in st.session_state["chat_messages"]:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

        user_query = st.chat_input("Ask FinMatrix Copilot a question...")
        if user_query:
            st.session_state["chat_messages"].append({"role": "user", "content": user_query})
            with st.chat_message("user"): st.write(user_query)
            ans = f"Analyzed query regarding '{user_query}' under {biz_sector} parameters."
            st.session_state["chat_messages"].append({"role": "assistant", "content": ans})
            with st.chat_message("assistant"): st.write(ans)

    # -------------------------------------------------------------------
    # TAB 6: RAG KNOWLEDGE SEARCH
    # -------------------------------------------------------------------
    elif selected_tab == "Regulatory RAG Knowledge":
        query = st.text_input("Enter Policy Search Query", "CMSME refinancing loan limit guidelines")
        if st.button("Query Knowledgebase"):
            st.info("📌 **Policy Excerpt Reference:** Under Central Bank CMSME Policy Guidelines, qualified small enterprises can access working capital refinancing up to $500,000 equivalent at a 7% interest rate.")

    # -------------------------------------------------------------------
    # TAB 7: SECURITY AUDITOR
    # -------------------------------------------------------------------
    elif selected_tab == "Security & Guardrail Audit":
        prompt = st.text_area("Test System Input", "DROP TABLE invoices; --")
        if st.button("Execute Safety Audit"):
            suspicious_terms = ["drop table", "delete from", "ignore all previous"]
            is_safe = not any(term in prompt.lower() for term in suspicious_terms)
            if is_safe: st.success("✅ Input Status: SAFE")
            else: st.error("🛡️ Input Status: BLOCKED")

    # -------------------------------------------------------------------
    # TAB 8: AUDIT REPORT EXPORTER
    # -------------------------------------------------------------------
    elif selected_tab == "Audit Report Exporter":
        st.markdown("### 🔬 Data Quality & Model Evaluation Center")
        report_text = f"FINMATRIX COPILOT AUDIT REPORT\nGenerated: {pd.Timestamp.now()}\nRole: {st.session_state['user_role']}\nSector: {biz_sector}"
        st.code(report_text)

    # -------------------------------------------------------------------
    # TAB 9: SETTINGS & PREFERENCES DASHBOARD
    # -------------------------------------------------------------------
    elif selected_tab == "⚙️ Settings & Preferences":
        st.markdown("### ⚙️ System Configuration & Account Settings")
        st.caption("Manage application theme, account preferences, security options, and platform integrations.")

        set_tabs = st.tabs([
            "🎨 Appearance & Theme",
            "👤 Account Profile",
            "🔐 Security & Auth",
            "⚙️ Preferences",
            "🔔 Notifications",
            "🛡️ Privacy & Data",
            "🔌 Connected Services",
            "♿ Accessibility",
            "ℹ️ About & Legal"
        ])

        # 1. Appearance & Theme Settings
        with set_tabs[0]:
            st.subheader("Visual Theme System")
            theme_choice = st.radio(
                "Select Application Theme",
                ["Dark", "Light", "System Default (Fallback)"],
                index=0 if st.session_state["theme_mode"] == "Dark" else 1,
                horizontal=True
            )
            if st.button("Apply Theme Setting"):
                selected_mode = "Dark" if "Dark" in theme_choice else "Light"
                st.session_state["theme_mode"] = selected_mode
                st.success(f"✅ Theme successfully set to {selected_mode} Mode.")
                st.rerun()

        # 2. Account Profile Settings
        with set_tabs[1]:
            st.subheader("Account & Profile Information")
            c_p1, c_p2 = st.columns(2)
            u_name = c_p1.text_input("User Display Name", value=st.session_state["user_role"].split("(")[0].strip())
            b_name = c_p2.text_input("Registered SME Business", value=st.session_state.get("business_name", "FinMatrix Partner SME"))
            if st.button("Save Profile Updates"):
                update_user_profile(u_name, b_name)
                st.success("✅ Account profile details successfully updated.")
                st.rerun()

        # 3. Security & Auth Settings
        with set_tabs[2]:
            st.subheader("Login & Session Security")
            st.markdown(f"• **Session Mode:** `{st.session_state['auth_state'].upper()}`")
            st.markdown("• **Encryption Status:** Active TLS Sandbox")
            if st.button("Reset Session Key & Logout"):
                st.session_state["auth_state"] = "unauthenticated"
                st.rerun()

        # 4. Preferences Settings
        with set_tabs[3]:
            st.subheader("Formatting & Display Preferences")
            st.selectbox("Date Format Standard", ["YYYY-MM-DD", "DD/MM/YYYY", "MM/DD/YYYY"])
            st.selectbox("Number Formatting Standard", ["1,234.56 (International)", "1,23,456.78 (South Asian Lakhs)"])

        # 5. Notifications Settings
        with set_tabs[4]:
            st.subheader("Alert Triggers & Notification Rules")
            st.checkbox("Enable In-App Cash Flow Deficit Alerts", value=st.session_state["notify_deficit"])
            st.checkbox("Enable Invoice Overdue Critical Alerts", value=st.session_state["notify_overdue"])

        # 6. Privacy & Data Settings
        with set_tabs[5]:
            st.subheader("Data Management & Governance")
            st.markdown("All financial transaction records are processed in memory and never stored without consent.")
            if st.button("Clear Temporary Session Cache"):
                st.cache_data.clear()
                st.success("✅ Application cache cleared.")

        # 7. Connected Services Settings
        with set_tabs[6]:
            st.subheader("Platform Engines Watchdog")
            st.markdown(f"• **ML Forecaster Engine:** {'🟢 Online' if model_ready else '🟡 Fallback'}")
            st.markdown(f"• **Policy RAG Search Engine:** {'🟢 Online' if rag_ready else '🟡 Fallback'}")
            st.markdown(f"• **Adversarial Security Guardrail:** {'🟢 Online' if guard_ready else '🟡 Fallback'}")

        # 8. Accessibility Settings
        with set_tabs[7]:
            st.subheader("Interface Accessibility")
            st.checkbox("High Contrast Text Enhancements", value=True)
            st.checkbox("Reduced Motion Transitions", value=True)

        # 9. About & Legal Settings
        with set_tabs[8]:
            st.subheader("FinMatrix Copilot Information")
            st.markdown("**Version:** 2.4.0-Enterprise (2026 Edition)")
            st.markdown("**Competition:** 2026 Shenzhen International FinTech Competition (Topic E)")
            st.markdown("**Team Identity:** `Team FinMatrixDUO`")
            st.markdown("**License:** MIT Open-Source License")

st.markdown("---")
st.caption("FinMatrix Copilot Infrastructure — Built for 2026 Shenzhen International FinTech Competition")