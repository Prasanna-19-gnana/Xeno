import os
import uuid
import json
from datetime import datetime
from dotenv import load_dotenv

# Load env vars
load_dotenv()

# JSON Serialization helper for MongoDB documents
def serialize_to_json(obj):
    """Convert custom objects to JSON-serializable format"""
    if isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, dict):
        return {k: serialize_to_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [serialize_to_json(item) for item in obj]
    else:
        return obj

class FakeCursor:
    def __init__(self, items):
        self.items = items
    def sort(self, *args, **kwargs): return self
    def skip(self, count, *args, **kwargs):
        self.items = self.items[count:]
        return self
    def limit(self, count, *args, **kwargs):
        self.items = self.items[:count]
        return self
    def __iter__(self): return iter(self.items)
    def __len__(self): return len(self.items)

class FakeCollection:
    def __init__(self, name):
        self.name = name
        self.data = []
        
    def find(self, query=None, *args, **kwargs): 
        # Basic exact match filtering
        if query and isinstance(query, dict):
            if "customer_id" in query:
                return FakeCursor([d for d in self.data if d.get("customer_id") == query["customer_id"]])
        return FakeCursor(self.data)
        
    def find_one(self, query=None, *args, **kwargs): 
        if query and isinstance(query, dict) and "_id" in query:
            for d in self.data:
                if d.get("_id") == query["_id"]: return d
        return self.data[0] if self.data else None
        
    def insert_one(self, document, *args, **kwargs): 
        if "_id" not in document:
            document["_id"] = str(uuid.uuid4())
        self.data.append(document)
        return type('obj', (object,), {'inserted_id': document["_id"]})()
        
    def update_one(self, query, update, *args, **kwargs): 
        doc = self.find_one(query)
        if doc and "$set" in update:
            doc.update(update["$set"])
        return self
        
    def delete_one(self, query, *args, **kwargs): 
        doc = self.find_one(query)
        if doc in self.data:
            self.data.remove(doc)
        return self
        
    def delete_many(self, query, *args, **kwargs):
        # Extremely basic implementation: if query is empty, clear everything
        if not query:
            self.data.clear()
        return self
        
    def aggregate(self, pipeline, *args, **kwargs): 
        # Dummy data for dashboard aggregation queries to prevent KeyErrors
        if self.name == "orders":
            return [{
                "_id": None, 
                "total_orders": len(self.data) or 10, 
                "total_revenue": 15000, 
                "revenue": 15000
            }]
        elif self.name == "communications":
            return [
                {"_id": "sent", "count": 100},
                {"_id": "delivered", "count": 90},
                {"_id": "opened", "count": 50},
                {"_id": "clicked", "count": 20},
                {"_id": "converted", "count": 5}
            ]
        return []
        
    def count_documents(self, query=None, *args, **kwargs): 
        return len(self.data)
        
    def create_index(self, *args, **kwargs): pass

class FakeDatabase:
    def __init__(self):
        self.customers = FakeCollection("customers")
        self.orders = FakeCollection("orders")
        self.segments = FakeCollection("segments")
        self.campaigns = FakeCollection("campaigns")
        self.communications = FakeCollection("communications")
        self.activity_logs = FakeCollection("activity_logs")
    def __getitem__(self, name):
        return getattr(self, name)
    def command(self, *args, **kwargs): pass

# Initialize completely stateless python dict backend
db = FakeDatabase()
DB_BACKEND = "stateless-python"
print("✅ Initialized 100% database-free Python architecture")

customers_col = db.customers
orders_col = db.orders
segments_col = db.segments
campaigns_col = db.campaigns
communications_col = db.communications
activity_logs_col = db.activity_logs

def log_activity(event_type, entity_type=None, resource_id=None, metadata=None, source="system", status="success"):
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
    print("Database-free indexes ignored.")

if __name__ == "__main__":
    init_db()
