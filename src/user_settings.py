"""
FinMatrix User Preferences & Settings State Manager
"""
import streamlit as st

def init_user_settings():
    """
    Initializes default user preferences in session_state if not already present.
    """
    if "theme_mode" not in st.session_state:
        st.session_state["theme_mode"] = "Dark"
    if "date_format" not in st.session_state:
        st.session_state["date_format"] = "YYYY-MM-DD"
    if "number_format" not in st.session_state:
        st.session_state["number_format"] = "1,234.56"
    if "notify_deficit" not in st.session_state:
        st.session_state["notify_deficit"] = True
    if "notify_overdue" not in st.session_state:
        st.session_state["notify_overdue"] = True
    if "data_consent" not in st.session_state:
        st.session_state["data_consent"] = True
    if "business_name" not in st.session_state:
        st.session_state["business_name"] = "FinMatrix Partner SME"

def update_user_profile(name, business_name):
    """
    Updates profile fields safely.
    """
    if name.strip():
        st.session_state["user_role"] = f"{name.strip()} (Finance Lead)"
    if business_name.strip():
        st.session_state["business_name"] = business_name.strip()
    return True