import streamlit as st
import requests

st.set_page_config(page_title="Change Case Status", layout="centered")
st.title("🔄 Change Case Status")

# Step 1: Get list of case IDs from backend
try:
    response = requests.get("http://127.0.0.1:8000/api/cases")
    response.raise_for_status()
    cases = response.json()
    case_ids = [case["case_id"] for case in cases]
except Exception as e:
    st.error(f"❌ Failed to fetch cases: {e}")
    case_ids = []

# Step 2: If cases are available, show form
if case_ids:
    selected_case_id = st.selectbox("🆔 Select Case ID", case_ids)

    new_status = st.selectbox(
        "📝 Select New Status",
        ["new", "under_investigation", "resolved", "archived"]
    )

    if st.button("✅ Update Status"):
        try:
            patch_url = f"http://127.0.0.1:8000/api/cases/{selected_case_id}/status"
            response = requests.patch(patch_url, json={"status": new_status})

            if response.status_code == 200:
                st.success(f"✅ Case {selected_case_id} updated to status: {new_status}")
            elif response.status_code == 404:
                st.error("❌ Case not found.")
            else:
                st.error(f"❌ Failed to update case. Status: {response.status_code}")
        except Exception as e:
            st.error(f"❌ Error connecting to API: {e}")
else:
    st.warning("⚠️ No available cases to update.")
