from pymongo import MongoClient

MONGO_URI = "mongodb://localhost:27017"

client = MongoClient(MONGO_URI)

db = client["human_rights_db"]

case_collection = db["cases"]

case_history_collection = db["case_status_history"]