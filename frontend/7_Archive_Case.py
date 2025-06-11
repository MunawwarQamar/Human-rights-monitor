import streamlit as st
import requests

def show():
    st.title("🗑️ Archive Human Rights Case")

    # Step 1: Fetch all case IDs
    try:
        response = requests.get("http://127.0.0.1:8000/api/cases")
        response.raise_for_status()
        cases = response.json()
        case_ids = [case["case_id"] for case in cases]
    except Exception as e:
        st.error(f"❌ Failed to load cases: {e}")
        case_ids = []

    # Step 2: User selects a case
    if case_ids:
        selected_case_id = st.selectbox("Select a Case to Archive", case_ids)

        st.warning("⚠️ Archiving a case will mark it as 'archived'. It will remain in the system but shown as inactive.")

        confirm = st.checkbox("✅ I confirm I want to archive this case.")

        if st.button("🗃️ Archive Case"):
            if confirm:
                try:
                    patch_url = f"http://127.0.0.1:8000/api/cases/{selected_case_id}/status"
                    response = requests.patch(patch_url, json={"status": "archived"})

                    if response.status_code == 200:
                        st.success(f"✅ Case {selected_case_id} archived successfully.")
                    elif response.status_code == 404:
                        st.error("❌ Case not found.")
                    else:
                        st.error(f"❌ Failed to archive case. Status: {response.status_code}")
                except Exception as e:
                    st.error(f"❌ Error connecting to server: {e}")
            else:
                st.info("Please confirm the action by checking the box.")
    else:
        st.info("ℹ️ No cases available to archive.")
