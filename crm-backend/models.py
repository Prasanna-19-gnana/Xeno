import os
import uuid
import json
from datetime import datetime
from bson import ObjectId
import mongomock
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

# Unconditionally use mongomock
client = mongomock.MongoClient()
db = client["trendwear_crm"]
DB_BACKEND = "mongodb-memory"
print("✅ Initialized stateless in-memory database (mongomock)")

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
        customers_col.create_index([("email", 1)], unique=True)
        customers_col.create_index([("total_spend", -1)])
        customers_col.create_index([("total_orders", -1)])
        customers_col.create_index([("last_order_date", -1)])
        customers_col.create_index([("city", 1)])

        # Orders indexes
        orders_col.create_index([("customer_id", 1)])
        orders_col.create_index([("category", 1)])
        orders_col.create_index([("order_date", -1)])

        # Campaigns indexes
        campaigns_col.create_index([("created_at", -1)])

        # Communications indexes
        communications_col.create_index([("campaign_id", 1)])
        communications_col.create_index([("customer_id", 1)])
        communications_col.create_index([("status", 1)])

        # Activity logs indexes
        activity_logs_col.create_index([("created_at", -1)])
        activity_logs_col.create_index([("event_type", 1), ("created_at", -1)])
        activity_logs_col.create_index([("entity_type", 1), ("created_at", -1)])
        activity_logs_col.create_index([("resource_id", 1), ("created_at", -1)])
        
        print("Database indexes successfully initialized.")
    except Exception as e:
        print(f"Error initializing indexes: {e}")

if __name__ == "__main__":
    init_db()
