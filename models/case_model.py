from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import datetime


class Coordinates(BaseModel):
    type: Literal["Point"] = "Point"
    coordinates: List[float]  # [longitude, latitude]


class Location(BaseModel):
    country: str
    region: Optional[str] = None
    coordinates: Optional[Coordinates] = None


class EvidenceItem(BaseModel):
    type: str  # e.g., photo, video, document
    url: str
    description: Optional[str] = None
    date_captured: Optional[datetime] = None


class Perpetrator(BaseModel):
    name: str
    type: Optional[str] = None  # e.g., military_unit, police, militia


class Case(BaseModel):
    case_id: str
    title: str
    description: str
    violation_types: List[str]

    status: str = "new"
    priority: Optional[str] = None

    location: Location

    date_occurred: datetime
    date_reported: datetime

    victims: Optional[List[str]] = []  # Can be ObjectId strings
    perpetrators: Optional[List[Perpetrator]] = []
    evidence: Optional[List[EvidenceItem]] = []

    created_by: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
