import streamlit as st
import requests

def show():
    st.title("📁 Upload Evidence File to a Case")

    # Step 1: Load all case IDs from API
    try:
        response = requests.get("http://127.0.0.1:8000/api/cases")
        response.raise_for_status()
        cases = response.json()
        case_ids = sorted({case["case_id"] for case in cases})
    except Exception as e:
        st.error(f"❌ Failed to fetch cases: {e}")
        case_ids = []

    # Step 2: Show upload form
    if case_ids:
        selected_case_id = st.selectbox("🆔 Select Case ID", case_ids)
        file_type = st.selectbox("📂 Select File Type", ["photo", "video", "document"])
        description = st.text_input("📝 File Description (optional)", placeholder="e.g., Satellite image of destroyed area")
        uploaded_file = st.file_uploader("📎 Choose a file", type=["jpg", "jpeg", "png", "pdf", "mp4", "avi", "mov"])

        if uploaded_file and st.button("🚀 Upload Evidence"):
            files = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
            try:
                upload_url = f"http://127.0.0.1:8000/api/cases/{selected_case_id}/upload"
                res = requests.post(upload_url, files=files)

                if res.status_code == 200:
                    file_response = res.json()
                    file_info = file_response.get("file", {})

                    # Update the file entry with type and description
                    patch_url = f"http://127.0.0.1:8000/api/cases/{selected_case_id}"
                    patch_data = {
                        "evidence": [{
                            "type": file_type,
                            "url": file_info.get("url", ""),
                            "description": description or file_info.get("description", "")
                        }]
                    }
                    requests.patch(patch_url, json=patch_data)

                    st.success(f"✅ File uploaded successfully to case {selected_case_id}")
                    st.markdown(f"🔗 [View File]({file_info.get('url', '#')})")
                elif res.status_code == 404:
                    st.error("❌ Case not found.")
                else:
                    st.error(f"❌ Upload failed. Status: {res.status_code}")
            except Exception as e:
                st.error(f"❌ Error uploading file: {e}")
    else:
        st.warning("⚠️ No cases available to upload evidence to.")
