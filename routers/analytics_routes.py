from fastapi import APIRouter, HTTPException
from database.connection import case_collection

router = APIRouter()

@router.get("/analytics/violations")
async def get_violation_statistics():
    try:
        pipeline = [
            {"$unwind": "$violation_types"},
            {"$group": {
                "_id": "$violation_types",
                "count": {"$sum": 1}
            }},
            {"$sort": {"count": -1}}
        ]

        result = list(case_collection.aggregate(pipeline))

        # Convert to simpler format
        stats = {entry["_id"]: entry["count"] for entry in result}
        return stats

    except Exception as e:
        print("❌ Error in /analytics/violations:", e)
        raise HTTPException(status_code=500, detail="Failed to fetch violation statistics")

@router.get("/analytics/geodata")
async def get_country_statistics():
    try:
        pipeline = [
            {"$group": {
                "_id": "$location.country",
                "count": {"$sum": 1}
            }},
            {"$sort": {"count": -1}}
        ]

        result = list(case_collection.aggregate(pipeline))

        # Convert to list of dicts
        stats = [{"country": entry["_id"], "count": entry["count"]} for entry in result]
        return stats

    except Exception as e:
        print("❌ Error in /analytics/geodata:", e)
        raise HTTPException(status_code=500, detail="Failed to fetch country statistics")
@router.get("/analytics/timeline")
async def get_cases_over_time():
    try:
        pipeline = [
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

        timeline = [
            {
                "date": f"{entry['_id']['year']}-{entry['_id']['month']:02d}",
                "count": entry["count"]
            }
            for entry in result
        ]

        return timeline

    except Exception as e:
        print("❌ Error in /analytics/timeline:", e)
        raise HTTPException(status_code=500, detail="Failed to generate timeline")
