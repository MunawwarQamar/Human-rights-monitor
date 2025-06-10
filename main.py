# main.py
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import os
from fastapi.middleware.cors import CORSMiddleware # تأكد من استيراد CORS middleware إذا كنت تستخدمه

# استيراد الراوترات الخاصة بك
from routers.case_routes import router as case_router
from routers.analytics_routes import router as analytics_router
# استيراد الراوتر من incident_routes.py وتسميته بشكل واضح
from routers.incident_routes import router as incident_router # <--- هذا هو التغيير الجديد

# تأكد من وجود مجلد التحميل
if not os.path.exists("uploads"):
    os.makedirs("uploads")

app = FastAPI(title="Human Rights Monitor API",
              description="API for reporting and tracking human rights incidents.")

# إعداد CORS (إذا كان مطلوبًا لتطبيقك)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501"], # تأكد أن هذا يطابق عنوان URL لـ Streamlit
    allow_methods=["*"], # السماح بجميع طرق الـ HTTP (GET, POST, PUT, DELETE, PATCH)
    allow_headers=["*"], # السماح بجميع رؤوس الـ HTTP
)


# تضمين الراوترات في تطبيق FastAPI الرئيسي
app.include_router(case_router, prefix="/api", tags=["Cases"])
app.include_router(analytics_router, prefix="/api", tags=["Analytics"])
app.include_router(incident_router, prefix="/api", tags=["Incident"]) # الآن incident_router معرف بشكل صحيح

# خدمة الملفات الثابتة (للوصول إلى الملفات المرفوعة)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

@app.get("/")
async def root():
    return {"message": "Welcome to the Human Rights Monitor API!"}
