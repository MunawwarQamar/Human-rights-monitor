import streamlit as st
import requests
import importlib

API_URL = "http://127.0.0.1:8000/api/login"

# إعداد حالة الجلسة
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "role" not in st.session_state:
    st.session_state["role"] = None
if "username" not in st.session_state:
    st.session_state["username"] = ""
if "page" not in st.session_state:
    st.session_state["page"] = None

# تسجيل الخروج
def logout():
    for key in ["authenticated", "role", "username", "page"]:
        st.session_state[key] = None
    st.rerun()

# صفحة تسجيل الدخول
if not st.session_state["authenticated"]:
    st.set_page_config(page_title="Login | Human Rights MIS", layout="centered")
    st.title("🔐 Login to Human Rights MIS")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    login_button = st.button("Login")

    if login_button:
        response = requests.post(API_URL, json={
            "username": username,
            "password": password
        })

        if response.status_code == 200:
            data = response.json()
            st.session_state["authenticated"] = True
            st.session_state["username"] = data["username"]
            st.session_state["role"] = data["role"]
            st.success("Login successful! 🎉")
            st.rerun()
        else:
            st.error("Invalid credentials. Please try again.")

# ✅ بعد تسجيل الدخول
else:
    st.set_page_config(page_title="Human Rights MIS", layout="wide")
    st.sidebar.title(f"Welcome {st.session_state['username']}")
    st.sidebar.caption(f"Role: {st.session_state['role']}")
    st.sidebar.button("Logout", on_click=logout)

    role = st.session_state["role"]

    if role == "admin":
        pages = {
            "Manage Cases": "1_Manage_Cases.py",
            "Case Details": "2_Case_Details.py",
            "Create Case": "3_Create_Case.py",
            "Edit Case": "4_Edit_Case.py",
            "Update Status": "5_Update_Status.py",
            "Upload Evidence": "6_Upload_Evidence.py",
            "Archive Case": "7_Archive_Case.py",
            "Victim Details": "8_Victim_Details.py",
            "Report Incident": "9_Report_Incident.py",
            "Witness Records": "10_Witness_Records.py",
            "Dashboard": "11_Dashboard.py"
        }
    elif role == "manager":
        pages = {
            "Manage Cases": "1_Manage_Cases.py",
            "Case Details": "2_Case_Details.py",
            "Create Case": "3_Create_Case.py",
            "Edit Case": "4_Edit_Case.py",
            "Update Status": "5_Update_Status.py",
            "Upload Evidence": "6_Upload_Evidence.py",
            "Dashboard": "11_Dashboard.py"
        }
    elif role == "reporter":
        pages = {
            "Report Incident": "9_Report_Incident.py"
        }
    else:
        pages = {}

    selected_page = st.sidebar.selectbox("📂 Navigate", list(pages.keys()))
    if selected_page:
        module_name = pages[selected_page].replace(".py", "")
        module = importlib.import_module(f"frontend.{module_name}")
        module.show()
