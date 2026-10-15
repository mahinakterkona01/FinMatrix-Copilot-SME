"""
FinMatrix Centralized Theme Engine
Provides dynamic CSS and Plotly layout styling for Light, Dark, and System modes.
"""

def get_theme_css(mode="Dark"):
    """
    Returns custom CSS rules based on selected theme mode.
    """
    if mode == "Light":
        bg_color = "#f8fafc"
        text_color = "#0f172a"
        card_bg = "#ffffff"
        border_color = "#cbd5e1"
        sidebar_bg = "#f1f5f9"
        input_bg = "#ffffff"
        input_text = "#0f172a"
        primary_blue = "#0284c7"
        sub_text = "#475569"
    else:  # Dark / System Fallback
        bg_color = "#0b0f19"
        text_color = "#f8fafc"
        card_bg = "#1e293b"
        border_color = "#334155"
        sidebar_bg = "#0f172a"
        input_bg = "#1e293b"
        input_text = "#ffffff"
        primary_blue = "#0284c7"
        sub_text = "#cbd5e1"

    css = f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

        html, body, [class*="css"], .stApp {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background-color: {bg_color} !important;
            color: {text_color} !important;
        }}

        #MainMenu, footer {{ visibility: hidden; }}
        .block-container {{ padding-top: 2rem; padding-bottom: 3rem; max-width: 1400px; }}

        section[data-testid="stSidebar"] {{
            background-color: {sidebar_bg} !important;
            border-right: 1px solid {border_color} !important;
        }}

        section[data-testid="stSidebar"] *, 
        section[data-testid="stSidebar"] label,
        section[data-testid="stSidebar"] span,
        section[data-testid="stSidebar"] p,
        section[data-testid="stSidebar"] div {{
            color: {text_color} !important;
        }}

        .stTextInput input, .stTextArea textarea, .stSelectbox select {{
            color: {input_text} !important;
            background-color: {input_bg} !important;
            border: 1px solid {border_color} !important;
            border-radius: 6px !important;
        }}

        .stTextInput label, .stTextArea label, .stSelectbox label {{
            color: {text_color} !important;
            font-weight: 600 !important;
        }}

        div[data-testid="stRadio"] label {{
            background-color: {card_bg} !important;
            padding: 8px 16px !important;
            border-radius: 8px !important;
            border: 1px solid {border_color} !important;
            margin-right: 8px !important;
        }}

        div[data-testid="stRadio"] label p {{
            color: {text_color} !important;
            font-weight: 600 !important;
            font-size: 14px !important;
        }}

        div[data-testid="stVerticalBlockBorderWrapper"] {{
            background-color: {card_bg} !important;
            border: 1px solid {border_color} !important;
            border-radius: 12px !important;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
        }}

        .fp-card {{
            background-color: {card_bg};
            border: 1px solid {border_color};
            border-radius: 12px;
            padding: 18px 20px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        }}
        .fp-card .label {{
            color: {sub_text}; font-size: 11px; font-weight: 600; letter-spacing: 1px; text-transform: uppercase;
        }}
        .fp-card .value {{
            font-size: 24px; font-weight: 700; margin: 6px 0; color: {text_color};
        }}
        .fp-card .caption {{ color: {sub_text}; font-size: 11px; }}

        .badge {{
            display: inline-block; padding: 4px 10px; border-radius: 999px; font-size: 10.5px; font-weight: 600;
            text-transform: uppercase; margin: 2px 4px 2px 0;
        }}
        .badge-green {{ background: #064e3b; color: #34d399 !important; border: 1px solid #059669; }}
        .badge-cyan  {{ background: #0c4a6e; color: #38bdf8 !important; border: 1px solid #0284c7; }}
        .badge-amber {{ background: #78350f; color: #fbbf24 !important; border: 1px solid #d97706; }}
        .badge-red   {{ background: #7f1d1d; color: #f87171 !important; border: 1px solid #dc2626; }}
        .badge-grey  {{ background: #334155; color: #cbd5e1 !important; border: 1px solid #475569; }}

        .status-row {{ display: flex; justify-content: space-between; align-items: center; margin: 6px 0; }}
        .status-row .k {{ color: {sub_text} !important; font-size: 11px; text-transform: uppercase; }}

        .brand-title {{
            text-align: center; font-size: 42px; font-weight: 700; color: #38bdf8; margin-top: 20px;
        }}
        .brand-sub {{ text-align: center; font-size: 16px; color: {text_color}; margin-top: 4px; }}
        .brand-tag {{ text-align: center; font-size: 13px; color: {sub_text}; margin-bottom: 20px; }}

        .stButton > button, .stDownloadButton > button {{
            border-radius: 8px; font-weight: 600;
            border: 1px solid {primary_blue};
            background-color: {primary_blue};
            color: #ffffff !important;
        }}
        .stButton > button:hover {{
            background-color: #0369a1;
            border-color: #0369a1;
        }}
    </style>
    """
    return css

def apply_plotly_theme(fig, mode="Dark", curr_sym="$", height=340, legend=True):
    """
    Applies theme styling to Plotly figures.
    """
    font_color = "#0f172a" if mode == "Light" else "#f8fafc"
    grid_color = "rgba(15, 23, 42, 0.1)" if mode == "Light" else "rgba(255, 255, 255, 0.1)"
    
    fig.update_layout(
        template="plotly_white" if mode == "Light" else "plotly_dark",
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color=font_color, size=12),
        margin=dict(l=10, r=10, t=30, b=10),
        hovermode="x unified",
        showlegend=legend,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, bgcolor="rgba(0,0,0,0)"),
    )
    fig.update_xaxes(showgrid=False, zeroline=False, linecolor="#475569")
    fig.update_yaxes(gridcolor=grid_color, zeroline=False, tickprefix=curr_sym, tickformat=",.0f")
    return fig