import io
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

# ==================================================
# PAGE CONFIGURATION
# ==================================================
st.set_page_config(
    page_title="ShadowPulse AI",
    page_icon="⚡",
    layout="wide"
)

# ==================================================
# HIGH-CONTRAST DASHBOARD DESIGN
# ==================================================
st.markdown("""
<style>
.stApp {
    background-color: #080F1E;
    color: #F8FAFC;
}
[data-testid="stSidebar"] {
    background-color: #111C30;
}
h1, h2, h3, p, label, li {
    color: #F8FAFC !important;
}
[data-testid="stMetric"] {
    background: #162641;
    border: 1px solid #405778;
    padding: 18px;
    border-radius: 12px;
}
[data-testid="stMetricLabel"] {
    color: #CBD5E1 !important;
}
[data-testid="stMetricValue"] {
    color: #FFFFFF !important;
}
div.stButton > button {
    background-color: #2563EB;
    color: #FFFFFF;
    border: 1px solid #60A5FA;
    border-radius: 8px;
    font-weight: bold;
    min-height: 44px;
}
div.stButton > button:hover {
    background-color: #1D4ED8;
    color: #FFFFFF;
}
[data-testid="stFileUploader"] {
    background: #111C30;
    border: 1px dashed #60A5FA;
    padding: 12px;
    border-radius: 12px;
}
</style>
""", unsafe_allow_html=True)

# ==================================================
# HEADER
# ==================================================
st.title("⚡ ShadowPulse AI")
st.subheader("Intelligent Energy Simulation & Risk Monitoring")
st.write(
    "Upload your sensor dataset, simulate unusual operating "
    "conditions, and compare the results using Machine Learning."
)

st.caption(
    "Simulation prototype | Python | Streamlit | Isolation Forest"
)

# ==================================================
# SIDEBAR
# ==================================================
with st.sidebar:
    st.title("⚡ ShadowPulse AI")
    st.divider()

    st.subheader("Simulation Controls")

    anomaly_percent = st.slider(
        "Percentage of readings to modify",
        min_value=1,
        max_value=30,
        value=10,
        step=1
    )

    severity = st.slider(
        "Simulation severity",
        min_value=1.0,
        max_value=5.0,
        value=2.0,
        step=0.5
    )

    contamination = st.slider(
        "Expected ML outlier proportion (%)",
        min_value=1,
        max_value=15,
        value=3
    )

    st.divider()
    st.caption(
        "These settings control a software simulation. "
        "No physical sensor is connected."
    )

# ==================================================
# FILE UPLOAD
# ==================================================
st.header("📁 Step 1: Upload Your Dataset")

uploaded_file = st.file_uploader(
    "Choose a sensor data CSV file",
    type=["csv"]
)

if uploaded_file is None:
    st.info(
        "Upload a CSV file to begin. No simulation or risk "
        "classification will run before you upload data."
    )

    st.subheader("Example CSV structure")

    example = pd.DataFrame({
        "Voltage": [12.0, 12.1, 11.9, 12.2, 12.0],
        "Current": [0.50, 0.52, 0.48, 0.51, 0.49],
        "Power": [6.00, 6.29, 5.71, 6.22, 5.88]
    })

    st.dataframe(example, use_container_width=True)

    st.stop()

# ==================================================
# READ FILE
# ==================================================
try:
    raw_df = pd.read_csv(uploaded_file)
except Exception as exc:
    st.error(f"Unable to read CSV: {exc}")
    st.stop()

raw_df.columns = [str(c).strip() for c in raw_df.columns]
raw_df = raw_df.dropna(how="all").reset_index(drop=True)

if raw_df.empty:
    st.error("The uploaded CSV file is empty.")
    st.stop()

st.success(f"Uploaded successfully: {uploaded_file.name}")

st.subheader("📄 Step 2: Preview Your Data")

st.write(
    f"Rows: **{len(raw_df)}** | "
    f"Columns: **{len(raw_df.columns)}**"
)

st.dataframe(
    raw_df.head(10),
    use_container_width=True,
    hide_index=True
)

# ==================================================
# NUMERIC COLUMN SELECTION
# ==================================================
st.header("🔧 Step 3: Select Sensor Measurements")

excluded_words = [
    "timestamp", "datetime", "date", "time",
    "recordid", "label", "status", "class"
]

numeric_options = []

for col in raw_df.columns:
    name = str(col).lower().replace("_", "").replace(" ", "")

    if any(word in name for word in excluded_words):
        continue

    converted = pd.to_numeric(raw_df[col], errors="coerce")

    if converted.notna().sum() >= 5 and converted.nunique() > 1:
        numeric_options.append(col)

if not numeric_options:
    st.error(
        "No usable numeric sensor columns found. "
        "Please upload a CSV with at least 5 numeric readings "
        "in a measurement column."
    )
    st.stop()

default_cols = [
    col for col in numeric_options
    if any(word in str(col).lower()
           for word in ["voltage", "current", "power", "watt"])
]

if not default_cols:
    default_cols = numeric_options[:min(3, len(numeric_options))]

selected_columns = st.multiselect(
    "Choose columns for ML analysis",
    options=numeric_options,
    default=default_cols
)

if not selected_columns:
    st.warning("Select at least one numeric sensor column.")
    st.stop()

# ==================================================
# PREPARE DATA
# ==================================================
working_df = raw_df[selected_columns].copy()

for col in selected_columns:
    working_df[col] = pd.to_numeric(
        working_df[col], errors="coerce"
    )

working_df = working_df.replace(
    [np.inf, -np.inf], np.nan
)

valid_mask = working_df.notna().all(axis=1)

original = working_df.loc[valid_mask].reset_index(drop=True)

if len(original) < 5:
    st.error(
        "At least 5 complete numeric readings are required "
        "after removing empty or invalid rows."
    )
    st.stop()

if len(original) > 100000:
    st.error(
        "This demo supports up to 100,000 complete readings. "
        "Please upload a smaller CSV file."
    )
    st.stop()

if (original.nunique() <= 1).all():
    st.error(
        "All selected measurements are constant. "
        "Choose columns containing varied readings."
    )
    st.stop()

st.info(
    f"{len(original)} complete readings will be used for simulation."
)

# ==================================================
# RUN SIMULATION
# ==================================================
st.header("🚀 Step 4: Run Simulation")

st.write(
    f"The simulation will modify approximately "
    f"**{anomaly_percent}%** of the uploaded readings, "
    f"with a severity setting of **{severity:.1f}×**."
)

run_simulation = st.button(
    "▶ Run Simulation & Detect Anomalies",
    type="primary",
    use_container_width=True
)

if run_simulation:
    try:
        # Reproducible simulation for consistent demonstrations
        rng = np.random.default_rng(42)

        simulated = original.copy()
        row_count = len(original)

        # Select rows from the uploaded dataset
        number_to_modify = max(
            1,
            int(round(row_count * anomaly_percent / 100))
        )
        number_to_modify = min(number_to_modify, row_count)

        modified_rows = np.sort(
            rng.choice(
                row_count,
                size=number_to_modify,
                replace=False
            )
        )

        # Modify selected measurements relative to the
        # uploaded data's own variation.
        for col in selected_columns:
            std_dev = original[col].std()

            if pd.isna(std_dev) or std_dev == 0:
                continue

            directions = rng.choice(
                [-1.0, 1.0],
                size=number_to_modify
            )

            changes = directions * std_dev * severity

            simulated.loc[modified_rows, col] = (
                original.loc[modified_rows, col].to_numpy()
                + changes
            )

        # Scale features for ML
        scaler = StandardScaler()

        scaled_original = scaler.fit_transform(original)
        scaled_simulated = scaler.transform(simulated)

        # Train on the uploaded dataset and score both datasets
        model = IsolationForest(
            n_estimators=200,
            contamination=contamination / 100.0,
            random_state=42
        )

        model.fit(scaled_original)

        original_predictions = model.predict(scaled_original)
        simulated_predictions = model.predict(scaled_simulated)

        original_scores = model.decision_function(scaled_original)
        simulated_scores = model.decision_function(scaled_simulated)

        # Build results
        results = simulated.copy()

        results.insert(
            0, "Reading Number", np.arange(1, row_count + 1)
        )

        results["Scenario"] = "Original / Unmodified"

        results.loc[modified_rows, "Scenario"] = (
            "Simulated Change"
        )

        results["Original ML Result"] = np.where(
            original_predictions == -1,
            "Unusual",
            "Normal"
        )

        results["Simulated ML Result"] = np.where(
            simulated_predictions == -1,
            "Unusual",
            "Normal"
        )

        results["Original ML Score"] = np.round(
            original_scores, 4
        )

        results["Simulated ML Score"] = np.round(
            simulated_scores, 4
        )

        results["Injected Change"] = "No"

        results.loc[modified_rows, "Injected Change"] = "Yes"

        # Demo risk category based on fraction flagged by ML.
        flagged_percent = (
            np.mean(simulated_predictions == -1) * 100
        )

        if flagged_percent >= 15:
            risk_level = "HIGH"
        elif flagged_percent >= 5:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"

        st.session_state["sp_results"] = results
        st.session_state["sp_filename"] = uploaded_file.name
        st.session_state["sp_selected"] = list(selected_columns)
        st.session_state["sp_modified"] = int(number_to_modify)
        st.session_state["sp_flagged"] = int(
            np.sum(simulated_predictions == -1)
        )
        st.session_state["sp_original_flagged"] = int(
            np.sum(original_predictions == -1)
        )
        st.session_state["sp_risk"] = risk_level
        st.session_state["sp_anomaly_percent"] = anomaly_percent
        st.session_state["sp_severity"] = severity

    except Exception as exc:
        st.error(f"Simulation failed: {exc}")

# ==================================================
# DISPLAY RESULTS
# ==================================================
if (
    "sp_results" in st.session_state
    and st.session_state.get("sp_filename") == uploaded_file.name
    and st.session_state.get("sp_selected") == list(selected_columns)
):
    results = st.session_state["sp_results"]

    st.divider()
    st.header("📊 Step 5: Simulation Results")

    total = len(results)
    flagged = st.session_state["sp_flagged"]
    baseline_flagged = st.session_state["sp_original_flagged"]

    actual_flagged_percent = flagged / total * 100

    m1, m2, m3, m4 = st.columns(4)

    m1.metric("Readings Analysed", total)
    m2.metric("Readings Modified", st.session_state["sp_modified"])
    m3.metric("ML Unusual Readings", flagged)
    m4.metric("ML Unusual Share", f"{actual_flagged_percent:.1f}%")

    risk_level = st.session_state["sp_risk"]

    st.subheader("🚦 Overall Simulation Risk")

    if risk_level == "HIGH":
        st.error(
            f"HIGH REVIEW PRIORITY — {actual_flagged_percent:.1f}% "
            "of simulated readings were flagged by the ML model."
        )
    elif risk_level == "MEDIUM":
        st.warning(
            f"MEDIUM REVIEW PRIORITY — {actual_flagged_percent:.1f}% "
            "of simulated readings were flagged by the ML model."
        )
    else:
        st.success(
            f"LOW REVIEW PRIORITY — {actual_flagged_percent:.1f}% "
            "of simulated readings were flagged by the ML model."
        )

    st.caption(
        "Risk categories are demo review thresholds, not validated "
        "electrical risk probabilities. An ML outlier is not proof "
        "of a real fault."
    )

    # --------------------------------------------------
    # BEFORE VS AFTER
    # --------------------------------------------------
    st.subheader("📈 Original vs Simulated Data")

    chart_col = st.selectbox(
        "Select measurement for comparison",
        options=selected_columns,
        key="comparison_column"
    )

    comparison = pd.DataFrame({
        "Reading Number": results["Reading Number"],
        "Original": original[chart_col].to_numpy(),
        "Simulated": results[chart_col].to_numpy()
    })

    comparison_long = comparison.melt(
        id_vars="Reading Number",
        var_name="Dataset",
        value_name=chart_col
    )

    fig = px.line(
        comparison_long,
        x="Reading Number",
        y=chart_col,
        color="Dataset",
        color_discrete_map={
            "Original": "#22C55E",
            "Simulated": "#F43F5E"
        },
        title=f"{chart_col}: Original vs Simulated",
        template="plotly_dark"
    )

    fig.update_layout(
        paper_bgcolor="#080F1E",
        plot_bgcolor="#111C30",
        font_color="#F8FAFC",
        legend_title_text="Dataset"
    )

    st.plotly_chart(fig, use_container_width=True)

    # --------------------------------------------------
    # ML RESULT DISTRIBUTION
    # --------------------------------------------------
    st.subheader("🧠 ML Anomaly Detection")

    left, right = st.columns(2)

    with left:
        st.markdown("**Original dataset**")
        st.metric("Originally flagged", baseline_flagged)

    with right:
        st.markdown("**Simulated dataset**")
        st.metric("Flagged after simulation", flagged)

    st.caption(
        "Isolation Forest is trained on the uploaded data. "
        "Its outlier proportion depends on the selected model setting "
        "and the distribution of the uploaded measurements."
    )

    # --------------------------------------------------
    # TABLE
    # --------------------------------------------------
    st.subheader("📋 Detailed Results")

    def colour_ml(value):
        if value == "Unusual":
            return (
                "background-color: #991B1B; "
                "color: #FFFFFF; font-weight: bold"
            )
        return (
            "background-color: #166534; "
            "color: #FFFFFF; font-weight: bold"
        )

    styled_results = results.style.map(
        colour_ml,
        subset=["Simulated ML Result"]
    )

    st.dataframe(
        styled_results,
        use_container_width=True,
        hide_index=True
    )

    # --------------------------------------------------
    # DOWNLOAD
    # --------------------------------------------------
    st.subheader("📥 Export Simulation Report")

    csv_data = results.to_csv(index=False).encode("utf-8")

    st.download_button(
        "⬇ Download Full Simulation Results (CSV)",
        data=csv_data,
        file_name="shadowpulse_simulation_results.csv",
        mime="text/csv",
        use_container_width=True
    )

    if st.button("🔄 Reset Simulation"):
        st.session_state.pop("sp_results", None)
        st.session_state.pop("sp_filename", None)
        st.session_state.pop("sp_selected", None)
        st.session_state.pop("sp_modified", None)
        st.session_state.pop("sp_flagged", None)
        st.session_state.pop("sp_original_flagged", None)
        st.session_state.pop("sp_risk", None)
        st.session_state.pop("sp_anomaly_percent", None)
        st.session_state.pop("sp_severity", None)
        st.rerun()

# ==================================================
# FOOTER
# ==================================================
st.divider()

st.caption(
    "ShadowPulse AI | Educational simulation prototype | "
    "Uses uploaded data and synthetic modifications. "
    "Not a substitute for real electrical safety monitoring."
)
