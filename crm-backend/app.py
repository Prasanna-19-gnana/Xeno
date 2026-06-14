import os
import json
from datetime import datetime
from flask import Flask, jsonify, g, request
from flask_cors import CORS
from bson import ObjectId
from dotenv import load_dotenv

from models import DB_BACKEND, init_db, db, log_activity, serialize_to_json
from routes.customers import customers_bp
from routes.orders import orders_bp
from routes.segments import segments_bp
from routes.campaigns import campaigns_bp
from routes.receipts import receipts_bp
from routes.ai import ai_bp
from routes.ml import ml_bp

# Load environment variables
load_dotenv()

# Custom JSON Encoder for MongoDB/BSON types
class MongoDBJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        elif isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

app = Flask(__name__)
app.json_encoder = MongoDBJSONEncoder  # Use custom encoder for JSON responses

# Enable CORS for all domains to ease frontend integration
CORS(app)


@app.before_request
def capture_audit_context():
    if not request.path.startswith("/api/") or request.method == "OPTIONS":
        return
    g.audit_payload = request.get_json(silent=True)


@app.after_request
def persist_api_activity(response):
    if request.path.startswith("/api/") and request.method != "OPTIONS":
        payload = getattr(g, "audit_payload", None)
        resource_id = None

        if request.view_args:
            for key in ("campaign_id", "segment_id", "customer_id", "communication_id", "order_id"):
                if key in request.view_args:
                    resource_id = request.view_args[key]
                    break

        if resource_id is None and isinstance(payload, dict):
            for key in ("campaign_id", "segment_id", "customer_id", "communication_id", "order_id"):
                if key in payload:
                    resource_id = payload[key]
                    break

        try:
            path_parts = request.path.split("/")
            entity_type = path_parts[2] if len(path_parts) > 2 else None
            log_activity(
                event_type="query" if request.method == "GET" else "action",
                entity_type=entity_type,
                resource_id=resource_id,
                metadata={
                    "method": request.method,
                    "path": request.path,
                    "endpoint": request.endpoint,
                    "query_params": request.args.to_dict(flat=True),
                    "payload": payload,
                    "response_status": response.status_code
                },
                source="request",
                status="success" if response.status_code < 400 else "error"
            )
        except Exception as audit_error:
            print(f"Warning: failed to persist audit log for {request.method} {request.path}: {audit_error}")

    return response

# Register Blueprints
app.register_blueprint(customers_bp, url_prefix="/api/customers")
app.register_blueprint(orders_bp, url_prefix="/api/orders")
app.register_blueprint(segments_bp, url_prefix="/api/segments")
app.register_blueprint(campaigns_bp, url_prefix="/api/campaigns")
app.register_blueprint(receipts_bp, url_prefix="/api/receipts")
app.register_blueprint(ai_bp, url_prefix="/api/ai")
app.register_blueprint(ml_bp)

@app.route("/api/health", methods=["GET"])
def health_check():
    try:
        # Check database connectivity
        db.command("ping")
        is_mongo = "mongodb" in DB_BACKEND or DB_BACKEND == "mongodb"
        db_status = "MongoDB is connected" if is_mongo else f"Database backend is {DB_BACKEND}"
        
        return jsonify({
            "status": "success",
            "message": f"CRM Backend is healthy. {db_status}.",
            "database_backend": DB_BACKEND,
            "timestamp": "2026-06-10 20:46:47"
        }), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Unhealthy CRM backend: {str(e)}"
        }), 500

@app.route("/api/dashboard/stats", methods=["GET"])
def get_dashboard_stats():
    try:
        # 1. Total Customers
        total_customers = db["customers"].count_documents({})
        
        # 2. Total Campaigns
        total_campaigns = db["campaigns"].count_documents({})
        
        # 3. Order aggregates (orders, revenue, AOV)
        order_pipeline = [
            {"$group": {
                "_id": None,
                "total_orders": {"$sum": 1},
                "total_revenue": {"$sum": "$amount"}
            }}
        ]
        order_stats = list(db["orders"].aggregate(order_pipeline))
        
        if order_stats:
            total_orders = order_stats[0]["total_orders"]
            total_revenue = order_stats[0]["total_revenue"]
            aov = round(total_revenue / total_orders, 2) if total_orders > 0 else 0
        else:
            total_orders = 0
            total_revenue = 0
            aov = 0

        # 4. Campaign Chart Data (recent 5 campaigns)
        campaigns = list(db["campaigns"].find().sort("created_at", -1).limit(5))
        chart_data = []
        total_attributed_orders = 0
        total_attributed_revenue = 0
        
        for camp in campaigns:
            comm_pipeline = [
                {"$match": {"campaign_id": camp["_id"]}},
                {"$group": {
                    "_id": "$status",
                    "count": {"$sum": 1}
                }}
            ]
            comm_stats = list(db["communications"].aggregate(comm_pipeline))
            
            stats = {
                "sent": 0,
                "delivered": 0,
                "opened": 0,
                "clicked": 0,
                "converted": 0,
                "failed": 0
            }
            for item in comm_stats:
                status = item["_id"]
                if status in stats:
                    stats[status] = item["count"]
            
            delivered_total = stats["delivered"] + stats["opened"] + stats["clicked"] + stats["converted"]
            opened_total = stats["opened"] + stats["clicked"] + stats["converted"]
            clicked_total = stats["clicked"] + stats["converted"]
            converted_total = stats["converted"]
            failed_total = stats["failed"]
            sent_total = stats["sent"] + delivered_total + failed_total
            delivery_rate = round((delivered_total / sent_total) * 100, 1) if sent_total else 0
            open_rate = round((opened_total / delivered_total) * 100, 1) if delivered_total else 0
            click_rate = round((clicked_total / opened_total) * 100, 1) if opened_total else 0
            conversion_rate = round((converted_total / clicked_total) * 100, 1) if clicked_total else 0

            attributed_orders = db["orders"].count_documents({"campaign_id": camp["_id"]})
            attributed_revenue_stats = list(db["orders"].aggregate([
                {"$match": {"campaign_id": camp["_id"]}},
                {"$group": {"_id": None, "revenue": {"$sum": "$amount"}}}
            ]))
            attributed_revenue = attributed_revenue_stats[0]["revenue"] if attributed_revenue_stats else 0

            total_attributed_orders += attributed_orders
            total_attributed_revenue += attributed_revenue
            
            chart_data.append({
                "id": camp["_id"],
                "name": camp["name"],
                "channel": camp["channel"],
                "sent": sent_total,
                "delivered": delivered_total,
                "opened": opened_total,
                "clicked": clicked_total,
                "converted": converted_total,
                "delivery_rate": delivery_rate,
                "open_rate": open_rate,
                "click_rate": click_rate,
                "conversion_rate": conversion_rate,
                "attributed_orders": attributed_orders,
                "attributed_revenue": attributed_revenue,
            })

        return jsonify({
            "status": "success",
            "data": {
                "total_customers": total_customers,
                "total_campaigns": total_campaigns,
                "total_orders": total_orders,
                "total_revenue": total_revenue,
                "average_order_value": aov,
                "total_attributed_orders": total_attributed_orders,
                "total_attributed_revenue": total_attributed_revenue,
                "recent_campaigns": chart_data
            }
        }), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route("/api/audit-logs", methods=["GET"])
def get_audit_logs():
    """Retrieve activity logs with optional filters for campaigns, queries, and actions."""
    try:
        page = int(request.args.get("page", 1))
        limit = int(request.args.get("limit", 50))
        skip = (page - 1) * limit

        # Build query filter
        query = {}
        
        event_type = request.args.get("event_type", "")  # "query", "action", "campaign_created", etc.
        if event_type:
            query["event_type"] = event_type
        
        entity_type = request.args.get("entity_type", "")  # "campaign", "customer", "order", etc.
        if entity_type:
            query["entity_type"] = entity_type
        
        resource_id = request.args.get("resource_id", "")
        if resource_id:
            query["resource_id"] = resource_id
        
        source = request.args.get("source", "")  # "request", "system"
        if source:
            query["source"] = source

        total = db["activity_logs"].count_documents(query)
        logs = list(db["activity_logs"].find(query).sort("created_at", -1).skip(skip).limit(limit))

        return jsonify({
            "status": "success",
            "total": total,
            "page": page,
            "limit": limit,
            "data": logs
        }), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route("/", methods=["GET"])
def index():
    return jsonify({
        "app": "TrendWear CRM Backend",
        "status": "running"
    }), 200

# Initialize DB indexes and run app
if __name__ == "__main__":
    print("Initializing MongoDB indexes...")
    init_db()
    
    port = int(os.getenv("PORT", 5000))
    debug_mode = os.getenv("FLASK_ENV", "development") == "development"
    
    print(f"Starting CRM Backend Server on port {port}...")
    app.run(host="0.0.0.0", port=port, debug=debug_mode, use_reloader=False)
