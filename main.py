from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os

from routers.case_routes import router as case_router
from routers.analytics_routes import router as analytics_router
from routers.incident_routes import router as incident_router  
if not os.path.exists("uploads"):
    os.makedirs("uploads")

app = FastAPI(
    title="Human Rights Monitor API",
    description="API for reporting and tracking human rights incidents."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(case_router, prefix="/api", tags=["Cases"])
app.include_router(analytics_router, prefix="/api", tags=["Analytics"])
app.include_router(incident_router, prefix="/api", tags=["Incident"])

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

@app.get("/")
async def root():
    return {"message": "Welcome to the Human Rights Monitor API!"}
