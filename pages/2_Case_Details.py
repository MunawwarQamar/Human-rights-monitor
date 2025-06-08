import streamlit as st
import requests

st.set_page_config(page_title="Case Details", layout="wide")
st.title("📄 View Case Details")

# Step 1: Fetch all cases for dropdown
try:
    case_list_response = requests.get("http://localhost:8000/api/cases")
    if case_list_response.status_code != 200:
        st.error("❌ Failed to load case list.")
        st.stop()
    all_cases = case_list_response.json()
    case_options = [f"{case['case_id']} — {case['title']}" for case in all_cases]
except Exception as e:
    st.error(f"🔌 Error loading case list: {e}")
    st.stop()

# Step 2: Select case from dropdown
selected_label = st.selectbox("🆔 Select a Case", case_options)
selected_case_id = selected_label.split(" — ")[0]

# Step 3: Fetch selected case details
try:
    case_response = requests.get(f"http://localhost:8000/api/cases/{selected_case_id}")
    if case_response.status_code != 200:
        st.error("❌ Failed to load case details.")
        st.stop()
    case = case_response.json()
except Exception as e:
    st.error(f"🔌 Failed to connect to server: {e}")
    st.stop()

# Display case details
st.subheader(f"📄 Case: {case.get('case_id')}")
st.markdown(f"**Title:** {case.get('title')}")
st.markdown(f"**Description:** {case.get('description')}")
st.markdown(f"**Status:** {case.get('status')}")
st.markdown(f"**Priority:** {case.get('priority')}")
st.markdown(f"**Violation Types:** {', '.join(case.get('violation_types', []))}")
st.markdown(f"**Date Occurred:** {case.get('date_occurred')[:10]}")
st.markdown(f"**Date Reported:** {case.get('date_reported')[:10]}")

location = case.get("location", {})
st.markdown(f"**Location:** {location.get('country')}, {location.get('region')}")

# Step 4: Show evidence with working links
st.markdown("---")
st.subheader("📎 Evidence Files")
evidence_list = case.get("evidence", [])
base_url = "http://localhost:8000"  # Replace with your server domain if deployed

if not evidence_list:
    st.info("No evidence files attached.")
else:
    for ev in evidence_list:
        full_url = base_url + ev["url"]
        st.markdown(f"- `{ev['type']}`: [{ev['description']}]({full_url})")

# Step 5: Status history
st.markdown("---")
st.subheader("🕓 Status Change History")
try:
    history_response = requests.get(f"http://localhost:8000/api/cases/{selected_case_id}/history")
    if history_response.status_code == 200:
        history_data = history_response.json()
        if history_data:
            for record in history_data:
                st.markdown(
                    f"🗓️ `{record['updated_at'][:19]}` — **{record['old_status']} ➡️ {record['new_status']}** by {record['updated_by']}"
                )
        else:
            st.info("No status changes recorded.")
    else:
        st.info("No history found.")
except Exception as e:
    st.error(f"Error fetching history: {e}")
