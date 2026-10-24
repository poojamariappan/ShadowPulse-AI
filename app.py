import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="ShadowPulse AI",
    page_icon="⚡",
    layout="wide"
)

WOKWI_URL = "https://wokwi.com/projects/478774244281971713"

st.markdown("""
<style>
.stApp {
    background-color: #081522;
    color: #F5F7FA;
}
[data-testid="stSidebar"] {
    background-color: #11283D;
}
h1, h2, h3, p, label {
    color: #F5F7FA;
}
.stButton button, .stLinkButton a {
    background-color: #36E0C1;
    color: #081522 !important;
    border: none;
    border-radius: 8px;
    font-weight: bold;
}
.panel {
    background: #11283D;
    border: 1px solid #28465D;
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 15px;
}
.small {
    color: #B5C8D8;
    font-size: 14px;
}
</style>
""", unsafe_allow_html=True)

st.title("⚡ ShadowPulse AI")
st.subheader("Virtual Electrical Load Monitoring")
st.write(
    "ESP32 simulation dashboard powered by your Wokwi project."
)

st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Choose page",
    ["Dashboard", "Wokwi Simulation", "About Project"]
)

if page == "Dashboard":
    st.markdown("### Project Overview")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div class="panel">
            <h3>ESP32 Virtual Sensor</h3>
            <p class="small">
            Reads a simulated analog input on GPIO 32.
            </p>
            <h2>GPIO 32</h2>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="panel">
            <h3>Monitoring Logic</h3>
            <p class="small">
            Demo current is calculated from the ADC value.
            </p>
            <h2>0.90 A threshold</h2>
        </div>
        """, unsafe_allow_html=True)

    st.info(
        "This dashboard links to your Wokwi simulation. "
        "It does not receive live sensor readings automatically."
    )

    st.link_button(
        "▶ Open Wokwi Simulation",
        WOKWI_URL,
        use_container_width=True
    )

elif page == "Wokwi Simulation":
    st.markdown("### Your ESP32 Simulation")
    st.write(
        "Try opening the simulator below. If it does not load, "
        "open the project directly using the button."
    )

    components.iframe(
        WOKWI_URL + "?embed=1",
        height=600,
        scrolling=True
    )

    st.link_button(
        "Open Wokwi in a New Tab",
        WOKWI_URL,
        use_container_width=True
    )

    st.caption(
        "Wokwi embedding may be restricted by the browser or "
        "Wokwi. The direct project link is the fallback."
    )

elif page == "About Project":
    st.markdown("### About ShadowPulse AI")

    st.markdown("""
    <div class="panel">
        <h3>Project Purpose</h3>
        <p>
        Demonstrate virtual electrical-load monitoring using an
        ESP32-based simulation.
        </p>
        <h3>How the Wokwi code works</h3>
        <ul>
            <li>Reads analog input from GPIO 32.</li>
            <li>Calculates demo current from the ADC value.</li>
            <li>Assumes a demo voltage of 5 V.</li>
            <li>Calculates demo power using voltage × current.</li>
            <li>Labels readings as normal or unusual based on 0.90 A.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    st.link_button(
        "View Wokwi Project",
        WOKWI_URL
    )

    st.warning(
        "Current and voltage are simulated values, not readings "
        "from a physical current sensor. This project is a demo, "
        "not a certified electrical protection system."
    )
