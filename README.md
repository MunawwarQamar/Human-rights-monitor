# Human Rights Case Management System 🧑‍⚖️

A backend system for managing and tracking human rights violation cases using FastAPI and MongoDB.  
This project provides RESTful APIs to store, update, and retrieve case data efficiently.

---

## 🧰 Tech Stack

- **FastAPI** – High-performance web framework for Python
- **MongoDB** – NoSQL database for flexible data storage
- **Pydantic** – Data validation and settings management
- **Uvicorn** – Lightning-fast ASGI server

---

## 📦 Requirements

- Python 3.11+
- Git
- Virtual Environment (recommended)
- Dependencies listed in `requirements.txt`

---

## 🚀 How to Run the Project

```bash
# 1. Clone the repository
git clone https://github.com/MunawwarQamar/Human-rights-monitor.git

# 2. Navigate to the project directory
cd Human-rights-monitor

# 3. Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate   # On Windows
# source venv/bin/activate   # On macOS/Linux

# 4. Install dependencies
pip install -r requirements.txt

# 5. Run the FastAPI application
uvicorn main:app --reload
