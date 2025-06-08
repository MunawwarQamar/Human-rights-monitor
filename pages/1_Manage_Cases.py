import streamlit as st
import requests
import pandas as pd
from datetime import date

st.subheader("📋 All Registered Cases")

# Filters
with st.expander("🔍 Filter Cases"):
    col1, col2, col3 = st.columns(3)

    with col1:
        status_filter = st.selectbox("Status:", ["All", "new", "under_investigation", "resolved", "archived"])

    with col2:
        country_filter = st.text_input("Country:")

    with col3:
        violation_filter = st.text_input("Violation Type:")

    col4, col5 = st.columns(2)

    with col4:
        date_from = st.date_input("From Date:", value=date(2024, 1, 1))

    with col5:
        date_to = st.date_input("To Date:", value=date.today())

    search_query = st.text_input("🔎 General Search (by Title / Description / ID):")

# API
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
    params["query"] = search_query

# Fetch and display data
try:
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        cases = response.json()
        if cases:
            df = pd.DataFrame(cases)
            if "case_id" in df.columns:
                df = df[["case_id", "title", "status", "priority", "location", "date_occurred"]]
            st.dataframe(df, use_container_width=True)
        else:
            st.warning("No matching cases found.")
    else:
        st.error(f"Failed to fetch cases. Status code: {response.status_code}")
except Exception as e:
    st.error(f"An error occurred while connecting to the API: {e}")
