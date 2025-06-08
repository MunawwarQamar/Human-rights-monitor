import streamlit as st
import requests
from datetime import datetime, date

st.set_page_config(page_title="Edit Case", layout="centered")
st.title("🛠️ Edit Existing Human Rights Case")

# Step 1: Fetch list of cases for dropdown
try:
    list_response = requests.get("http://localhost:8000/api/cases")
    list_response.raise_for_status()
    all_cases = list_response.json()
    case_options = [f"{c['case_id']} — {c['title']}" for c in all_cases]
except Exception as e:
    st.error(f"❌ Failed to fetch case list: {e}")
    st.stop()

selected_label = st.selectbox("Select a case to edit", case_options)
selected_case_id = selected_label.split(" — ")[0]

# Step 2: Fetch selected case details
try:
    case_response = requests.get(f"http://localhost:8000/api/cases/{selected_case_id}")
    case_response.raise_for_status()
    case = case_response.json()
except Exception as e:
    st.error(f"❌ Failed to fetch case data: {e}")
    st.stop()

# ---------- Form for Editing ----------
with st.form("edit_case_form"):
    st.subheader("📋 Edit Case Details")

    title = st.text_input("Title", case.get("title"))
    description = st.text_area("Description", case.get("description"), height=150)

    violation_types = st.multiselect(
        "Violation Types",
        ["arbitrary_detention", "forced_displacement", "torture", "execution", "property_destruction"],
        default=case.get("violation_types", [])
    )

    priority = st.selectbox("Priority", ["low", "medium", "high"], index=["low", "medium", "high"].index(case.get("priority", "medium")))
    status = st.selectbox("Status", ["new", "under_investigation", "resolved", "archived"], index=["new", "under_investigation", "resolved", "archived"].index(case.get("status", "new")))

    st.markdown("### 🌍 Location")
    location = case.get("location", {})
    country = st.text_input("Country", location.get("country", ""))
    region = st.text_input("Region", location.get("region", ""))
    coords = location.get("coordinates", {}).get("coordinates", [0.0, 0.0])
    lon = st.number_input("Longitude", value=coords[0], format="%.6f")
    lat = st.number_input("Latitude", value=coords[1], format="%.6f")

    st.markdown("### 📅 Dates")
    occurred_str = case.get("date_occurred", date.today().isoformat())[:10]
    reported_str = case.get("date_reported", date.today().isoformat())[:10]
    date_occurred = st.date_input("Date Occurred", date.fromisoformat(occurred_str))
    date_reported = st.date_input("Date Reported", date.fromisoformat(reported_str))

    submitted = st.form_submit_button("💾 Update Case")

# ---------- Submit PATCH ----------
if submitted:
    updated_payload = {
        "title": title,
        "description": description,
        "violation_types": violation_types,
        "status": status,
        "priority": priority,
        "location": {
            "country": country,
            "region": region,
            "coordinates": {
                "type": "Point",
                "coordinates": [lon, lat]
            }
        },
        "date_occurred": date_occurred.isoformat(),
        "date_reported": date_reported.isoformat()
    }

    try:
        patch_response = requests.patch(
            f"http://localhost:8000/api/cases/{selected_case_id}",
            json=updated_payload
        )
        if patch_response.status_code == 200:
            st.success("✅ Case updated successfully!")
        else:
            st.error(f"❌ Failed to update case: {patch_response.json().get('detail')}")
    except Exception as e:
        st.error(f"🔌 Error updating case: {e}")
