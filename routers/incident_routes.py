# routers/incident_routes.py
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Query, status
from typing import List, Optional, Any
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import datetime
from pydantic import BaseModel, Field, EmailStr, BeforeValidator, field_validator, model_validator, ValidationError
from typing_extensions import Annotated
import shutil
import os
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
from dotenv import load_dotenv
import re

# router = APIRouter()  # <--- هذا هو التعريف الصحيح للراوتر
router = APIRouter(tags=["Incident Reports"]) # يمكنك إضافة tags هنا

# تحميل المتغيرات البيئية من ملف .env
load_dotenv()

# **قم بإزالة هذه الأسطر من هنا!**
# app = FastAPI()
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["http://localhost:8501"],
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# تفاصيل الاتصال بقاعدة بيانات MongoDB
MONGO_DETAILS = os.getenv("MONGODB_URI")
if not MONGO_DETAILS:
    raise RuntimeError("MONGODB_URI غير موجود في ملف .env. يرجى التأكد من تعيينه.")

client = AsyncIOMotorClient(MONGO_DETAILS)
db = client.human_rights_monitor
collection = db.incident_reports

# تحديد مجلد لرفع الملفات والتأكد من وجوده (يمكن نقل هذا لـ main.py أيضًا إذا أردت مركزية أكبر)
UPLOAD_FOLDER = "./uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# تهيئة Geocoder
geolocator = Nominatim(user_agent="hr_monitor_app")

# --- Pydantic Models للتحقق من البيانات ---
# (كل نماذج Pydantic الخاصة بك كما هي)
class Coordinates(BaseModel):
    type: str = "Point"
    coordinates: List[float]

    @model_validator(mode='before')
    @classmethod
    def parse_coordinates_input(cls, value: Any) -> Any:
        if isinstance(value, dict):
            if "coordinates" in value and isinstance(value["coordinates"], list):
                return value
            if '0' in value and '1' in value:
                try:
                    return {"type": "Point", "coordinates": [float(value['0']), float(value['1'])]}
                except ValueError:
                    pass
        elif isinstance(value, (list, tuple)) and len(value) == 2:
            return {"type": "Point", "coordinates": [float(value[0]), float(value[1])]}
        return value

class Location(BaseModel):
    country: str
    city: Optional[str] = None
    coordinates: Coordinates

class ContactInfo(BaseModel):
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    preferred_contact: Optional[str] = None

class IncidentDetails(BaseModel):
    date: datetime.datetime
    location: Location
    description: str
    violation_types: List[str]

    @field_validator('date', mode='before')
    @classmethod
    def convert_to_datetime_utc(cls, v: Any) -> datetime.datetime:
        if isinstance(v, datetime.datetime):
            return v
        if isinstance(v, datetime.date):
            return datetime.datetime(v.year, v.month, v.day, 0, 0, 0, 0, tzinfo=datetime.timezone.utc)
        if isinstance(v, str):
            try:
                return datetime.datetime.fromisoformat(v.replace("Z", "+00:00"))
            except ValueError:
                try:
                    dt_date = datetime.date.fromisoformat(v)
                    return datetime.datetime(dt_date.year, dt_date.month, dt_date.day, 0, 0, 0, 0, tzinfo=datetime.timezone.utc)
                except ValueError:
                    pass
        raise ValueError(f"Invalid date format for datetime conversion: {v}. Expected Walpole-MM-DD or Walpole-MM-DDTHH:MM:SS.")

class ReportEvidence(BaseModel):
    type: str
    url: str
    description: Optional[str] = None

class IncidentReport(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    report_id: str
    reporter_type: str
    anonymous: bool = False
    contact_info: Optional[ContactInfo] = None
    incident_details: IncidentDetails
    evidence: List[ReportEvidence] = []
    status: str = "new"
    assigned_to: Optional[str] = None
    created_at: datetime.datetime = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc))

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str,
            datetime.datetime: lambda v: v.isoformat(),
        }
        json_schema_extra = {
            "example": {
                "report_id": "IR-2025-1001",
                "reporter_type": "individual",
                "anonymous": False,
                "contact_info": {
                    "email": "reporter@example.com",
                    "phone": "123-456-7890",
                    "preferred_contact": "email"
                },
                "incident_details": {
                    "date": "2025-06-01T00:00:00Z",
                    "location": {
                        "country": "Palestine",
                        "city": "Ramallah",
                        "coordinates": {
                            "type": "Point",
                            "coordinates": [35.2163, 31.9037]
                        }
                    },
                    "description": "Witnessed arbitrary detention.",
                    "violation_types": ["arbitrary detention", "freedom of movement"]
                },
                "evidence": [
                    {
                        "type": "photo",
                        "url": "/uploads/IR-2025-1001_image1.jpg",
                        "description": "Photo of the incident location"
                    }
                ],
                "status": "new",
                "created_at": "2025-02-08T12:00:00.000Z"
            }
        }

class ReportStatusUpdate(BaseModel):
    status: str = Field(..., pattern="^(new|in_progress|closed|resolved|on_hold)$", description="Status of the report")

# --- وظائف مساعدة (كما هي) ---
async def generate_report_id():
    current_year = datetime.datetime.now(datetime.timezone.utc).year
    latest_report = await collection.find_one(
        {"report_id": {"$regex": r"^IR-\d{4}-\d+$"}},
        sort=[("report_id", -1)]
    )

    if latest_report and "report_id" in latest_report:
        match = re.search(r"IR-(\d{4})-(\d+)", latest_report["report_id"])
        if match and int(match.group(1)) == current_year:
            last_number = int(match.group(2))
            new_number = last_number + 1
            return f"IR-{current_year}-{new_number}"

    return f"IR-{current_year}-1001"

async def reverse_geocode(latitude: float, longitude: float):
    try:
        location = geolocator.reverse((latitude, longitude), language='en', timeout=10)
        if location and location.raw and 'address' in location.raw:
            address = location.raw['address']
            city_name = address.get("city") or address.get("town") or \
                        address.get("village") or address.get("state") or \
                        address.get("county")
            return {
                "country": address.get("country", "Unknown"),
                "city": city_name
            }
    except GeocoderTimedOut:
        print(f"Geocoder timed out for coordinates: {latitude}, {longitude}")
        return {"country": "Unknown", "city": None}
    except Exception as e:
        print(f"An error occurred during geocoding for coordinates {latitude}, {longitude}: {e}")
        return {"country": "Unknown", "city": None}
    return {"country": "Unknown", "city": None}

# --- نقاط نهاية الـ API (تعديل: استخدام 'router' بدلاً من 'app') ---

@router.post("/reports/", status_code=201, response_model=IncidentReport)
async def create_report(
    reporter_type: str = Form(...),
    anonymous: bool = Form(False),
    email: Optional[EmailStr] = Form(None),
    phone: Optional[str] = Form(None),
    preferred_contact: Optional[str] = Form(None),
    date: datetime.datetime = Form(..., description="Date of the incident (YYYY-MM-DD or Walpole-MM-DDTHH:MM:SS)"),
    country: Optional[str] = Form(None),
    city: Optional[str] = Form(None),
    longitude: float = Form(..., ge=-180, le=180, description="Longitude of the incident location"),
    latitude: float = Form(..., ge=-90, le=90, description="Latitude of the incident location"),
    description: str = Form(..., min_length=3, description="Detailed description of the incident"),
    violation_types: str = Form(..., description="Comma-separated list of violation types (e.g., 'detention,torture')"),
    files: Optional[List[UploadFile]] = File(None)
):
    """
    Creates a new incident report in the database, handling form data and file uploads.
    """
    # ... بقية الكود كما هي ولكن باستخدام router.post بدلاً من app.post
    violation_list = [v.strip() for v in violation_types.split(",") if v.strip()]

    location_info_from_coords = await reverse_geocode(latitude, longitude)
    resolved_country = location_info_from_coords["country"]
    resolved_city = location_info_from_coords["city"]

    if country and country.strip() and country.strip().lower() != resolved_country.lower():
        resolved_country = country.strip()
    
    if city and city.strip() and city.strip().lower() != (resolved_city or '').lower():
        resolved_city = city.strip()

    report_id = await generate_report_id()

    contact_info_data = None
    if not anonymous:
        if not email and not phone:
            raise HTTPException(status_code=400, detail="Email or phone is required if not submitting anonymously.")
        contact_info_data = ContactInfo(email=email, phone=phone, preferred_contact=preferred_contact)

    incident_report_data = IncidentReport(
        report_id=report_id,
        reporter_type=reporter_type,
        anonymous=anonymous,
        contact_info=contact_info_data,
        incident_details=IncidentDetails(
            date=date,
            location=Location(
                country=resolved_country,
                city=resolved_city,
                coordinates=Coordinates(type="Point", coordinates=[longitude, latitude])
            ),
            description=description,
            violation_types=violation_list,
        ),
        evidence=[],
        status="new",
        created_at=datetime.datetime.now(datetime.timezone.utc)
    )

    if files:
        for file in files:
            file_extension = ""
            if "." in file.filename:
                base_name, file_extension = os.path.splitext(file.filename)
                file_extension = file_extension.lower().strip()
                sanitized_base_name = re.sub(r'[^\w\s.-]', '', base_name).strip()
            else:
                sanitized_base_name = re.sub(r'[^\w\s.-]', '', file.filename).strip()

            if not sanitized_base_name:
                sanitized_base_name = "uploaded_file"
            
            unique_filename = f"{report_id}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')}_{sanitized_base_name}{file_extension}"
            file_location = os.path.join(UPLOAD_FOLDER, unique_filename)

            try:
                with open(file_location, "wb") as buffer:
                    shutil.copyfileobj(file.file, buffer)
            except Exception as e:
                print(f"Error saving file {file.filename}: {e}")
                raise HTTPException(status_code=500, detail=f"Could not save file {file.filename}: {e}")
            finally:
                file.file.close()

            ftype = "document"
            if file_extension in [".jpg", ".jpeg", ".png", ".gif", ".webp"]:
                ftype = "photo"
            elif file_extension in [".mp4", ".avi", ".mov", ".webm", ".flv"]:
                ftype = "video"

            incident_report_data.evidence.append(
                ReportEvidence(
                    type=ftype,
                    url=f"/uploads/{unique_filename}",
                    description=file.filename
                )
            )

    report_dict_to_insert = incident_report_data.model_dump(by_alias=True, exclude_none=True)
    if "_id" in report_dict_to_insert and report_dict_to_insert["_id"] is None:
        del report_dict_to_insert["_id"]

    result = await collection.insert_one(report_dict_to_insert)

    created_report_doc = await collection.find_one({"_id": result.inserted_id})
    if not created_report_doc:
        raise HTTPException(status_code=500, detail="Failed to retrieve created report after insertion.")

    if '_id' in created_report_doc:
        created_report_doc['id'] = str(created_report_doc['_id'])
        del created_report_doc['_id']

    return IncidentReport.model_validate(created_report_doc)


@router.get("/reports/", response_model=List[IncidentReport])
async def list_reports(
    status: Optional[str] = Query(None, description="Filter reports by status (e.g., 'new', 'in_progress', 'closed')"),
    start_date: Optional[datetime.date] = Query(None, description="Filter reports created on or after this date (YYYY-MM-DD)"),
    end_date: Optional[datetime.date] = Query(None, description="Filter reports created on or before this date (YYYY-MM-DD)"),
    country: Optional[str] = Query(None, description="Filter reports by country"),
    skip: int = Query(0, ge=0, description="Number of reports to skip for pagination"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of reports to return")
):
    """
    Retrieves a list of incident reports, with optional filtering and pagination.
    """
    # ... بقية الكود كما هي ولكن باستخدام router.get بدلاً من app.get
    query = {}
    if status:
        query["status"] = status

    if start_date or end_date:
        date_query = {}
        if start_date:
            date_query["$gte"] = datetime.datetime(start_date.year, start_date.month, start_date.day, 0, 0, 0, 0, tzinfo=datetime.timezone.utc)
        if end_date:
            date_query["$lte"] = datetime.datetime(end_date.year, end_date.month, end_date.day, 23, 59, 59, 999999, tzinfo=datetime.timezone.utc)
        if date_query:
            query["incident_details.date"] = date_query

    if country:
        query["incident_details.location.country"] = country

    cursor = collection.find(query).skip(skip).limit(limit)
    results = []
    async for doc in cursor:
        try:
            if '_id' in doc:
                doc['id'] = str(doc['_id'])
                del doc['_id']
            results.append(IncidentReport.model_validate(doc))
        except ValidationError as e:
            print(f"Validation error for document: {doc} - Error: {e}")
            continue
    return results


@router.get("/reports/analytics", response_model=List[dict])
async def reports_analytics():
    """
    Provides analytics on incident reports, specifically counting occurrences of violation types.
    """
    # ... بقية الكود كما هي ولكن باستخدام router.get بدلاً من app.get
    pipeline = [
        {"$unwind": "$incident_details.violation_types"},
        {"$group": {
            "_id": "$incident_details.violation_types",
            "count": {"$sum": 1}
        }},
        {"$sort": {"count": -1}}
    ]
    agg_result = await collection.aggregate(pipeline).to_list(length=100)
    return [{"violation_type": r["_id"], "count": r["count"]} for r in agg_result]


@router.get("/reports/{report_id}", response_model=IncidentReport)
async def get_report_by_id(report_id: str):
    """
    Retrieves a single incident report by its unique report ID.
    """
    # ... بقية الكود كما هي ولكن باستخدام router.get بدلاً من app.get
    report = await collection.find_one({"report_id": report_id})
    if report:
        try:
            if '_id' in report:
                report['id'] = str(report['_id'])
                del report['_id']
            return IncidentReport.model_validate(report)
        except ValidationError as e:
            print(f"Validation error for report {report_id}: {report} - Error: {e}")
            raise HTTPException(status_code=500, detail="Failed to parse report data.")
    raise HTTPException(status_code=404, detail="Report not found")


@router.patch("/reports/{report_id}", response_model=IncidentReport)
async def update_report_status(report_id: str, status_update: ReportStatusUpdate):
    """
    Updates the status of an existing incident report.
    """
    # ... بقية الكود كما هي ولكن باستخدام router.patch بدلاً من app.patch
    existing_report = await collection.find_one({"report_id": report_id})
    if not existing_report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")

    result = await collection.update_one(
        {"report_id": report_id},
        {"$set": {"status": status_update.status}}
    )

    if result.modified_count == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Report status not updated. Perhaps the status is already the same or report not found."
        )

    updated_report_doc = await collection.find_one({"report_id": report_id})
    if not updated_report_doc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve updated report.")

    if '_id' in updated_report_doc:
        updated_report_doc['id'] = str(updated_report_doc['_id'])
        del updated_report_doc['_id']

    return IncidentReport.model_validate(updated_report_doc)
