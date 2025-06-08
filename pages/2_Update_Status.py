import streamlit as st
import requests

st.subheader("📝 Update Case Status")

# Get all case IDs from API
try:
    response = requests.get("http://127.0.0.1:8000/api/cases")
    if response.status_code == 200:
        cases = response.json()
        case_ids = list({case["case_id"] for case in cases})
    else:
        st.error("Failed to fetch cases.")
        case_ids = []
except Exception as e:
    st.error(f"Error fetching cases: {e}")
    case_ids = []

if case_ids:
    selected_case_id = st.selectbox("Select Case ID:", case_ids)

    new_status = st.selectbox(
        "Select New Status:",
        ["new", "under_investigation", "resolved", "archived"]
    )

    if st.button("Update Status"):
        patch_url = f"http://127.0.0.1:8000/api/cases/{selected_case_id}"
        response = requests.patch(patch_url, json={"status": new_status})

        if response.status_code == 200:
            st.success(f"✅ Case {selected_case_id} updated to status: {new_status}")
        elif response.status_code == 404:
            st.error("❌ Case not found.")
        else:
            st.error(f"❌ Failed to update case. Status: {response.status_code}")
else:
    st.warning("⚠️ No available cases to update.")
