from fastapi import FastAPI
from routers.case_routes import router as case_router
from fastapi.staticfiles import StaticFiles
import os
from routers.analytics_routes import router as analytics_router 

if not os.path.exists("uploads"):
    os.makedirs("uploads")

app = FastAPI()

app.include_router(case_router, prefix="/api", tags=["Cases"])
app.include_router(analytics_router, prefix="/api", tags=["Analytics"]) 

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
