import os
import random
import time
from datetime import datetime, timezone, timedelta

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

try:
    from supabase import create_client
except ImportError:
    create_client = None

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="ShadowPulse AI",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------- THEME ----------------
st.markdown("""
<style>
:root { color-scheme: dark; }
.stApp { background: #071321; color: #edf6ff; }
[data-testid="stSidebar"] { background: #0c2034; border-right: 1px solid #193b55; }
[data-testid="stMetric"] {
  background: linear-gradient(135deg, #102b46, #0c2034);
  border: 1px solid #1b4965; border-radius: 14px; padding: 15px 16px;
}
[data-testid="stMetricLabel"] { color: #a9c8df !important; }
[data-testid="stMetricValue"] { color: #47e3d0 !important; }
h1, h2, h3 { color: #edf6ff; }
p, label, li { color: #d4e5f2; }
div.stButton > button, div.stDownloadButton > button {
  background: #43dfcf; color: #061522; border: 0; border-radius: 9px;
  font-weight: 700; min-height: 2.55rem;
}
div.stButton > button:hover, div.stDownloadButton > button:hover {
  background: #75f0e3; color: #061522; border: 0;
}
.sp-panel {
  background: #0d2237; border: 1px solid #1a405a; border-radius: 14px;
  padding: 16px 18px; margin-bottom: 10px;
}
.sp-muted { color: #9ebbd0; font-size: .9rem; }
.sp-pill {
  display:inline-block; padding: 5px 10px; border-radius: 999px;
  background:#123d4a; color:#59f0df; font-weight:800; font-size:.78rem;
  border:1px solid #216a78;
}
[data-testid="stDataFrame"] { border: 1px solid #1a405a; border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

# ---------------- CONSTANTS ----------------
LOAD_PROFILES = {
    "LED Lamp": {"voltage": 5.0, "current": 0.22, "variation": 0.025, "expected_max": 0.35},
    "DC Motor": {"voltage": 5.0, "current": 0.62, "variation": 0.07, "expected_max": 0.90},
    "Other Load": {"voltage": 5.0, "current": 0.40, "variation": 0.08, "expected_max": 0.75},
}
NAV_ITEMS = [
    "Dashboard", "Live Simulation", "AI Analysis", "Energy Analytics",
    "Alerts", "History", "Settings"
]

# ---------------- SUPABASE HELPERS ----------------
def get_supabase():
    if create_client is None:
        return None, "Supabase package is not installed"
    try:
        url = st.secrets.get("SUPABASE_URL", os.getenv("SUPABASE_URL", ""))
        key = st.secrets.get("SUPABASE_KEY", os.getenv("SUPABASE_KEY", ""))
        if not url or not key:
            return None, "Demo mode — Supabase credentials not configured"
        return create_client(url, key), "Connected configuration found"
    except Exception as exc:
        return None, f"Supabase not configured: {exc}"

def persist_reading(row):
    client, status = get_supabase()
    if client is None:
        return False, status
    try:
        client.table("sensor_readings").insert(row).execute()
        return True, "Saved to Supabase"
    except Exception as exc:
        return False, f"Supabase save failed: {exc}"

def persist_alert(row):
    client, status = get_supabase()
    if client is None:
        return False, status
