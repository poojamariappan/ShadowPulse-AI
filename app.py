
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import random
import time

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="ShadowPulse AI",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------- SESSION STATE ----------------
if "history" not in st.session_state:
    st.session_state.history = []

if "voltage" not in st.session_state:
    st.session_state.voltage = 230.0

if "current" not in st.session_state:
    st.session_state.current = 2.5

if "simulation_running" not in st.session_state:
    st.session_state.simulation_running = False

if "threshold" not in st.session_state:
    st.session_state.threshold = 1000.0

# ---------------- CUSTOM STYLE ----------------
st.markdown("""
<style>
.main {
    background-color: #f5f7fb;
}
[data-testid="stMetric"] {
    background-color: white;
    padding: 16px;
    border-radius: 12px;
    border: 1px solid #e5e7eb;
}
h1, h2, h3 {
    color: #172554;
}
</style>
""", unsafe_allow_html=True)

# ---------------- SIDEBAR ----------------
st.sidebar.title("⚡ ShadowPulse AI")
st.sidebar.caption("Smart Electrical Monitoring System")

page = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Live Simulation",
        "Load Analysis",
        "Energy Analytics",
        "Anomaly Alerts",
        "History",
        "Settings"
    ]
)

st.sidebar.divider()
st.sidebar.write("**System Status**")
st.sidebar.success("Demo system active")
st.sidebar.caption("Using simulated sensor readings")

# ---------------- HELPER FUNCTIONS ----------------
def generate_reading():
    """Generate simulated electrical readings."""
    voltage = round(random.uniform(215, 245), 2)
    current = round(random.uniform(0.5, 8.0), 2)
    power = round(voltage * current, 2)
    energy = round(power / 1000, 3)

    if voltage < 220:
        status = "Low Voltage"
    elif voltage > 240:
        status = "High Voltage"
    elif power > st.session_state.threshold:
        status = "High Load"
    else:
        status = "Normal"

    return {
        "Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Voltage (V)": voltage,
        "Current (A)": current,
        "Power (W)": power,
        "Energy (kWh)": energy,
        "Status": status
    }


def get_history_df():
    if not st.session_state.history:
        return pd.DataFrame(
            columns=[
                "Time", "Voltage (V)", "Current (A)",
                "Power (W)", "Energy (kWh)", "Status"
            ]
        )
    return pd.DataFrame(st.session_state.history)


def show_metrics(reading):
    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Voltage", f"{reading['Voltage (V)']} V")
    col2.metric("Current", f"{reading['Current (A)']} A")
    col3.metric("Power", f"{reading['Power (W)']} W")
    col4.metric("Energy", f"{reading['Energy (kWh)']} kWh")


def add_reading():
    reading = generate_reading()
    st.session_state.history.append(reading)

    # Keep the latest 500 readings
    st.session_state.history = st.session_state.history[-500:]

    st.session_state.voltage = reading["Voltage (V)"]
    st.session_state.current = reading["Current (A)"]

    return reading


# Create initial demo readings
if not st.session_state.history:
    for _ in range(20):
        add_reading()

df = get_history_df()
latest = df.iloc[-1].to_dict()

# ---------------- PAGE: DASHBOARD ----------------
if page == "Dashboard":

    st.title("⚡ ShadowPulse AI")
    st.subheader("Smart Electrical Monitoring Dashboard")
    st.write(
        "Monitor electrical parameters, observe simulated loads, "
        "and identify unusual readings from one dashboard."
    )

    st.divider()

    # Wokwi simulation link
    st.subheader("🔌 Hardware Simulation")
    st.write(
        "Open the virtual circuit used to demonstrate "
        "the ShadowPulse AI hardware concept."
    )

    st.link_button(
        "▶ Open Wokwi Simulation",
        "https://wokwi.com/projects/478774244281971713",
        type="primary"
    )

    st.divider()

    st.subheader("📊 Current Electrical Readings")
    show_metrics(latest)

    if latest["Status"] == "Normal":
        st.success("System status: Normal")
    else:
        st.warning(f"System alert: {latest['Status']}")

    st.subheader("📈 Recent Power Consumption")
    chart_df = df.tail(20)

    fig = px.line(
        chart_df,
        x="Time",
        y="Power (W)",
        markers=True,
        title="Power Consumption Over Recent Readings"
    )
    fig.update_layout(
        xaxis_title="Time",
        yaxis_title="Power (W)",
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("📋 Latest Readings")
    st.dataframe(
        df.tail(10).iloc[::-1],
        use_container_width=True,
        hide_index=True
    )

    if st.button("🔄 Generate New Reading", type="primary"):
        add_reading()
        st.rerun()


# ---------------- PAGE: LIVE SIMULATION ----------------
elif page == "Live Simulation":

    st.title("🔴 Live Simulation")
    st.write(
        "Generate changing sample electrical readings "
        "to demonstrate how monitoring works."
    )

    col1, col2 = st.columns(2)

    with col1:
        if st.button("▶ Generate Reading", type="primary"):
            reading = add_reading()
            st.success("New simulated reading generated.")
            st.rerun()

    with col2:
        if st.button("⚠ Generate Test Alert"):
            reading = {
                "Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Voltage (V)": 250.0,
                "Current (A)": 8.0,
                "Power (W)": 2000.0,
                "Energy (kWh)": 2.0,
                "Status": "High Voltage / High Load"
            }
            st.session_state.history.append(reading)
            st.session_state.history = st.session_state.history[-500:]
            st.warning("Test alert reading added.")
            st.rerun()

    st.divider()

    latest = get_history_df().iloc[-1].to_dict()
    show_metrics(latest)

    st.subheader("Hardware Simulation")
    st.write(
        "Use this button to view the circuit simulation separately."
    )
    st.link_button(
        "Open Wokwi Circuit",
        "https://wokwi.com/projects/478774244281971713"
    )

    st.info(
        "This page generates simulated values. It does not "
        "automatically receive sensor data from Wokwi."
    )


# ---------------- PAGE: LOAD ANALYSIS ----------------
elif page == "Load Analysis":

    st.title("⚙️ Electrical Load Analysis")
    st.write("Review the power usage of the simulated electrical load.")

    df = get_history_df()

    if not df.empty:
        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Average Power",
            f"{df['Power (W)'].mean():.2f} W"
        )
        col2.metric(
            "Maximum Power",
            f"{df['Power (W)'].max():.2f} W"
        )
        col3.metric(
            "Minimum Power",
            f"{df['Power (W)'].min():.2f} W"
        )

        fig = px.bar(
            df.tail(20),
            x="Time",
            y="Power (W)",
            title="Recent Load Profile"
        )
        st.plotly_chart(fig, use_container_width=True)

        fig2 = px.scatter(
            df,
            x="Current (A)",
            y="Power (W)",
            color="Status",
            title="Current vs Power"
        )
        st.plotly_chart(fig2, use_container_width=True)

        st.subheader("Load Interpretation")

        if df.iloc[-1]["Power (W)"] > st.session_state.threshold:
            st.warning(
                "The latest simulated power is above the configured "
                "threshold. Check the load in a real deployment."
            )
        else:
            st.success(
                "The latest simulated power is within the configured "
                "demo threshold."
            )


# ---------------- PAGE: ENERGY ANALYTICS ----------------
elif page == "Energy Analytics":

    st.title("🔋 Energy Analytics")
    st.write("Explore energy readings and estimated electricity cost.")

    df = get_history_df()

    col1, col2 = st.columns(2)

    with col1:
        hours = st.number_input(
            "Estimated operating hours",
            min_value=1,
            max_value=24,
            value=8
        )

    with col2:
        tariff = st.number_input(
            "Electricity tariff (₹ per kWh)",
            min_value=0.0,
            value=8.0,
            step=0.5
        )

    avg_power_kw = df["Power (W)"].mean() / 1000
    estimated_energy = avg_power_kw * hours
    estimated_cost = estimated_energy * tariff

    col1, col2, col3 = st.columns(3)
    col1.metric("Average Load", f"{avg_power_kw:.3f} kW")
    col2.metric("Estimated Energy", f"{estimated_energy:.3f} kWh")
    col3.metric("Estimated Cost", f"₹{estimated_cost:.2f}")

    st.caption(
        "Cost is an estimate based on the simulated average load "
        "and the operating hours entered above."
    )

    fig = px.area(
        df.tail(30),
        x="Time",
        y="Energy (kWh)",
        title="Energy Per Simulated Reading"
    )
    st.plotly_chart(fig, use_container_width=True)


# ---------------- PAGE: ANOMALY ALERTS ----------------
elif page == "Anomaly Alerts":

    st.title("🚨 Anomaly Alerts")
    st.write(
        "Review simulated readings that cross configured "
        "voltage or power thresholds."
    )

    df = get_history_df()

    voltage_low = 220
    voltage_high = 240

    alerts = df[
        (df["Voltage (V)"] < voltage_low)
        | (df["Voltage (V)"] > voltage_high)
        | (df["Power (W)"] > st.session_state.threshold)
    ].copy()

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Readings", len(df))
    col2.metric("Alert Readings", len(alerts))
    col3.metric(
        "Alert Percentage",
        f"{(len(alerts) / max(len(df), 1)) * 100:.1f}%"
    )

    if alerts.empty:
        st.success("No threshold alerts in the current demo history.")
    else:
        st.warning(
            "Some simulated readings crossed the configured "
            "thresholds. These are demonstration alerts."
        )
        st.dataframe(
            alerts.iloc[::-1],
            use_container_width=True,
            hide_index=True
        )

    st.subheader("Alert Distribution")

    if not alerts.empty:
        alert_counts = alerts["Status"].value_counts().reset_index()
        alert_counts.columns = ["Status", "Count"]

        fig = px.pie(
            alert_counts,
            names="Status",
            values="Count",
            title="Distribution of Alert Statuses"
        )
        st.plotly_chart(fig, use_container_width=True)


# ---------------- PAGE: HISTORY ----------------
elif page == "History":

    st.title("📜 Reading History")
    st.write("View and export simulated electrical readings.")

    df = get_history_df()

    if df.empty:
        st.info("No readings available.")
    else:
        st.dataframe(
            df.iloc[::-1],
            use_container_width=True,
            hide_index=True
        )

        csv_data = df.to_csv(index=False).encode("utf-8")

        st.download_button(
            "⬇️ Download History as CSV",
            data=csv_data,
            file_name="shadowpulse_history.csv",
            mime="text/csv"
        )

        if st.button("🗑️ Clear History"):
            st.session_state.history = []
            st.rerun()


# ---------------- PAGE: SETTINGS ----------------
elif page == "Settings":

    st.title("🛠️ Settings")
    st.write("Configure demonstration alert settings.")

    st.session_state.threshold = st.number_input(
        "High power threshold (W)",
        min_value=100.0,
        max_value=10000.0,
        value=float(st.session_state.threshold),
        step=50.0
    )

    st.markdown("**Voltage alert limits**")
    st.write("Low voltage: below 220 V")
    st.write("High voltage: above 240 V")

    st.divider()

    st.subheader("Hardware Simulation Link")
    st.link_button(
        "Open Wokwi Simulation",
        "https://wokwi.com/projects/478774244281971713"
    )

    st.subheader("About ShadowPulse AI")
    st.write(
        "ShadowPulse AI is a prototype dashboard concept for "
        "electrical monitoring, load analysis, energy estimation, "
        "and threshold-based anomaly alerts."
    )

    st.info(
        "This prototype uses synthetic data and rule-based alerts. "
        "It does not currently use physical sensors, a trained AI model, "
        "or a live Wokwi-to-Streamlit data connection."
    )

# ---------------- FOOTER ----------------
st.divider()
st.caption(
    "ShadowPulse AI | Educational prototype | "
    "Simulated data only — not for electrical safety decisions."
)
