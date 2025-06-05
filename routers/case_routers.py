from fastapi import APIRouter, HTTPException
from models.case_model import Case
from database.connection import case_collection

router = APIRouter()

@router.post("/cases")
async def create_case(case: Case):
    # حوّل بيانات القضيّة إلى dict وخزنها في قاعدة البيانات
    result = case_collection.insert_one(case.dict())
    
    if not result.inserted_id:
        raise HTTPException(status_code=500, detail="Failed to add case.")
    
    return {"message": "Case added successfully!", "case_id": str(result.inserted_id)}
