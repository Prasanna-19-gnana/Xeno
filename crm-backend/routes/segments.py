import uuid
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify
from models import segments_col, customers_col, orders_col, serialize_to_json

segments_bp = Blueprint("segments", __name__)

def compile_segment_rules(rules):
    """
    Translates rule parameters into a MongoDB query dictionary.
    Rules dictionary format:
    {
        "total_spend_gt": 5000,
        "total_orders_gte": 5,
        "city_eq": "Chennai",
        "inactive_days_gt": 30,
        "category_bought": "Shoes"
    }
    """
    mongo_query = {}
    
    # Total spend rule
    if "total_spend_gt" in rules and rules["total_spend_gt"] is not None:
        try:
            mongo_query["total_spend"] = {"$gt": float(rules["total_spend_gt"])}
        except ValueError:
            pass

    # Total orders rule
    if "total_orders_gte" in rules and rules["total_orders_gte"] is not None:
        try:
            mongo_query["total_orders"] = {"$gte": int(rules["total_orders_gte"])}
        except ValueError:
            pass

    # City rule
    if "city_eq" in rules and rules["city_eq"]:
        mongo_query["city"] = rules["city_eq"]

    # Inactivity rule: last_order_date is older than today - X days
    if "inactive_days_gt" in rules and rules["inactive_days_gt"] is not None:
        try:
            days = int(rules["inactive_days_gt"])
            # Use current date dynamically
            reference_date = datetime.utcnow()
            cutoff_date = (reference_date - timedelta(days=days)).strftime("%Y-%m-%d")
            mongo_query["last_order_date"] = {"$lt": cutoff_date, "$ne": ""}
        except ValueError:
            pass

    # Category purchased rule
    if "category_bought" in rules and rules["category_bought"]:
        category = rules["category_bought"]
        # Find all customer IDs who bought this category
        customer_ids = orders_col.distinct("customer_id", {"category": category})
        # If there are no orders for this category, make sure we return no customers
        if not customer_ids:
            mongo_query["_id"] = {"$in": []}
        else:
            mongo_query["_id"] = {"$in": customer_ids}

    return mongo_query

@segments_bp.route("", methods=["POST"])
def create_segment():
    try:
        data = request.json or {}
        name = data.get("name")
        rules = data.get("rules", {})

        if not name:
            return jsonify({
                "status": "error",
                "message": "Segment name is required."
            }), 400

        # Calculate matching customers
        mongo_query = compile_segment_rules(rules)
        customer_count = customers_col.count_documents(mongo_query)

        segment_id = f"seg_{uuid.uuid4().hex[:12]}"
        segment_doc = {
            "_id": segment_id,
            "name": name,
            "rules": rules,
            "customer_count": customer_count,
            "created_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        }

        segments_col.insert_one(segment_doc)

        return jsonify({
            "status": "success",
            "data": segment_doc
        }), 201
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@segments_bp.route("", methods=["GET"])
def get_segments():
    try:
        segments = list(segments_col.find().sort("created_at", -1))
        # Serialize MongoDB documents for JSON response
        serialized_segments = [serialize_to_json(seg) for seg in segments]
        return jsonify({
            "status": "success",
            "data": serialized_segments
        }), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@segments_bp.route("/<string:segment_id>/customers", methods=["GET"])
def get_segment_customers(segment_id):
    try:
        segment = segments_col.find_one({"_id": segment_id})
        if not segment:
            return jsonify({
                "status": "error",
                "message": f"Segment with ID {segment_id} not found."
            }), 404

        # For pre-created segments with customer_ids
        if "customer_ids" in segment and segment["customer_ids"]:
            customer_ids = segment["customer_ids"]
            mongo_query = {"_id": {"$in": customer_ids}}
        else:
            # For custom segments with rules
            rules = segment.get("rules", {})
            mongo_query = compile_segment_rules(rules)

        # Pagination
        page = int(request.args.get("page", 1))
        limit = int(request.args.get("limit", 20))
        skip = (page - 1) * limit

        total = customers_col.count_documents(mongo_query)
        cursor = customers_col.find(mongo_query).sort("total_spend", -1).skip(skip).limit(limit)
        customers = list(cursor)
        
        # Serialize for JSON response
        serialized_customers = [serialize_to_json(cust) for cust in customers]

        return jsonify({
            "status": "success",
            "total": total,
            "page": page,
            "limit": limit,
            "segment_name": segment["name"],
            "data": serialized_customers
        }), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500
