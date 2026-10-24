import time
import random
from datetime import datetime

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="ShadowPulse AI",
    page_icon="⚡",
    layout="wide"
)

# ---------- CONTRASTING DASHBOARD STYLE ----------
st.markdown("""
<style>
.stApp {
    background: #071321;
    color: #F4F7FB;
}
[data-testid="stSidebar"] {
    background: #10243A;
}
h1, h2, h3, p, label {
    color: #F4F7FB;
}
[data-testid="stMetric"] {
    background: #102B46;
    padding: 18px;
    border-radius: 12px;
    border: 1px solid #284966;
}
[data-testid="stMetricValue"] {
    color: #4DE2C5;
}
.stButton > button {
    background: #4DE2C5;
    color: #071321;
    border-radius: 8px;
    border: none;
    font-weight: bold;
    width: 100%;
}
</style>
""", unsafe_allow_html=True)

# ---------- HEADER ----------
st.title("⚡ ShadowPulse AI")
st.subheader("Virtual Electrical Load Monitoring & Anomaly Detection")
st.caption(
    "ESP32 Wokwi-inspired simulation | Synthetic readings only | "
    "Not connected to a physical sensor"
)

# ---------- SIDEBAR ----------
st.sidebar.title("Simulation Controls")

load_name = st.sidebar.selectbox(
    "Choose load category",
    ["Auto Detect", "Lamp-like", "Fan-like", "Motor-like"]
)

simulation_mode = st.sidebar.selectbox(
    "Simulation scenario",
    [
        "Normal Operation",
        "Variable Input",
        "Unusual Input"
    ]
)

reading_count = st.sidebar.slider(
    "Number of readings",
    min_value=10,
    max_value=100,
    value=30,
    step=10
)

run_button = st.sidebar.button("▶ Run Simulation")
st.sidebar.caption("Each reading represents one simulated second.")

# ---------- SENSOR SIMULATION ----------
def generate_readings(count, scenario):
    rows = []
    raw_values = []

    for i in range(count):
        # Simulates ESP32 analogRead(GPIO 32), 12-bit range
        if scenario == "Normal Operation":
            raw = random.randint(250, 2100)
        elif scenario == "Variable Input":
            raw = random.randint(500, 3000)
        else:
            # Generate some high inputs to demonstrate alerts
            if random.random() < 0.45:
                raw = random.randint(2500, 4095)
            else:
                raw = random.randint(800, 2500)

        # Same conversion idea as the Wokwi sketch
        current = (raw / 4095.0) * 1.5
        voltage = 5.0
        power = voltage * current

        if current < 0.28:
            detected_load = "Lamp-like"
        elif current < 0.48:
            detected_load = "Fan-like"
        else:
            detected_load = "Motor-like"

        anomaly = current > 0.90
        status = "UNUSUAL INPUT" if anomaly else "Normal"

        rows.append({
            "Reading": i + 1,
            "Raw ADC": raw,
            "Current (A)": round(current, 3),
            "Voltage (V)": voltage,
            "Power (W)": round(power, 3),
            "Detected Category": detected_load,
            "Status": status
        })
        raw_values.append(raw)

    return pd.DataFrame(rows)

# ---------- RUN AND SAVE RESULTS ----------
if "history" not in st.session_state:
    st.session_state.history = pd.DataFrame()

if run_button:
    st.session_state.current_data = generate_readings(
        reading_count, simulation_mode
    )
    st.session_state.last_run = datetime.now().strftime(
        "%d-%m-%Y %H:%M:%S"
    )
    st.session_state.last_scenario = simulation_mode

if "current_data" not in st.session_state:
    st.session_state.current_data = generate_readings(
        reading_count, "Normal Operation"
    )
    st.session_state.last_run = "Preview only"
    st.session_state.last_scenario = "Normal Operation"

df = st.session_state.current_data.copy()

# ---------- FILTER DISPLAY CATEGORY ----------
if load_name != "Auto Detect":
    display_df = df[df["Detected Category"] == load_name].copy()
    if display_df.empty:
        display_df = df.copy()
        st.info(
            "No readings matched that category in this run. "
            "Showing all readings instead."
        )
else:
    display_df = df.copy()

# ---------- METRICS ----------
total = len(df)
alerts = int((df["Status"] == "UNUSUAL INPUT").sum())
normal = total - alerts
alert_percentage = (alerts / total * 100) if total else 0
avg_current = df["Current (A)"].mean()
max_current = df["Current (A)"].max()
avg_power = df["Power (W)"].mean()

if max_current > 0.90:
    overall_status = "UNUSUAL INPUT"
else:
    overall_status = "Normal"

st.markdown("### Live Simulation Summary")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Latest Current", f"{df.iloc[-1]['Current (A)']:.2f} A")
c2.metric("Demo Voltage", "5.00 V")
c3.metric("Latest Power", f"{df.iloc[-1]['Power (W)']:.2f} W")
c4.metric("Unusual Readings", f"{alerts} / {total}")

# ---------- ALERT ----------
if overall_status == "UNUSUAL INPUT":
    st.error(
        f"⚠️ Unusual input detected in this simulation. "
        f"{alerts} of {total} readings crossed 0.90 A."
    )
else:
    st.success(
        "✅ No readings crossed the configured 0.90 A threshold "
        "in this simulation."
    )

st.caption(
    f"Scenario: {st.session_state.last_scenario} | "
    f"Last run: {st.session_state.last_run} | "
    f"Mean current: {avg_current:.3f} A | "
    f"Maximum current: {max_current:.3f} A | "
    f"Mean demo power: {avg_power:.3f} W"
)

# ---------- CURRENT GRAPH ----------
st.markdown("### 📈 Current Monitoring")

fig_current = px.line(
    display_df,
    x="Reading",
    y="Current (A)",
    markers=True,
    title="Simulated Current Readings"
)
fig_current.add_hline(
    y=0.90,
    line_dash="dash",
    annotation_text="Unusual input threshold: 0.90 A"
)
fig_current.update_layout(
    paper_bgcolor="#10243A",
    plot_bgcolor="#10243A",
    font_color="#F4F7FB",
    xaxis_title="Reading number",
    yaxis_title="Current (A)"
)
st.plotly_chart(fig_current, use_container_width=True)

# ---------- POWER GRAPH ----------
st.markdown("### ⚡ Power Monitoring")

fig_power = px.area(
    display_df,
    x="Reading",
    y="Power (W)",
    title="Calculated Demo Power (Voltage × Current)"
)
fig_power.update_layout(
    paper_bgcolor="#10243A",
    plot_bgcolor="#10243A",
    font_color="#F4F7FB"
)
st.plotly_chart(fig_power, use_container_width=True)

# ---------- CATEGORY SUMMARY ----------
st.markdown("### 🔎 Load Category Summary")

category_counts = df["Detected Category"].value_counts().reset_index()
category_counts.columns = ["Load Category", "Number of Readings"]

col_left, col_right = st.columns(2)

with col_left:
    st.dataframe(category_counts, use_container_width=True, hide_index=True)

with col_right:
    fig_category = px.pie(
        category_counts,
        names="Load Category",
        values="Number of Readings",
        title="Detected Load Categories"
    )
    fig_category.update_layout(
        paper_bgcolor="#10243A",
        font_color="#F4F7FB"
    )
    st.plotly_chart(fig_category, use_container_width=True)

# ---------- READINGS TABLE ----------
st.markdown("### 🧾 Sensor Readings Table")
st.dataframe(display_df, use_container_width=True, hide_index=True)

# ---------- DOWNLOAD ----------
csv_data = df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="⬇ Download Simulation Report",
    data=csv_data,
    file_name="shadowpulse_simulation_report.csv",
    mime="text/csv"
)

st.markdown("---")
st.caption(
    "Demo limitation: ADC readings, current, and voltage are simulated. "
    "No physical current sensor is connected. This threshold demo is "
    "not a certified electrical protection or fault-detection system."
)
