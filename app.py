
import io
import re

import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="ShadowPulse AI",
    page_icon="⚡",
    layout="wide"
)

# ---------------- HIGH-CONTRAST STYLE ----------------
st.markdown("""
<style>
.stApp {
    background: #080F1E;
    color: #F8FAFC;
}
[data-testid="stSidebar"] {
    background: #111C30;
}
h1, h2, h3, p, label, span {
    color: #F8FAFC;
}
[data-testid="stMetric"] {
    background: #162641;
    border: 1px solid #3B5275;
    padding: 18px;
    border-radius: 12px;
}
[data-testid="stMetricValue"] {
    color: #FFFFFF;
}
div.stButton > button {
    background: #2563EB;
    color: white;
    border: 1px solid #60A5FA;
    border-radius: 8px;
    font-weight: 700;
}
div.stButton > button:hover {
    background: #1D4ED8;
    color: white;
    border: 1px solid #93C5FD;
}
div[data-testid="stFileUploader"] {
    background: #111C30;
    border: 1px dashed #60A5FA;
    padding: 14px;
    border-radius: 12px;
}
.small-note {
    color: #CBD5E1;
    font-size: 14px;
}
</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------
st.title("⚡ ShadowPulse AI")
st.markdown(
    "### Intelligent Energy Monitoring & Anomaly Detection"
)
st.markdown(
    '<p class="small-note">Upload your sensor CSV file '
    'to analyse readings using machine learning.</p>',
    unsafe_allow_html=True
)

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.title("⚡ ShadowPulse AI")
    st.markdown("---")
    st.subheader("Analysis Settings")
    st.write("**Detection algorithm:** Isolation Forest")
    contamination_pct = st.slider(
        "Expected unusual readings (%)",
        min_value=1,
        max_value=10,
        value=3,
        help=(
            "This is the model's assumed proportion of anomalies, "
            "not a measured risk probability."
        )
    )
    st.caption(
        "No simulated readings are generated. "
        "Only your uploaded file is analysed."
    )

# ---------------- FILE UPLOAD ----------------
st.subheader("📁 Upload Sensor Data")

uploaded_file = st.file_uploader(
    "Choose a CSV file containing sensor readings",
    type=["csv"],
    help="CSV should contain at least 5 rows and numeric sensor columns."
)

st.info(
    "Suggested columns: Voltage, Current, Power. "
    "Other numeric sensor measurements can also be analysed."
)

# ---------------- COLUMN DETECTION ----------------
def normalise_name(name):
    return re.sub(r"[^a-z0-9]", "", str(name).lower())


def prepare_features(data):
    """Find useful numeric sensor columns and clean the data."""
    df = data.copy()
    df.columns = [str(c).strip() for c in df.columns]

    # Remove completely empty rows and columns
    df = df.dropna(how="all").dropna(axis=1, how="all")

    if df.empty:
        raise ValueError("The uploaded CSV has no usable data.")

    normalised = {
        normalise_name(col): col for col in df.columns
    }

    # Recognise common voltage/current/power column names
    aliases = {
        "Voltage": [
            "voltage", "voltagev", "voltagevolt", "v"
        ],
        "Current": [
            "current", "currenta", "currentamp", "amperage", "a"
        ],
        "Power": [
            "power", "powerw", "watt", "wattage"
        ]
    }

    selected = []

    for standard_name, possible_names in aliases.items():
        for alias in possible_names:
            if alias in normalised:
                original = normalised[alias]
                df[original] = pd.to_numeric(
                    df[original], errors="coerce"
                )
                if df[original].notna().any():
                    selected.append(original)
                    break

    # If known sensor fields are absent, use other numeric columns
    if not selected:
        excluded_words = (
            "time", "date", "timestamp", "index", "id",
            "label", "status", "risk", "class", "target"
        )

        for col in df.columns:
            name = normalise_name(col)

            if any(word in name for word in excluded_words):
                continue

            converted = pd.to_numeric(df[col], errors="coerce")

            if converted.notna().sum() >= 5:
                df[col] = converted
                selected.append(col)

    # Derive power only when voltage and current are available
    # and the uploaded file has no usable power column.
    selected_names = [normalise_name(c) for c in selected]

    if "power" not in selected_names:
        voltage_col = next(
            (c for c in selected
             if normalise_name(c) in
             ["voltage", "voltagev", "voltagevolt", "v"]),
            None
        )
        current_col = next(
            (c for c in selected
             if normalise_name(c) in
             ["current", "currenta", "currentamp", "amperage", "a"]),
            None
        )

        if voltage_col and current_col:
            df["Derived Power (W)"] = (
                df[voltage_col] * df[current_col]
            )
            selected.append("Derived Power (W)")

    if not selected:
        raise ValueError(
            "No usable numeric sensor columns found. "
            "Include numeric Voltage, Current, Power, "
            "or other sensor measurement columns."
        )

    features = df[selected].replace([np.inf, -np.inf], np.nan)

    # Drop rows missing any selected feature
    valid_mask = features.notna().all(axis=1)
    clean_features = features.loc[valid_mask].copy()
    clean_data = df.loc[valid_mask].copy()

    if len(clean_features) < 5:
        raise ValueError(
            "At least 5 complete sensor readings are required."
        )

    if len(selected) > 1:
        # Remove constant features that do not help detection
        varying = clean_features.nunique(dropna=True) > 1
        clean_features = clean_features.loc[:, varying]

    if clean_features.shape[1] == 0:
        raise ValueError(
            "All selected sensor columns have constant values. "
            "More varied readings are needed for anomaly detection."
        )

    return clean_data, clean_features, selected


# ---------------- ANALYSIS ----------------
if uploaded_file is not None:
    st.markdown("---")

    try:
        raw_df = pd.read_csv(uploaded_file)

        st.subheader("📄 Uploaded Data Preview")
        st.caption(
            f"File: {uploaded_file.name} · "
            f"{len(raw_df)} rows · {len(raw_df.columns)} columns"
        )
        st.dataframe(
            raw_df.head(10),
            use_container_width=True,
            hide_index=True
        )

        if st.button(
            "🔍 Analyse Uploaded File",
            type="primary",
            use_container_width=True
        ):
            clean_data, features, selected_columns = prepare_features(
                raw_df
            )

            # Scale features so measurements with different units
            # can contribute more comparably to the model.
            scaler = StandardScaler()
            scaled_features = scaler.fit_transform(features)

            model = IsolationForest(
                n_estimators=200,
                contamination=contamination_pct / 100.0,
                random_state=42
            )

            predictions = model.fit_predict(scaled_features)
            scores = model.decision_function(scaled_features)

            results = clean_data.copy()
            results["ML Score"] = scores
            results["ML Result"] = np.where(
                predictions == -1,
                "Unusual",
                "Normal"
            )

            # Relative severity ranks among flagged readings.
            # These are review categories, not probabilities.
            flagged = predictions == -1
            results["Risk Level"] = "LOW"

            if flagged.any():
                flagged_scores = scores[flagged]
                cutoff = np.quantile(flagged_scores, 0.5)

                results.loc[flagged, "Risk Level"] = np.where(
                    flagged_scores <= cutoff,
                    "HIGH",
                    "MEDIUM"
                )

            st.session_state["shadowpulse_results"] = results
            st.session_state["shadowpulse_features"] = list(
                features.columns
            )
            st.session_state["shadowpulse_filename"] = uploaded_file.name

        # Display results only after the user starts analysis
        if (
            "shadowpulse_results" in st.session_state
            and st.session_state.get("shadowpulse_filename")
            == uploaded_file.name
        ):
            results = st.session_state["shadowpulse_results"]
            feature_cols = st.session_state["shadowpulse_features"]

            total = len(results)
            unusual = int((results["ML Result"] == "Unusual").sum())
            normal = total - unusual
            percentage = unusual / total * 100 if total else 0

            st.markdown("---")
            st.subheader("📊 Analysis Summary")

            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Readings Analysed", total)
            m2.metric("Normal Readings", normal)
            m3.metric("Unusual Readings", unusual)
            m4.metric("Unusual Share", f"{percentage:.1f}%")

            if unusual:
                st.warning(
                    f"Review recommended: the model flagged "
                    f"{unusual} reading(s) as unusual. "
                    "This does not prove an electrical fault."
                )
            else:
                st.success(
                    "No unusual readings were flagged by this model. "
                    "This does not guarantee the equipment is safe."
                )

            # Clear status colours with readable text
            st.subheader("🚦 Detection Results")

            def colour_status(value):
                if value == "Unusual":
                    return (
                        "background-color: #7F1D1D; "
                        "color: #FFFFFF; font-weight: bold"
                    )
                return (
                    "background-color: #14532D; "
                    "color: #FFFFFF; font-weight: bold"
                )

            def colour_risk(value):
                colours = {
                    "HIGH": "#B91C1C",
                    "MEDIUM": "#92400E",
                    "LOW": "#166534"
                }
                return (
                    f"background-color: {colours.get(value, '#334155')}; "
                    "color: #FFFFFF; font-weight: bold"
                )

            styled = results.style.map(
                colour_status, subset=["ML Result"]
            ).map(
                colour_risk, subset=["Risk Level"]
            )

            st.dataframe(
                styled,
                use_container_width=True,
                hide_index=True
            )

            st.subheader("📈 Sensor Trends")

            chart_column = st.selectbox(
                "Choose a measurement",
                feature_cols
            )

            chart_df = results[[chart_column, "ML Result"]].copy()
            chart_df["Reading Number"] = np.arange(1, len(results) + 1)

            fig = px.scatter(
                chart_df,
                x="Reading Number",
                y=chart_column,
                color="ML Result",
                color_discrete_map={
                    "Normal": "#22C55E",
                    "Unusual": "#F43F5E"
                },
                title=f"{chart_column} — normal vs unusual readings",
                template="plotly_dark"
            )
            fig.update_layout(
                paper_bgcolor="#080F1E",
                plot_bgcolor="#111C30",
                font_color="#F8FAFC"
            )
            st.plotly_chart(fig, use_container_width=True)

            st.subheader("📥 Export Results")

            csv_bytes = results.to_csv(index=False).encode("utf-8")

            st.download_button(
                "Download Analysis Results (CSV)",
                data=csv_bytes,
                file_name="shadowpulse_analysis.csv",
                mime="text/csv",
                use_container_width=True
            )

            st.caption(
                "ML scores are model decision scores, not risk probabilities. "
                "Risk labels are relative review categories for this dataset. "
                "Validate with labelled real-world data before relying on results."
            )

    except Exception as exc:
        st.error(
            "The file could not be analysed. "
            "Check that it is a valid CSV with numeric sensor readings."
        )
        st.caption(f"Details: {exc}")

else:
    st.markdown("---")
    st.subheader("Waiting for your sensor file")
    st.info(
        "Upload a CSV file above. The dashboard will not generate "
        "readings or display a risk alert until you analyse a file."
    )

    st.markdown("""
    **Example CSV format**

    | Voltage | Current | Power |
    |---:|---:|---:|
    | 12.0 | 0.50 | 6.0 |
    | 12.1 | 0.52 | 6.29 |
    | 11.9 | 0.48 | 5.71 |
    | 12.2 | 0.51 | 6.22 |
    | 12.0 | 0.49 | 5.88 |
    """)
