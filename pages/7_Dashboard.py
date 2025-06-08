import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from io import BytesIO

st.set_page_config(page_title="Analytics Dashboard", layout="wide")
st.subheader("📊 Human Rights Dashboard")

base_url = "http://127.0.0.1:8000/api/analytics"

# 1️⃣ Violations Pie Chart
try:
    st.markdown("### 🧯 Violation Types Distribution")
    response = requests.get(f"{base_url}/violations")
    if response.status_code == 200:
        data = response.json()
        df = pd.DataFrame({"Violation": list(data.keys()), "Count": list(data.values())})
        fig = px.pie(df, names="Violation", values="Count", hole=0.4)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Could not load violation data.")
except Exception as e:
    st.error(f"Error loading violation stats: {e}")


# 2️⃣ Geographic Distribution (Bar Chart)
try:
    st.markdown("### 🌍 Cases by Country")
    response = requests.get(f"{base_url}/geodata")
    if response.status_code == 200:
        data = response.json()
        df = pd.DataFrame(data)
        fig = px.bar(df, x="country", y="count", color="country", title="Cases by Country")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Could not load geographic data.")
except Exception as e:
    st.error(f"Error loading geodata: {e}")


# 3️⃣ Timeline (Line Chart)
try:
    st.markdown("### 📆 Cases Over Time")
    response = requests.get(f"{base_url}/timeline")
    if response.status_code == 200:
        data = response.json()
        df = pd.DataFrame(data)
        fig = px.line(df, x="date", y="count", markers=True, title="Cases by Month")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Could not load timeline data.")
except Exception as e:
    st.error(f"Error loading timeline: {e}")

# ------------------------------------------
# 📥 Export Data to Excel
# ------------------------------------------
st.markdown("### 📥 Export Case Data")

try:
    case_response = requests.get("http://127.0.0.1:8000/api/cases")
    if case_response.status_code == 200:
        cases_data = case_response.json()
        df_cases = pd.DataFrame(cases_data)

        if not df_cases.empty:
            export_df = df_cases[
                ["case_id", "title", "status", "priority", "violation_types", "location", "date_occurred"]
                if all(col in df_cases.columns for col in ["case_id", "title", "status", "priority", "violation_types", "location", "date_occurred"])
                else df_cases.columns
            ]

            output = BytesIO()
            with pd.ExcelWriter(output, engine="openpyxl") as writer:
                export_df.to_excel(writer, index=False, sheet_name="Cases")

            excel_data = output.getvalue()

            st.success(f"Loaded {len(export_df)} cases for export.")
            st.download_button(
                label="📥 Download as Excel",
                data=excel_data,
                file_name="cases_report.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.warning("No data available to export.")
    else:
        st.error("Failed to fetch case data.")
except Exception as e:
    st.error(f"Error loading data for export: {e}")
