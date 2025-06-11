from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from database.connection import db
import bcrypt

router = APIRouter()
users_collection = db["users"]

class LoginRequest(BaseModel):
    username: str
    password: str

@router.post("/login")
def login(data: LoginRequest):
    user = users_collection.find_one({"username": data.username})

    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    if not bcrypt.checkpw(data.password.encode('utf-8'), user["password"].encode('utf-8')):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    return {
        "message": "Login successful",
        "username": user["username"],
        "role": user["role"]
    }
