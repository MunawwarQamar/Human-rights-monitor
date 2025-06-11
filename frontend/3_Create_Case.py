import streamlit as st
import requests
from datetime import datetime

def show():
    st.title("➕ Create New Human Rights Case")
    st.info("Fields marked with * are required.")

    # ---------- Input Form ----------
    with st.form("create_case_form"):
        st.subheader("📋 Case Details")

        case_id = st.text_input("Case ID *", placeholder="e.g., HRM-2025-0001")
        title = st.text_input("Title *")
        description = st.text_area("Description *", height=150)

        violation_types = st.multiselect(
            "Violation Types *",
            ["arbitrary_detention", "forced_displacement", "torture", "execution", "property_destruction"],
        )

        priority = st.selectbox("Priority *", ["low", "medium", "high"])
        status = st.selectbox("Initial Status *", ["new", "under_investigation", "resolved"])

        st.markdown("### 🌍 Location")
        country = st.text_input("Country *")
        region = st.text_input("Region *")
        lat = st.number_input("Latitude", format="%.6f", value=0.0)
        lon = st.number_input("Longitude", format="%.6f", value=0.0)

        st.markdown("### 📅 Dates")
        date_occurred = st.date_input("Date Occurred *")
        date_reported = st.date_input("Date Reported *", datetime.today())

        submitted = st.form_submit_button("🚀 Submit Case")

    # ---------- Submission Logic ----------
    if submitted:
        required_fields = [case_id, title, description, violation_types, country, region]
        if not all(required_fields):
            st.warning("⚠️ Please fill in all required fields marked with *.")
        else:
            case_payload = {
                "case_id": case_id,
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
                response = requests.post("http://localhost:8000/api/cases", json=case_payload)
                if response.status_code in (200, 201):
                    st.success("✅ Case created successfully!")
                    st.info("📎 You can upload evidence files from the 'Upload Evidence' page.")
                else:
                    st.error(f"❌ Failed to create case: {response.json().get('detail')}")
            except Exception as e:
                st.error(f"🔌 Could not connect to backend. Error: {str(e)}")
