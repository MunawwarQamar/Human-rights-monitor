import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from io import BytesIO

def show():
    st.title("📊 Human Rights Analytics Dashboard")

    # ----- Filters -----
    with st.expander("🔍 Filter Options"):
        col1, col2, col3 = st.columns(3)
        with col1:
            selected_country = st.text_input("Filter by Country:")
        with col2:
            selected_violation = st.text_input("Filter by Violation Type:")
        with col3:
            date_range = st.date_input("Date Range (from - to)", [])

    params = {}
    if selected_country:
        params["country"] = selected_country
    if selected_violation:
        params["violation"] = selected_violation
    if len(date_range) == 2:
        params["date_from"] = date_range[0].isoformat()
        params["date_to"] = date_range[1].isoformat()

    # ----- Pie Chart: Violation Types -----
    st.markdown("### 🧯 Violation Types Distribution")
    try:
        response = requests.get("http://127.0.0.1:8000/api/analytics/violations", params=params)
        response.raise_for_status()
        data = response.json()
        df = pd.DataFrame({"Violation": list(data.keys()), "Count": list(data.values())})
        fig = px.pie(df, names="Violation", values="Count", hole=0.4)
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"Error loading violation stats: {e}")

    # ----- Bar Chart: Cases by Country -----
    st.markdown("### 🌍 Cases by Country")
    try:
        response = requests.get("http://127.0.0.1:8000/api/analytics/geodata", params=params)
        response.raise_for_status()
        data = response.json()
        df = pd.DataFrame(data)
        fig = px.bar(df, x="country", y="count", color="country", title="Cases by Country")
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"Error loading geographic data: {e}")

    # ----- Line Chart: Cases Over Time -----
    st.markdown("### 📆 Cases Over Time")
    try:
        response = requests.get("http://127.0.0.1:8000/api/analytics/timeline", params=params)
        response.raise_for_status()
        data = response.json()
        df = pd.DataFrame(data)
        fig = px.line(df, x="date", y="count", markers=True, title="Cases by Month")
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"Error loading timeline: {e}")

    # ----- Map -----
    st.markdown("### 🗺️ Geographic Map of Cases")
    try:
        response = requests.get("http://127.0.0.1:8000/api/cases", params=params)
        response.raise_for_status()
        data = response.json()
        locations = []

        if isinstance(data, list):
            for case in data:
                if not isinstance(case, dict):
                    continue
                location = case.get("location", {})
                coordinates = location.get("coordinates", [])
                coords = []

                # ✅ التعامل مع coordinate كـ dict أو list
                if isinstance(coordinates, dict):
                    coords = coordinates.get("coordinates", [])
                elif isinstance(coordinates, list):
                    coords = coordinates

                if isinstance(coords, list) and len(coords) == 2:
                    locations.append({
                        "case_id": case.get("case_id", ""),
                        "title": case.get("title", ""),
                        "lon": coords[0],
                        "lat": coords[1],
                        "status": case.get("status", "unknown")
                    })

        df_map = pd.DataFrame(locations)
        if not df_map.empty:
            fig = px.scatter_mapbox(df_map, lat="lat", lon="lon", hover_name="title",
                                    hover_data=["case_id", "status"],
                                    color="status", zoom=2, height=500)
            fig.update_layout(mapbox_style="open-street-map")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No valid coordinates found.")
    except Exception as e:
        st.error(f"Error loading map data: {e}")

    # ----- Export to Excel -----
    st.markdown("### 📥 Export Case Data to Excel")
    try:
        response = requests.get("http://127.0.0.1:8000/api/cases", params=params)
        response.raise_for_status()
        data = response.json()
        df = pd.DataFrame(data)
        if not df.empty:
            export_df = df[["case_id", "title", "status", "priority", "violation_types", "location", "date_occurred"]] \
                if all(col in df.columns for col in ["case_id", "title", "status", "priority", "violation_types", "location", "date_occurred"]) \
                else df
            output = BytesIO()
            with pd.ExcelWriter(output, engine="openpyxl") as writer:
                export_df.to_excel(writer, index=False, sheet_name="Cases")
            st.download_button(
                label="📥 Download Cases as Excel",
                data=output.getvalue(),
                file_name="cases_report.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.warning("No data available to export.")
    except Exception as e:
        st.error(f"Error exporting data: {e}")

