import os
import uuid
import json
from datetime import datetime
from bson import ObjectId
from pymongo import MongoClient, ASCENDING, DESCENDING
from dotenv import load_dotenv

# Load env vars
load_dotenv()

# JSON Serialization helper for MongoDB documents
def serialize_to_json(obj):
    """Convert MongoDB documents to JSON-serializable format"""
    if isinstance(obj, ObjectId):
        return str(obj)
    elif isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, dict):
        return {k: serialize_to_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [serialize_to_json(item) for item in obj]
    else:
        return obj

# MongoDB Atlas Configuration
MONGO_URI = os.getenv("MONGO_URI")
DEV_MODE = os.getenv("DEV_MODE", "false").lower() == "true"
FIREBASE_CREDENTIALS = os.getenv("FIREBASE_CREDENTIALS") or os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
FIREBASE_PROJECT_ID = os.getenv("FIREBASE_PROJECT_ID")
FIREBASE_DATABASE_URL = os.getenv("FIREBASE_DATABASE_URL")
MONGO_TIMEOUT_MS = int(os.getenv("MONGO_TIMEOUT_MS", "8000"))

# Safely extract DB_NAME or default to 'trendwear_crm'
DB_NAME = "trendwear_crm"
if MONGO_URI:
    try:
        DB_NAME = MONGO_URI.split("/")[-1].split("?")[0] or "trendwear_crm"
    except Exception:
        pass

print(f"📊 Connecting to database backend...")
print(f"Database Name: {DB_NAME}")
print(f"Dev Mode: {DEV_MODE}")

# MongoDB Atlas connection with retry logic
client = None
db = None
DB_BACKEND = "mongodb"




# Step 1: Try MongoDB Atlas
if MONGO_URI:
    try:
        print(f"📊 Connecting to MongoDB Atlas...")
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=MONGO_TIMEOUT_MS, connectTimeoutMS=MONGO_TIMEOUT_MS)
        # Verify connection with ping command
        client.admin.command("ping")
        db = client[DB_NAME]
        print("✅ Successfully connected to MongoDB Atlas!")
    except Exception as e:
        print(f"⚠️  Failed to connect to MongoDB Atlas: {str(e)}")
else:
    print("⚠️  No MONGO_URI provided; skipping connection to MongoDB Atlas.")

# Step 3: Fallback to local MongoDB
if db is None and DEV_MODE:
    print("\n🔧 DEV_MODE enabled. Attempting fallback to local MongoDB...")
    try:
        LOCAL_URI = "mongodb://localhost:27017/trendwear_crm"
        client = MongoClient(LOCAL_URI, serverSelectionTimeoutMS=5000)
        client.admin.command("ping")  # Ping to verify
        db = client["trendwear_crm"]
        DB_BACKEND = "mongodb-local"
        print("✅ Connected to local MongoDB (DEV MODE)")
    except Exception as local_e:
        print(f"❌ Local MongoDB also unavailable: {local_e}")

# Step 4: Fallback to in-memory mongomock
if db is None:
    print("\n🧪 Attempting final fallback to in-memory MongoDB (mongomock)...")
    try:
        import mongomock
        client = mongomock.MongoClient()
        db = client[DB_NAME]
        DB_BACKEND = "mongodb-memory"
        print("✅ Connected to in-memory MongoDB fallback (mongomock)")
    except Exception as fallback_err:
        raise ConnectionError(
            f"MongoDB Atlas, Firebase, and local MongoDB are unavailable. "
            f"In-memory fallback also failed: {fallback_err}\n"
            f"Please set the MONGO_URI environment variable in Render."
        )

# Collections
customers_col = db["customers"]
orders_col = db["orders"]
segments_col = db["segments"]
campaigns_col = db["campaigns"]
communications_col = db["communications"]
activity_logs_col = db["activity_logs"]


def log_activity(event_type, entity_type=None, resource_id=None, metadata=None, source="system", status="success"):
    """Persist an auditable event for queries, actions, and background jobs."""
    document = {
        "_id": f"log_{uuid.uuid4().hex[:12]}",
        "event_type": event_type,
        "entity_type": entity_type,
        "resource_id": resource_id,
        "metadata": metadata or {},
        "source": source,
        "status": status,
        "created_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    }
    activity_logs_col.insert_one(document)
    return document["_id"]

def init_db():
    """Create indexes to optimize search and segment queries."""
    try:
        # Customers indexes
        customers_col.create_index([("email", ASCENDING)], unique=True)
        customers_col.create_index([("total_spend", DESCENDING)])
        customers_col.create_index([("total_orders", DESCENDING)])
        customers_col.create_index([("last_order_date", DESCENDING)])
        customers_col.create_index([("city", ASCENDING)])

        # Orders indexes
        orders_col.create_index([("customer_id", ASCENDING)])
        orders_col.create_index([("category", ASCENDING)])
        orders_col.create_index([("order_date", DESCENDING)])

        # Campaigns indexes
        campaigns_col.create_index([("created_at", DESCENDING)])

        # Communications indexes
        communications_col.create_index([("campaign_id", ASCENDING)])
        communications_col.create_index([("customer_id", ASCENDING)])
        communications_col.create_index([("status", ASCENDING)])

        # Activity logs indexes
        activity_logs_col.create_index([("created_at", DESCENDING)])
        activity_logs_col.create_index([("event_type", ASCENDING), ("created_at", DESCENDING)])
        activity_logs_col.create_index([("entity_type", ASCENDING), ("created_at", DESCENDING)])
        activity_logs_col.create_index([("resource_id", ASCENDING), ("created_at", DESCENDING)])
        
        print("Database indexes successfully initialized.")
    except Exception as e:
        print(f"Error initializing indexes: {e}")

if __name__ == "__main__":
    init_db()
