# 🕊️ Human Rights Case Management System

A secure and data-driven platform for documenting and managing human rights violations. Built with FastAPI, MongoDB, and Streamlit.

---

## 1️⃣ Overview

The Human Rights MIS system enables NGOs and legal teams to:

- Record human rights cases (e.g., arbitrary detention, forced displacement)
- Manage victims and witness data securely
- Submit incident reports with geolocation and media
- Analyze data through charts and exportable reports

---

## 2️⃣ Key Features

- ✅ CRUD for human rights cases
- 🔍 Filter cases by country, status, violation, and date
- 🧾 Case status history tracking
- 📎 Evidence uploading (PDF, images, videos)
- 📊 Analytics dashboard with pie, bar, and line charts
- 📁 Export cases to Excel
- 🌐 Organized UI navigation (About, Dashboard, etc.)

---

## 3️⃣ Technologies Used

- 🐍 Python 3.12
- 🚀 FastAPI + Uvicorn (Backend API)
- 🍃 MongoDB (NoSQL Database)
- 🧾 Pydantic (Validation)
- 📊 Streamlit (Frontend Dashboard)
- 📦 Plotly, Requests, pandas, openpyxl

---

## 4️⃣ Folder Structure

```
.
├── main.py                  # Entry point (FastAPI app)
├── models/                 # Pydantic models
├── routers/                # API route definitions
├── database/               # MongoDB connection & collections
├── dashboard/              # Streamlit frontend pages
├── uploads/                # Evidence storage
├── populate_cases.py       # Script to populate test data
├── requirements.txt
└── README.md
```

---

## 5️⃣ How to Run the Project

### ▶️ Backend (FastAPI)
```bash
uvicorn main:app --reload
```

### ▶️ Frontend (Streamlit)
```bash
cd dashboard/
streamlit run main.py
```

### ▶️ Load Test Data (Optional)
```bash
python populate_cases.py
```

---

## 6️⃣ API Documentation

- `POST /cases/` – Create new case
- `GET /cases/` – List all cases (with filters)
- `GET /cases/{case_id}` – Retrieve a specific case
- `PATCH /cases/{case_id}` – Update case status
- `DELETE /cases/{case_id}` – Archive a case
- `GET /cases/{case_id}/history` – View status history
- `POST /cases/{case_id}/upload` – Upload file to a case
- `GET /analytics/violations` – Violations summary
- `GET /analytics/geodata` – Distribution by country
- `GET /analytics/timeline` – Trend over time

---

## 7️⃣ Screenshots / Demo

> 📸 _Add here images of your dashboard UI, charts, and evidence upload._

---

## 8️⃣ Contributors

| Name              | Role                                  |
|-------------------|----------------------------------------|
| **Munawwar Qamar** | Case Management + Dashboard + Analytics |
| **Aya**            | Victim & Witness Module                |
| **Shahd**          | Incident Reporting Module              |

---

## 9️⃣ Acknowledgements

- `Streamlit Option Menu` for horizontal navbars
- MongoDB Aggregation for real-time analytics
- FastAPI Documentation: https://fastapi.tiangolo.com/
- Plotly Express & OpenPyXL for data visualization/export