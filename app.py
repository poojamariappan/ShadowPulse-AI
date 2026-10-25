
import streamlit as st
import pandas as pd
import random
from datetime import datetime

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="ShadowPulse AI",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------- CONSTANTS ----------------
WOKWI_URL = "https://wokwi.com/projects/478774244281971713"

# ---------------- SESSION STATE ----------------
if "history" not in st.session_state:
    st.session_state.history = []

if "threshold" not in st.session_state:
    st.session_state.threshold = 1000.0

# ---------------- CSS ----------------


def show_metrics(reading):
    st.markdown("""
    <style>
    .metric-card {
        padding: 20px;
        border-radius: 16px;
        min-height: 145px;
        border: 1px solid transparent;
        box-shadow: 0 5px 14px rgba(15, 23, 42, 0.06);
    }

    .metric-label {
        font-size: 16px;
        font-weight: 600;
        margin-bottom: 12px;
    }

    .metric-value {
        font-size: 27px;
        font-weight: 750;
        margin-bottom: 9px;
    }

    .metric-status {
        font-size: 13px;
        font-weight: 500;
    }

    .voltage-card {
        background: #e0f2fe;
        border-color: #bfdbfe;
        color: #075985;
    }

    .current-card {
        background: #f3e8ff;
        border-color: #e9d5ff;
        color: #6b21a8;
    }

    .power-card {
        background: #ffedd5;
        border-color: #fed7aa;
        color: #9a3412;
    }

    .energy-card {
        background: #d1fae5;
        border-color: #a7f3d0;
        color: #065f46;
    }
    </style>
    """, unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)

    cards = [
        (c1, "voltage-card", "⚡", "Voltage",
         f"{reading['Voltage (V)']} V", "Normal range"),
        (c2, "current-card", "◉", "Current",
         f"{reading['Current (A)']} A", "Sensor reading"),
        (c3, "power-card", "〽️", "Power",
         f"{reading['Power (W)']} W", "Power consumption"),
        (c4, "energy-card", "🍃", "Energy",
         f"{reading['Energy (kWh)']} kWh", "Energy reading")
    ]

    for col, css_class, emoji, label, value, status in cards:
        with col:
            st.markdown(
                f"""
                <div class="metric-card {css_class}">
                    <div class="metric-label">{emoji} {label}</div>
                    <div class="metric-value">{value}</div>
                    <div class="metric-status">● {status}</div>
                </div>
                """,
                unsafe_allow_html=True
            )


# ---------------- SIDEBAR ----------------
st.sidebar.title("⚡ ShadowPulse AI")
st.sidebar.caption("Smart Electrical Monitoring")

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
st.sidebar.success("Demo system active")
st.sidebar.caption("Electrical monitoring prototype")

# ---------------- FUNCTIONS ----------------
def generate_reading():
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


def add_reading():
    reading = generate_reading()
    st.session_state.history.append(reading)
    st.session_state.history = st.session_state.history[-500:]
    return reading


def get_data():
    if not st.session_state.history:
        add_reading()
    return pd.DataFrame(st.session_state.history)


def show_metrics(reading):
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Voltage", f"{reading['Voltage (V)']} V")
    c2.metric("Current", f"{reading['Current (A)']} A")
    c3.metric("Power", f"{reading['Power (W)']} W")
    c4.metric("Energy", f"{reading['Energy (kWh)']} kWh")


# Generate initial demo data
if not st.session_state.history:
    for _ in range(10):
        add_reading()

df = get_data()
latest = df.iloc[-1].to_dict()

# ---------------- DASHBOARD ----------------
if page == "Dashboard":

    st.title("⚡ ShadowPulse AI")
    st.subheader("Smart Electrical Monitoring Dashboard")

    st.write(
        "Monitor electrical readings and review simulated "
        "power consumption and anomaly alerts."
    )

    st.divider()
    st.subheader("🔌 Hardware Simulation")

    st.write("Open the virtual circuit used for this project.")

    st.link_button(
        "▶ Open Wokwi Simulation",
        WOKWI_URL,
        type="primary",
        use_container_width=True
    )

    st.divider()
    st.subheader("📊 Current Readings")
    show_metrics(latest)

    if latest["Status"] == "Normal":
        st.success("System status: Normal")
    else:
        st.warning(f"System alert: {latest['Status']}")

    st.subheader("📈 Recent Power Consumption")
    st.line_chart(df.set_index("Time")["Power (W)"])

    st.subheader("📋 Recent Readings")
    st.dataframe(df.tail(10).iloc[::-1], use_container_width=True)

    if st.button("🔄 Generate New Reading"):
        add_reading()
        st.rerun()


# ---------------- LIVE SIMULATION ----------------
elif page == "Live Simulation":

    # Clicking this page automatically opens Wokwi
    st.title("🔴 Live Hardware Simulation")

    st.info("Opening your Wokwi circuit...")

    st.link_button(
        "▶ Open Wokwi Simulation",
        WOKWI_URL,
        type="primary",
        use_container_width=True
    )

    st.markdown(
        f"""
        If the circuit does not open automatically, use the button above
        or [open the Wokwi project directly]({WOKWI_URL}).
        """
    )

    st.divider()

    st.subheader("📊 Simulated Electrical Readings")
    show_metrics(latest)

    st.warning(
        "Note: These values are generated demo readings. "
        "They are not live values received from Wokwi."
    )


# ---------------- LOAD ANALYSIS ----------------
elif page == "Load Analysis":

    st.title("⚙️ Load Analysis")
    st.write("Analyse simulated electrical load.")

    c1, c2, c3 = st.columns(3)
    c1.metric("Average Power", f"{df['Power (W)'].mean():.2f} W")
    c2.metric("Maximum Power", f"{df['Power (W)'].max():.2f} W")
    c3.metric("Minimum Power", f"{df['Power (W)'].min():.2f} W")

    st.subheader("Power Consumption")
    st.bar_chart(df.set_index("Time")["Power (W)"])

    st.subheader("Current vs Power")
    st.scatter_chart(
        df,
        x="Current (A)",
        y="Power (W)"
    )


# ---------------- ENERGY ANALYTICS ----------------
elif page == "Energy Analytics":

    st.title("🔋 Energy Analytics")

    hours = st.number_input(
        "Estimated operating hours per day",
        min_value=1,
        max_value=24,
        value=8
    )

    tariff = st.number_input(
        "Electricity cost (₹ per kWh)",
        min_value=0.0,
        value=8.0,
        step=0.5
    )

    average_kw = df["Power (W)"].mean() / 1000
    estimated_energy = average_kw * hours
    estimated_cost = estimated_energy * tariff

    c1, c2, c3 = st.columns(3)
    c1.metric("Average Load", f"{average_kw:.3f} kW")
    c2.metric("Estimated Energy", f"{estimated_energy:.3f} kWh")
    c3.metric("Estimated Cost", f"₹{estimated_cost:.2f}")

    st.caption("Cost is estimated from the simulated readings.")

    st.subheader("Energy Readings")
    st.line_chart(df.set_index("Time")["Energy (kWh)"])


# ---------------- ANOMALY ALERTS ----------------
elif page == "Anomaly Alerts":

    st.title("🚨 Anomaly Alerts")

    alerts = df[
        (df["Voltage (V)"] < 220)
        | (df["Voltage (V)"] > 240)
        | (df["Power (W)"] > st.session_state.threshold)
    ]

    c1, c2 = st.columns(2)
    c1.metric("Total Readings", len(df))
    c2.metric("Alert Readings", len(alerts))

    if alerts.empty:
        st.success("No threshold alerts found in current demo readings.")
    else:
        st.warning("Some readings crossed the configured thresholds.")
        st.dataframe(alerts.iloc[::-1], use_container_width=True)

    st.caption(
        "Alerts are based on simple threshold rules, not a trained AI model."
    )


# ---------------- HISTORY ----------------
elif page == "History":

    st.title("📜 Reading History")

    st.dataframe(df.iloc[::-1], use_container_width=True)

    st.download_button(
        "⬇️ Download CSV",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name="shadowpulse_history.csv",
        mime="text/csv"
    )

    if st.button("🗑️ Clear History"):
        st.session_state.history = []
        st.rerun()


# ---------------- SETTINGS ----------------
elif page == "Settings":

    st.title("🛠️ Settings")

    st.session_state.threshold = st.number_input(
        "High power threshold (W)",
        min_value=100.0,
        max_value=10000.0,
        value=float(st.session_state.threshold),
        step=50.0
    )

    st.subheader("Hardware Simulation")
    st.link_button("Open Wokwi Circuit", WOKWI_URL)

    st.subheader("About")
    st.write(
        "ShadowPulse AI is an educational electrical monitoring "
        "dashboard prototype."
    )

    st.info(
        "The current version uses generated sample data. "
        "Live sensor integration is not configured."
    )


# ---------------- FOOTER ----------------
st.divider()
st.caption(
    "ShadowPulse AI | Educational prototype | "
    "Simulated readings only"
)
