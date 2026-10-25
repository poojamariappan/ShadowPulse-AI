
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime

st.set_page_config(
    page_title="ShadowPulse AI",
    page_icon="⚡",
    layout="wide"
)

st.markdown("""
<style>
.stApp {
    background-color: #07111f;
    color: #e8f1ff;
}
[data-testid="stSidebar"] {
    background-color: #0b1728;
}
div[data-testid="stMetric"] {
    background: #102239;
    border: 1px solid #1d4260;
    padding: 15px;
    border-radius: 12px;
}
</style>
""", unsafe_allow_html=True)

st.title("⚡ ShadowPulse AI")
st.caption("Smart Electrical Load & Energy Monitoring System")

# Store data during the current app session
if "history" not in st.session_state:
    st.session_state.history = []

if "alerts" not in st.session_state:
    st.session_state.alerts = []

if "counter" not in st.session_state:
    st.session_state.counter = 0

# Simulated load profiles
loads = {
    "LED Lamp": {"power": 12, "category": "Lighting"},
    "Ceiling Fan": {"power": 65, "category": "Motor"},
    "Laptop Charger": {"power": 90, "category": "Electronics"},
    "Water Pump": {"power": 500, "category": "Motor"},
    "Heater": {"power": 1000, "category": "Heating"},
}

# Sidebar
st.sidebar.title("Control Panel")

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

selected_load = st.sidebar.selectbox(
    "Select Electrical Load",
    list(loads.keys())
)

power_limit = st.sidebar.number_input(
    "Power Alert Threshold (W)",
    min_value=10,
    max_value=10000,
    value=800
)

current_limit = st.sidebar.number_input(
    "Current Alert Threshold (A)",
    min_value=0.1,
    max_value=100.0,
    value=5.0
)

abnormal_mode = st.sidebar.toggle(
    "Simulate Abnormal Load",
    value=False
)


def classify_load(power):
    if power < 30:
        return "Low Power Load"
    elif power < 150:
        return "Small Appliance"
    elif power < 750:
        return "Medium Power Load"
    return "High Power Load"


def generate_reading():
    spec = loads[selected_load]

    voltage = float(np.random.normal(230, 2))

    multiplier = (
        np.random.uniform(1.8, 2.5)
        if abnormal_mode
        else np.random.uniform(0.92, 1.08)
    )

    power = spec["power"] * multiplier
    current = power / max(voltage, 1)

    # Assumption: one generated reading represents one minute
    energy = power / 1000 / 60

    reasons = []

    if voltage < 210 or voltage > 245:
        reasons.append("Voltage outside limits")

    if power > power_limit:
        reasons.append("High power consumption")

    if current > current_limit:
        reasons.append("High current")

    status = "ANOMALY" if reasons else "NORMAL"

    st.session_state.counter += 1

    reading = {
        "Reading": st.session_state.counter,
        "Time": datetime.now().strftime("%H:%M:%S"),
        "Load": selected_load,
        "Category": spec["category"],
        "Voltage (V)": round(voltage, 2),
        "Current (A)": round(current, 3),
        "Power (W)": round(power, 2),
        "Energy (kWh)": round(energy, 6),
        "Load Type": classify_load(power),
        "Status": status,
        "Reason": ", ".join(reasons) if reasons else "Normal"
    }

    st.session_state.history.append(reading)

    if status == "ANOMALY":
        st.session_state.alerts.append(reading.copy())

    return reading


df = pd.DataFrame(st.session_state.history)


# DASHBOARD
if page == "Dashboard":

    st.header("System Dashboard")

    if df.empty:
        st.info(
            "No readings available. Open Live Simulation "
            "and generate your first reading."
        )
    else:
        latest = df.iloc[-1]

        total_energy = df["Energy (kWh)"].sum()
        average_power = df["Power (W)"].mean()
        alert_count = len(st.session_state.alerts)

        c1, c2, c3, c4 = st.columns(4)

        c1.metric(
            "Current Power",
            f"{latest['Power (W)']:.2f} W"
        )

        c2.metric(
            "Total Energy",
            f"{total_energy:.5f} kWh"
        )

        c3.metric(
            "Average Power",
            f"{average_power:.2f} W"
        )

        c4.metric("Total Alerts", alert_count)

        st.subheader("Latest Electrical Reading")

        a, b, c = st.columns(3)

        a.metric("Voltage", f"{latest['Voltage (V)']} V")
        b.metric("Current", f"{latest['Current (A)']} A")
        c.metric("Load", latest["Load"])

        if latest["Status"] == "ANOMALY":
            st.error(f"Anomaly: {latest['Reason']}")
        else:
            st.success("Electrical readings are within configured limits.")

        fig = px.line(
            df,
            x="Reading",
            y="Power (W)",
            markers=True,
            title="Power Consumption Trend"
        )

        st.plotly_chart(fig, use_container_width=True)


# LIVE SIMULATION
elif page == "Live Simulation":

    st.header("Live Load Simulation")

    st.write("Selected load:", selected_load)
    st.write("Nominal power:", loads[selected_load]["power"], "W")

    if st.button("Generate New Reading", type="primary"):
        reading = generate_reading()

        if reading["Status"] == "ANOMALY":
            st.error(f"Alert generated: {reading['Reason']}")
        else:
            st.success("New reading generated successfully.")

    if st.button("Generate 10 Readings"):
        for _ in range(10):
            generate_reading()

        st.success("10 simulated readings generated.")

    if st.button("Reset Simulation"):
        st.session_state.history = []
        st.session_state.alerts = []
        st.session_state.counter = 0
        st.rerun()

    df = pd.DataFrame(st.session_state.history)

    if not df.empty:
        st.subheader("Recent Readings")
        st.dataframe(df.tail(15), use_container_width=True)


# LOAD ANALYSIS
elif page == "Load Analysis":

    st.header("Electrical Load Analysis")

    profile_df = pd.DataFrame([
        {
            "Load": name,
            "Category": data["category"],
            "Nominal Power (W)": data["power"]
        }
        for name, data in loads.items()
    ])

    fig = px.bar(
        profile_df,
        x="Load",
        y="Nominal Power (W)",
        color="Category",
        title="Comparison of Electrical Loads"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Load Classification")

    for name, data in loads.items():
        with st.expander(name):
            st.write("Category:", data["category"])
            st.write("Nominal power:", data["power"], "W")
            st.write(
                "Estimated type:",
                classify_load(data["power"])
            )

    if not df.empty:
        st.subheader("Observed Load Performance")

        summary = df.groupby("Load").agg(
            Readings=("Reading", "count"),
            Average_Power=("Power (W)", "mean"),
            Maximum_Power=("Power (W)", "max"),
            Total_Energy=("Energy (kWh)", "sum")
        ).reset_index()

        st.dataframe(
            summary.round(4),
            use_container_width=True
        )


# ENERGY ANALYTICS
elif page == "Energy Analytics":

    st.header("Energy-Based Analysis")

    if df.empty:
        st.info(
            "Generate readings in Live Simulation "
            "to calculate energy analytics."
        )
    else:
        tariff = st.number_input(
            "Electricity Tariff (₹ per kWh)",
            min_value=0.0,
            value=8.0,
            step=0.5
        )

        total_energy = df["Energy (kWh)"].sum()
        average_power = df["Power (W)"].mean()
        peak_power = df["Power (W)"].max()
        estimated_cost = total_energy * tariff

        c1, c2, c3, c4 = st.columns(4)

        c1.metric("Total Energy", f"{total_energy:.5f} kWh")
        c2.metric("Average Power", f"{average_power:.2f} W")
        c3.metric("Peak Power", f"{peak_power:.2f} W")
        c4.metric("Estimated Cost", f"₹{estimated_cost:.4f}")

        chart_df = df.copy()
        chart_df["Cumulative Energy (kWh)"] = (
            chart_df["Energy (kWh)"].cumsum()
        )

        fig1 = px.line(
            chart_df,
            x="Reading",
            y="Energy (kWh)",
            markers=True,
            title="Energy per Simulated Interval"
        )

        st.plotly_chart(fig1, use_container_width=True)

        fig2 = px.line(
            chart_df,
            x="Reading",
            y="Cumulative Energy (kWh)",
            markers=True,
            title="Cumulative Energy Consumption"
        )

        st.plotly_chart(fig2, use_container_width=True)

        energy_by_load = df.groupby("Load")[
            "Energy (kWh)"
        ].sum().reset_index()

        fig3 = px.pie(
            energy_by_load,
            names="Load",
            values="Energy (kWh)",
            title="Energy Share by Load"
        )

        st.plotly_chart(fig3, use_container_width=True)

        st.caption(
            "Simulation assumption: each reading represents one minute. "
            "Cost is illustrative, not an actual electricity bill."
        )


# ANOMALY ALERTS
elif page == "Anomaly Alerts":

    st.header("Anomaly Detection and Alerts")

    alerts_df = pd.DataFrame(st.session_state.alerts)

    if alerts_df.empty:
        st.success("No anomaly alerts recorded yet.")
        st.info(
            "Turn on Simulate Abnormal Load in the sidebar, "
            "then generate a reading to test alerts."
        )
    else:
        st.error(f"{len(alerts_df)} anomaly alert(s) detected.")

        st.dataframe(
            alerts_df.iloc[::-1],
            use_container_width=True
        )

        st.download_button(
            "Download Alerts CSV",
            alerts_df.to_csv(index=False).encode("utf-8"),
            "shadowpulse_alerts.csv",
            "text/csv"
        )


# HISTORY
elif page == "History":

    st.header("Reading History")

    if df.empty:
        st.info("No readings available yet.")
    else:
        load_filter = st.selectbox(
            "Filter by load",
            ["All Loads"] + list(loads.keys())
        )

        filtered_df = df.copy()

        if load_filter != "All Loads":
            filtered_df = filtered_df[
                filtered_df["Load"] == load_filter
            ]

        st.dataframe(
            filtered_df.iloc[::-1],
            use_container_width=True
        )

        st.download_button(
            "Download Reading History CSV",
            filtered_df.to_csv(index=False).encode("utf-8"),
            "shadowpulse_history.csv",
            "text/csv"
        )


# SETTINGS
elif page == "Settings":

    st.header("System Settings")

    st.write("Power threshold:", power_limit, "W")
    st.write("Current threshold:", current_limit, "A")

    st.subheader("How ShadowPulse AI Works")

    st.markdown("""
    1. Generate simulated voltage, current and power readings.
    2. Estimate the load category from power ranges.
    3. Calculate simulated energy consumption.
    4. Check readings against configured thresholds.
    5. Display alerts, charts and historical readings.
    """)

    st.warning(
        "This is a software simulation. It does not read physical sensors "
        "or use a trained machine-learning model. Readings and history "
        "are stored in the current Streamlit session."
    )

st.sidebar.divider()
st.sidebar.caption("ShadowPulse AI | Simulation Demo")
