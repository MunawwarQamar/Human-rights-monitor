import streamlit as st

st.set_page_config(page_title="Human Rights CMS", layout="wide")

# -------------------------------
# Logo (Optional)
# -------------------------------
# Uncomment below if you add a logo image
# st.image("logo.png", width=120)

# -------------------------------
# Title & Intro
# -------------------------------
st.title("🕊️ Human Rights Case Management System")
st.markdown("""
Welcome to the **Human Rights CMS**, a comprehensive platform developed as part of a university project.

This system enables organizations and field investigators to **document**, **track**, and **analyze** reported human rights violations effectively.
""")

# -------------------------------
# System Purpose
# -------------------------------
st.markdown("### 🧭 System Purpose")
st.write("""
This platform supports the collection and organization of:
- 📂 Human rights violation cases
- 🧍 Victim and witness information
- 📎 Evidence files (PDFs, images, videos)
- 📄 Incident reports
- 📊 Visual analytics for better decision-making
""")

# -------------------------------
# Team Members
# -------------------------------
st.markdown("### 👥 Team Members")
st.write("""
- 👩‍💻 **Munawwar Qamar** — Case Management, Dashboard, Upload, Frontend
- 👩 **Aya** — Victim & Witness Modules
- 👩 **Shahd** — Incident Reporting & Data Validation
""")

# -------------------------------
# System Modules
# -------------------------------
st.markdown("### 🧩 System Modules")
st.markdown("""
- **📋 Case Management:** View, filter, update and archive human rights cases.
- **📁 Evidence Upload:** Upload and attach documents (PDFs, images, videos) to specific cases.
- **🧍 Victim & Witness:** Manage victim and witness profiles and testimonies.
- **📝 Incident Reporting:** Submit new cases and gather contextual details.
- **📊 Dashboard:** Visualize statistics and trends using interactive graphs.
""")

# -------------------------------
# Navigation Instructions
# -------------------------------
st.markdown("### 🔗 How to Navigate")
st.write("""
Use the menu on the **left sidebar** to switch between system modules.
Each module is designed to be standalone and easy to use.
""")

st.success("🎯 You can now begin exploring the system from the sidebar.")
