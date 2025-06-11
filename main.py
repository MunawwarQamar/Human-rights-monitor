from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import os

from routers.case_routes import router as case_router
from routers.analytics_routes import router as analytics_router
from routers import user_routes

if not os.path.exists("uploads"):
    os.makedirs("uploads")

app = FastAPI()

app.include_router(case_router, prefix="/api", tags=["Cases"])
app.include_router(analytics_router, prefix="/api", tags=["Analytics"])
app.include_router(user_routes.router, prefix="/api", tags=["Users"])

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
