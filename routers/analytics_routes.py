from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from datetime import datetime
from database.connection import case_collection

router = APIRouter()

# -------------------------------
# Helper: build match filter
# -------------------------------
def build_match_filter(
    country: Optional[str],
    violation: Optional[str],
    date_from: Optional[datetime],
    date_to: Optional[datetime]
):
    match = {}

    if country:
        match["location.country"] = {"$regex": country, "$options": "i"}

    if violation:
        match["violation_types"] = {"$regex": violation, "$options": "i"}

    if date_from or date_to:
        match["date_occurred"] = {}
        if date_from:
            match["date_occurred"]["$gte"] = date_from
        if date_to:
            match["date_occurred"]["$lte"] = date_to

    return match

# -------------------------------
# 1. Violations Pie Chart
# -------------------------------
@router.get("/analytics/violations")
async def get_violation_statistics(
    country: Optional[str] = Query(None),
    violation: Optional[str] = Query(None),
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None)
):
    try:
        match = build_match_filter(country, violation, date_from, date_to)
        pipeline = []
        if match:
            pipeline.append({"$match": match})

        pipeline += [
            {"$unwind": "$violation_types"},
            {"$group": {
                "_id": "$violation_types",
                "count": {"$sum": 1}
            }},
            {"$sort": {"count": -1}}
        ]

        result = list(case_collection.aggregate(pipeline))
        return {entry["_id"]: entry["count"] for entry in result}
    except Exception as e:
        print("❌ Error in /analytics/violations:", e)
        raise HTTPException(status_code=500, detail="Failed to fetch violation statistics")

# -------------------------------
# 2. Country Statistics Bar Chart
# -------------------------------
@router.get("/analytics/geodata")
async def get_country_statistics(
    country: Optional[str] = Query(None),
    violation: Optional[str] = Query(None),
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None)
):
    try:
        match = build_match_filter(country, violation, date_from, date_to)
        pipeline = []
        if match:
            pipeline.append({"$match": match})

        pipeline += [
            {"$group": {
                "_id": "$location.country",
                "count": {"$sum": 1}
            }},
            {"$sort": {"count": -1}}
        ]

        result = list(case_collection.aggregate(pipeline))
        return [{"country": entry["_id"], "count": entry["count"]} for entry in result]
    except Exception as e:
        print("❌ Error in /analytics/geodata:", e)
        raise HTTPException(status_code=500, detail="Failed to fetch country statistics")

# -------------------------------
# 3. Timeline Chart (Cases by Month)
# -------------------------------
@router.get("/analytics/timeline")
async def get_cases_over_time(
    country: Optional[str] = Query(None),
    violation: Optional[str] = Query(None),
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None)
):
    try:
        match = build_match_filter(country, violation, date_from, date_to)
        pipeline = []
        if match:
            pipeline.append({"$match": match})

        # 🛡️ Filter only records with valid date_occurred
        pipeline.append({"$match": {"date_occurred": {"$type": "date"}}})

        pipeline += [
            {
                "$group": {
                    "_id": {
                        "year": {"$year": "$date_occurred"},
                        "month": {"$month": "$date_occurred"}
                    },
                    "count": {"$sum": 1}
                }
            },
            {"$sort": {"_id.year": 1, "_id.month": 1}}
        ]

        result = list(case_collection.aggregate(pipeline))
        return [
            {
                "date": f"{entry['_id']['year']}-{entry['_id']['month']:02d}",
                "count": entry["count"]
            }
            for entry in result
        ]
    except Exception as e:
        print("❌ Error in /analytics/timeline:", e)
        raise HTTPException(status_code=500, detail="Failed to generate timeline")
