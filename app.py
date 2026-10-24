
import random
from datetime import datetime

import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="ShadowPulse AI",
    page_icon="⚡",
    layout="wide"
)

# ---------- STYLE ----------
st.markdown("""
<style>
.stApp {
    background-color: #0b1220;
    color: #f1f5f9;
}
[data-testid="stMetric"] {
    background: #172338;
    padding: 16px;
    border-radius: 12px;
}
div[data-testid="stAlert"] {
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

# ---------- SESSION DATA ----------
if "history" not in st.session_state:
    st.session_state.history = []

if "reading_no" not in st.session_state:
    st.session_state.reading_no = 0

# ---------- SIDEBAR ----------
st.sidebar.title("⚡ ShadowPulse AI")
st.sidebar.caption("Intelligent Energy Monitoring")

load_type = st.sidebar.selectbox(
    "Select Electrical Load",
    ["LED Lamp", "DC Motor", "Other Load"]
)

simulate_anomaly = st.sidebar.toggle(
    "Simulate unusual consumption",
    value=False
)

st.sidebar.info(
    "Demo mode: readings are simulated, "
    "not collected from real hardware."
)

# ---------- LOAD PROFILES ----------
profiles = {
    "LED Lamp": {
        "voltage": 12.0,
        "current": 0.5,
        "limit": 10.0
    },
    "DC Motor": {
        "voltage": 12.0,
        "current": 1.5,
        "limit": 25.0
    },
    "Other Load": {
        "voltage": 5.0,
        "current": 1.0,
        "limit": 8.0
    }
}

profile = profiles[load_type]

# ---------- HEADER ----------
st.title("⚡ ShadowPulse AI")
st.write(
    "Smart energy monitoring and unusual-consumption detection"
)

st.caption(
    "Prototype dashboard | Python + Streamlit | Simulated sensor data"
)

# ---------- GENERATE READING ----------
def generate_reading():
    voltage = random.uniform(
        profile["voltage"] * 0.95,
        profile["voltage"] * 1.05
    )

    current = random.uniform(
        profile["current"] * 0.85,
        profile["current"] * 1.15
    )

    if simulate_anomaly:
        current = profile["current"] * random.uniform(2.0, 3.0)

    power = voltage * current

    # Simple rule-based anomaly detection
    if power > profile["limit"]:
        status = "UNUSUAL"
        risk = "HIGH"
        recommendation = (
            "Inspect the load and check for unexpected "
            "power consumption."
        )
    else:
        status = "NORMAL"
        risk = "LOW"
        recommendation = (
            "Consumption is within the configured demo limit."
        )

    return {
        "Time": datetime.now().strftime("%H:%M:%S"),
        "Load": load_type,
        "Voltage (V)": round(voltage, 2),
        "Current (A)": round(current, 2),
        "Power (W)": round(power, 2),
        "Status": status,
        "Risk": risk,
        "Recommendation": recommendation
    }


# ---------- BUTTONS ----------
left, right = st.columns([2, 1])

with left:
    st.subheader("Live Monitoring")

with right:
    generate = st.button(
        "🔄 Generate New Reading",
        use_container_width=True
    )

if generate or not st.session_state.history:
    reading = generate_reading()
    st.session_state.history.append(reading)
    st.session_state.reading_no += 1

# ---------- CURRENT READING ----------
current_reading = st.session_state.history[-1]

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Voltage",
    f'{current_reading["Voltage (V)"]} V'
)

c2.metric(
    "Current",
    f'{current_reading["Current (A)"]} A'
)

c3.metric(
    "Power",
    f'{current_reading["Power (W)"]} W'
)

c4.metric(
    "Readings Generated",
    st.session_state.reading_no
)

st.write(f"**Selected load:** {load_type}")

if current_reading["Status"] == "UNUSUAL":
    st.error("🚨 Unusual power consumption detected!")
    st.warning(current_reading["Recommendation"])
else:
    st.success("✅ Power consumption is within the demo limit.")
    st.info(current_reading["Recommendation"])

# ---------- LOAD IDENTIFICATION ----------
st.subheader("Load Identification")

st.write(
    f"Detected load category: **{current_reading['Load']}**"
)

st.caption(
    "In this prototype, the load category comes from your "
    "selection; automatic electrical load classification "
    "is not implemented."
)

# ---------- HISTORY ----------
df = pd.DataFrame(st.session_state.history)

st.subheader("📊 Power Consumption History")

chart_data = df[["Time", "Power (W)"]].set_index("Time")
st.line_chart(chart_data)

st.subheader("📋 Reading History")
st.dataframe(df, use_container_width=True, hide_index=True)

# ---------- SUMMARY ----------
st.subheader("🧠 Risk Summary")

unusual_count = int((df["Status"] == "UNUSUAL").sum())
normal_count = int((df["Status"] == "NORMAL").sum())

m1, m2, m3 = st.columns(3)
m1.metric("Normal Readings", normal_count)
m2.metric("Unusual Readings", unusual_count)
m3.metric(
    "Latest Risk",
    current_reading["Risk"]
)

# ---------- DOWNLOAD ----------
st.download_button(
    "⬇️ Download Reading History (CSV)",
    data=df.to_csv(index=False).encode("utf-8"),
    file_name="shadowpulse_history.csv",
    mime="text/csv"
)

if st.button("🗑️ Clear History"):
    st.session_state.history = []
    st.session_state.reading_no = 0
    st.rerun()

# ---------- ENERGY ANALYTICS ----------
st.subheader("⚡ Energy Analytics")

hours_used = st.slider(
    "Estimated operating hours per day",
    min_value=1,
    max_value=24,
    value=8
)

tariff = st.number_input(
    "Electricity cost per kWh (₹)",
    min_value=0.0,
    value=8.0,
    step=0.5
)

power_kw = current_reading["Power (W)"] / 1000

daily_energy = power_kw * hours_used
monthly_energy = daily_energy * 30
monthly_cost = monthly_energy * tariff

a, b, c = st.columns(3)

a.metric("Estimated Daily Energy", f"{daily_energy:.3f} kWh")
b.metric("Estimated Monthly Energy", f"{monthly_energy:.2f} kWh")
c.metric("Estimated Monthly Cost", f"₹{monthly_cost:.2f}")

st.caption(
    "Estimates assume the latest power reading stays constant "
    "for the selected operating hours. Actual usage and bills may vary."
)

st.divider()

st.caption(
    "ShadowPulse AI | Educational simulation prototype. "
    "Not intended for electrical safety decisions."
)
