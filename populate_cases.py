import requests
from datetime import datetime

API_URL = "http://127.0.0.1:8000/api/cases"

sample_cases = [
    {
        "case_id": "HRM-2023-1001",
        "title": "Arbitrary Arrest in City Center",
        "description": "Several protesters were arrested without warrants.",
        "violation_types": ["arbitrary_arrest"],
        "status": "under_investigation",
        "priority": "high",
        "location": {
            "country": "Egypt",
            "region": "Cairo Governorate",
            "coordinates": {"type": "Point", "coordinates": [31.2357, 30.0444]}
        },
        "date_occurred": "2023-03-10T00:00:00",
        "date_reported": "2023-03-11T00:00:00",
        "victims": ["601c5f77bcf86cd799439011"],
        "perpetrators": [{"name": "Police Unit 7", "type": "police"}],
        "evidence": [
            {
                "type": "photo",
                "url": "/uploads/arrest-egypt.jpg",
                "description": "Photos of detained youth",
                "date_captured": "2023-03-10T00:00:00"
            }
        ],
        "created_by": "admin"
    },
    {
        "case_id": "HRM-2023-1002",
        "title": "Torture Allegation in Detention Center",
        "description": "Former detainees reported physical abuse.",
        "violation_types": ["torture"],
        "status": "new",
        "priority": "medium",
        "location": {
            "country": "Tunisia",
            "region": "Sfax",
            "coordinates": {"type": "Point", "coordinates": [10.7603, 34.7406]}
        },
        "date_occurred": "2023-01-20T00:00:00",
        "date_reported": "2023-01-25T00:00:00",
        "victims": [],
        "perpetrators": [{"name": "Detention Center Staff", "type": "military_unit"}],
        "evidence": [],
        "created_by": "admin"
    },
    {
        "case_id": "HRM-2023-1003",
        "title": "Enforced Disappearance near Border",
        "description": "Family members lost contact with 3 individuals.",
        "violation_types": ["enforced_disappearance"],
        "status": "resolved",
        "priority": "high",
        "location": {
            "country": "Lebanon",
            "region": "Bekaa Valley",
            "coordinates": {"type": "Point", "coordinates": [35.8739, 33.8338]}
        },
        "date_occurred": "2023-02-05T00:00:00",
        "date_reported": "2023-02-07T00:00:00",
        "victims": ["601c5f77bcf86cd799439012", "601c5f77bcf86cd799439013"],
        "perpetrators": [],
        "evidence": [],
        "created_by": "admin"
    },
    {
        "case_id": "HRM-2023-1004",
        "title": "Unlawful Demolition of Homes",
        "description": "Several homes were bulldozed without court orders.",
        "violation_types": ["property_destruction"],
        "status": "under_investigation",
        "priority": "low",
        "location": {
            "country": "Palestine",
            "region": "Hebron",
            "coordinates": {"type": "Point", "coordinates": [35.0954, 31.5326]}
        },
        "date_occurred": "2023-04-12T00:00:00",
        "date_reported": "2023-04-13T00:00:00",
        "victims": [],
        "perpetrators": [{"name": "Civil Administration", "type": "government"}],
        "evidence": [
            {
                "type": "video",
                "url": "/uploads/demolition-video.mp4",
                "description": "Video showing bulldozers in action",
                "date_captured": "2023-04-12T00:00:00"
            }
        ],
        "created_by": "monitor_user"
    },
    {
        "case_id": "HRM-2023-1005",
        "title": "Suppression of Peaceful Protest",
        "description": "Protesters were dispersed violently by security.",
        "violation_types": ["freedom_of_assembly"],
        "status": "resolved",
        "priority": "medium",
        "location": {
            "country": "Jordan",
            "region": "Amman",
            "coordinates": {"type": "Point", "coordinates": [35.9106, 31.9539]}
        },
        "date_occurred": "2023-05-01T00:00:00",
        "date_reported": "2023-05-02T00:00:00",
        "victims": [],
        "perpetrators": [{"name": "Riot Control Police", "type": "police"}],
        "evidence": [],
        "created_by": "observer"
    },
    {
        "case_id": "HRM-2023-1006",
        "title": "Blockade of Humanitarian Aid",
        "description": "Trucks with medical supplies were denied access.",
        "violation_types": ["denial_of_humanitarian_access"],
        "status": "under_investigation",
        "priority": "high",
        "location": {
            "country": "Syria",
            "region": "Idlib",
            "coordinates": {"type": "Point", "coordinates": [36.6410, 35.9306]}
        },
        "date_occurred": "2023-06-10T00:00:00",
        "date_reported": "2023-06-11T00:00:00",
        "victims": [],
        "perpetrators": [],
        "evidence": [],
        "created_by": "admin"
    },
    {
        "case_id": "HRM-2023-1007",
        "title": "Media Censorship Incident",
        "description": "News outlet forcibly shut down by authorities.",
        "violation_types": ["freedom_of_expression"],
        "status": "new",
        "priority": "low",
        "location": {
            "country": "Morocco",
            "region": "Rabat",
            "coordinates": {"type": "Point", "coordinates": [-6.8498, 34.0209]}
        },
        "date_occurred": "2023-07-15T00:00:00",
        "date_reported": "2023-07-16T00:00:00",
        "victims": [],
        "perpetrators": [],
        "evidence": [],
        "created_by": "journalist"
    },
    {
        "case_id": "HRM-2023-1008",
        "title": "Refugee Camp Raid",
        "description": "Night raid in refugee camp caused injuries.",
        "violation_types": ["arbitrary_arrest", "torture"],
        "status": "under_investigation",
        "priority": "high",
        "location": {
            "country": "Sudan",
            "region": "Darfur",
            "coordinates": {"type": "Point", "coordinates": [24.9042, 13.6275]}
        },
        "date_occurred": "2023-08-22T00:00:00",
        "date_reported": "2023-08-23T00:00:00",
        "victims": ["601c5f77bcf86cd799439015"],
        "perpetrators": [{"name": "Paramilitary Group", "type": "militia"}],
        "evidence": [],
        "created_by": "field_agent"
    },
    {
        "case_id": "HRM-2023-1009",
        "title": "School Bombing Incident",
        "description": "Airstrike hit a school with children inside.",
        "violation_types": ["attacks_on_civilians"],
        "status": "resolved",
        "priority": "high",
        "location": {
            "country": "Yemen",
            "region": "Sanaa",
            "coordinates": {"type": "Point", "coordinates": [44.2066, 15.3694]}
        },
        "date_occurred": "2023-09-05T00:00:00",
        "date_reported": "2023-09-06T00:00:00",
        "victims": [],
        "perpetrators": [],
        "evidence": [],
        "created_by": "ngo_partner"
    },
    {
        "case_id": "HRM-2023-1010",
        "title": "Blocked Internet Access During Protest",
        "description": "Internet blackout during mass protest.",
        "violation_types": ["freedom_of_expression"],
        "status": "new",
        "priority": "medium",
        "location": {
            "country": "Algeria",
            "region": "Algiers",
            "coordinates": {"type": "Point", "coordinates": [3.0588, 36.7538]}
        },
        "date_occurred": "2023-10-12T00:00:00",
        "date_reported": "2023-10-13T00:00:00",
        "victims": [],
        "perpetrators": [],
        "evidence": [],
        "created_by": "admin"
    }
]

for case in sample_cases:
    try:
        response = requests.post(API_URL, json=case)
        print(f"\U0001F4E4 Sent: {case['case_id']} - Status: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"\u274C Error sending {case['case_id']}: {e}")
