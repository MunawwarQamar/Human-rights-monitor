import streamlit as st
import requests
import pandas as pd
from datetime import date

def show():
    # st.set_page_config(page_title="All Cases", layout="wide")
    st.title("📋 All Registered Cases")

    # Filters
    with st.expander("🔍 Filter Cases"):
        col1, col2, col3 = st.columns(3)
        with col1:
            status_filter = st.selectbox("Status:", ["All", "new", "under_investigation", "resolved", "archived"])
        with col2:
            country_filter = st.text_input("Country:")
        with col3:
            violation_filter = st.text_input("Violation Type:")

        use_date_filter = st.checkbox("📅 Enable Date Filter", value=False)

        col4, col5 = st.columns(2)
        with col4:
            date_from = st.date_input("From Date:") if use_date_filter else None
        with col5:
            date_to = st.date_input("To Date:", value=date.today()) if use_date_filter else None

        search_query = st.text_input("🔎 General Search (by Title / Description / ID):")

    # Prepare API request
    base_url = "http://127.0.0.1:8000/api/cases"
    params = {}
    if status_filter != "All":
        params["status"] = status_filter
    if country_filter:
        params["country"] = country_filter
    if violation_filter:
        params["violation"] = violation_filter
    if date_from:
        params["date_from"] = date_from.isoformat()
    if date_to:
        params["date_to"] = date_to.isoformat()
    if search_query:
        params["query_text"] = search_query

    # Fetch and display cases
    try:
        response = requests.get(base_url, params=params)
        if response.status_code == 200:
            cases = response.json()
            if cases:
                for case in cases:
                    loc = case.get("location", {})
                    case["country"] = loc.get("country", "")
                    case["region"] = loc.get("region", "")
                    case["violations"] = ", ".join(case.get("violation_types", []))
                df = pd.DataFrame(cases)
                df_display = df[["case_id", "title", "status", "priority", "country", "region", "violations", "date_occurred"]]
                st.dataframe(df_display, use_container_width=True)
            else:
                st.warning("No matching cases found.")
        else:
            st.error(f"❌ Failed to fetch cases. Status code: {response.status_code}")
    except Exception as e:
        st.error(f"🔌 Error connecting to the API: {e}")
