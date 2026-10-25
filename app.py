import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="ShadowPulse AI", page_icon="⚡", layout="wide")

# ---------- Styling ----------
st.markdown("""
<style>
.stApp { background: #07111f; color: #e8f1ff; }
[data-testid="stSidebar"] { background: #0b1728; }
.block-container { padding-top: 1.4rem; }
div[data-testid="stMetric"] {
  background: #0d1d31; border: 1px solid #17344e;
  padding: 14px; border-radius: 12px;
}
h1, h2, h3 { color: #e8f1ff; }
.small-muted { color: #9fb2c8; }
</style>
""", unsafe_allow_html=True)

st.title("⚡ ShadowPulse AI")
st.caption("Software-based electrical load monitoring • simulated readings • explainable anomaly rules")

# ---------- Session state ----------
if "readings" not in st.session_state:
    st.session_state.readings = []
if "alerts" not in st.session_state:
    st.session_state.alerts = []
if "reading_id" not in st.session_state:
    st.session_state.reading_id = 0

LOADS = {
    "LED Lamp": {"nominal_w": 12, "voltage": 230, "current": 0.06, "category": "Lighting"},
    "Ceiling Fan": {"nominal_w": 65, "voltage": 230, "current": 0.30, "category": "Motor"},
    "Laptop Charger": {"nominal_w": 90, "voltage": 230, "current": 0.42, "category": "Electronics"},
    "Water Pump": {"nominal_w": 500, "voltage": 230, "current": 2.20, "category": "Motor"},
    "Heater": {"nominal_w": 1000, "voltage": 230, "current": 4.50, "category": "Heating"},
    "Custom Load": {"nominal_w": 150, "voltage": 230, "current": 0.70, "category": "Other"},
}

def classify_load(power_w):
    if power_w < 30:
        return "Low-power / Lighting"
    if power_w < 150:
        return "Electronics / Small appliance"
    if power_w < 750:
        return "Motor / Medium appliance"
    return "High-power appliance"

def generate_reading(load_name, anomaly_mode=False, voltage_nominal=230, threshold_w=800, threshold_current=5.0):
    spec = LOADS[load_name]
    voltage = float(np.clip(np.random.normal(voltage_nominal, 2.0), 205, 250))
    base_power = spec["nominal_w"]
    multiplier = np.random.uniform(0.92, 1.08)
    if anomaly_mode:
        multiplier = np.random.uniform(1.8, 2.5)
    power = max(1.0, base_power * multiplier)
    current = power / max(voltage, 1)
    energy = power / 1000.0 * (1.0 / 60.0)  # simulated one-minute interval, kWh
    issues = []
    if voltage < 210 or voltage > 245:
        issues.append("Voltage outside configured range")
    if power > threshold_w:
        issues.append("Power threshold exceeded")
    if current > threshold_current:
        issues.append("Current threshold exceeded")
    status = "ANOMALY" if issues else "Normal"
    st.session_state.reading_id += 1
    row = {
        "Reading": st.session_state.reading_id,
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Load": load_name,
        "Category": spec["category"],
        "Voltage (V)": round(voltage, 2),
        "Current (A)": round(current, 3),
        "Power (W)": round(power, 2),
        "Energy (kWh)": round(energy, 5),
        "Estimated Type": classify_load(power),
        "Status": status,
        "Reason": "; ".join(issues) if issues else "No rule triggered",
    }
    st.session_state.readings.append(row)
    if status == "ANOMALY":
        st.session_state.alerts.insert(0, row.copy())
    return row

# ---------- Sidebar controls ----------
st.sidebar.title("Control Panel")
page = st.sidebar.radio(
    "Navigate",
    ["Dashboard", "Live Simulation", "Load Analysis", "Energy Analytics", "Anomaly Alerts", "History", "Settings"]
)
st.sidebar.divider()
