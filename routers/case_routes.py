from fastapi import APIRouter, HTTPException, Body, Query
from typing import Optional
from datetime import datetime
from models.case_model import Case
from database.connection import case_collection, case_history_collection


router = APIRouter()

@router.post("/cases")
async def create_case(case: Case):
    result = case_collection.insert_one(case.dict())
    if not result.inserted_id:
        raise HTTPException(status_code=500, detail="Failed to add case.")
    return {"message": "Case added successfully!", "case_id": str(result.inserted_id)}


@router.get("/cases")
async def get_all_cases(
    country: Optional[str] = Query(None),
    violation: Optional[str] = Query(None),
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None)
):
    try:
        query = {}

        if country:
            query["location.country"] = country

        if violation:
            query["violation_types"] = violation

        if date_from and date_to:
            query["date_occurred"] = {"$gte": date_from, "$lte": date_to}
        elif date_from:
            query["date_occurred"] = {"$gte": date_from}
        elif date_to:
            query["date_occurred"] = {"$lte": date_to}

        cases_cursor = case_collection.find(query)
        cases = []
        for case in cases_cursor:
            case["_id"] = str(case["_id"])
            cases.append(case)

        return cases
    except Exception as e:
        print("❌ Error in filtered GET /cases:", e)
        raise HTTPException(status_code=500, detail="Failed to retrieve cases")


@router.get("/cases/{case_id}")
async def get_case_by_id(case_id: str):
    try:
        case = case_collection.find_one({"case_id": case_id})
        if not case:
            raise HTTPException(status_code=404, detail="Case not found")
        case["_id"] = str(case["_id"])
        return case
    except Exception as e:
        print("❌ Error in GET /cases/{id}:", e)
        raise HTTPException(status_code=500, detail="Failed to retrieve case")


@router.patch("/cases/{case_id}")
async def update_case_status(case_id: str, status: str = Body(...)):
    try:
        case = case_collection.find_one({"case_id": case_id})
        if not case:
            raise HTTPException(status_code=404, detail="Case not found")

        old_status = case["status"]

        result = case_collection.update_one(
            {"case_id": case_id},
            {"$set": {"status": status}}
        )

        if result.modified_count == 0:
            raise HTTPException(status_code=500, detail="Status not updated")

        case_history_collection.insert_one({
            "case_id": case_id,
            "old_status": old_status,
            "new_status": status,
            "updated_at": datetime.utcnow(),
            "updated_by": "admin"
        })

        return {"message": "Case status updated successfully", "new_status": status}
    except Exception as e:
        print("❌ Error in PATCH /cases/{case_id}:", e)
        raise HTTPException(status_code=500, detail="Failed to update status")


@router.delete("/cases/{case_id}")
async def archive_case(case_id: str):
    try:
        result = case_collection.update_one(
            {"case_id": case_id},
            {"$set": {"status": "archived"}}
        )

        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Case not found")

        return {"message": f"Case {case_id} archived successfully"}
    except Exception as e:
        print("❌ Error in DELETE /cases/{case_id}:", e)
        raise HTTPException(status_code=500, detail="Failed to archive case")

@router.get("/cases/{case_id}/history")
async def get_case_status_history(case_id: str):
    try:
        history_cursor = case_history_collection.find({"case_id": case_id}).sort("updated_at", -1)
        history = []
        for record in history_cursor:
            record["_id"] = str(record["_id"])
            history.append(record)
        return history
    except Exception as e:
        print("Error in GET /cases/{case_id}/history:", e)
        raise HTTPException(status_code=500, detail="Failed to retrieve case history")
from fastapi import UploadFile, File
import os

UPLOAD_FOLDER = "uploads"

@router.post("/cases/{case_id}/upload")
async def upload_file_to_case(case_id: str, file: UploadFile = File(...)):
    try:
        case = case_collection.find_one({"case_id": case_id})
        if not case:
            raise HTTPException(status_code=404, detail="Case not found")

        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())

        evidence_entry = {
            "type": "file",
            "url": f"/{UPLOAD_FOLDER}/{file.filename}",
            "description": f"Uploaded: {file.filename}"
        }

        case_collection.update_one(
            {"case_id": case_id},
            {"$push": {"evidence": evidence_entry}}
        )

        return {"message": "File uploaded and linked to case", "file": evidence_entry}
    except Exception as e:
        print("❌ Error in file upload:", e)
        raise HTTPException(status_code=500, detail="Failed to upload file")
