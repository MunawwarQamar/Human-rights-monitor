from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class Case(BaseModel):
    case_id: str
    title: str
    description: str
    violation_types: List[str]
    status: str = "new"
    priority: Optional[str] = None
    location: Optional[dict] = None
    date_occurred: datetime
    date_reported: datetime
    victims: List[str]
    perpetrators: Optional[List[dict]] = None
    evidence: Optional[List[dict]] = None
    created_by: str
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
