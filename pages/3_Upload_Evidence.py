import streamlit as st
import requests

st.subheader("📁 Upload Evidence File to Case")

# Get all case IDs
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

# Upload form
if case_ids:
    selected_case_id = st.selectbox("Select Case ID:", case_ids)
    uploaded_file = st.file_uploader("Choose a file (PDF, Image, Video)...")

    if uploaded_file and st.button("Upload File"):
        files = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
        try:
            upload_url = f"http://127.0.0.1:8000/api/cases/{selected_case_id}/upload"
            res = requests.post(upload_url, files=files)

            if res.status_code == 200:
                st.success(f"✅ File uploaded to case {selected_case_id}")
            elif res.status_code == 404:
                st.error("❌ Case not found.")
            else:
                st.error(f"❌ Upload failed. Status: {res.status_code}")
        except Exception as e:
            st.error(f"Error uploading file: {e}")
else:
    st.warning("⚠️ No cases available to attach files.")
