from flask import Blueprint, request, jsonify
from models import orders_col, serialize_to_json

orders_bp = Blueprint("orders", __name__)

@orders_bp.route("", methods=["GET"])
def get_orders():
    try:
        page = int(request.args.get("page", 1))
        limit = int(request.args.get("limit", 20))
        skip = (page - 1) * limit

        # Filtering
        query = {}
        category = request.args.get("category", "")
        if category:
            query["category"] = category

        min_amount = request.args.get("min_amount", "")
        max_amount = request.args.get("max_amount", "")
        if min_amount or max_amount:
            query["amount"] = {}
            if min_amount:
                query["amount"]["$gte"] = int(min_amount)
            if max_amount:
                query["amount"]["$lte"] = int(max_amount)

        # Sorting
        sort_field = request.args.get("sort_by", "order_date")
        sort_order = int(request.args.get("sort_order", -1))  # -1 for desc, 1 for asc
        
        # Validations
        allowed_sorts = ["amount", "order_date", "category"]
        if sort_field not in allowed_sorts:
            sort_field = "order_date"

        # Count total matches
        total = orders_col.count_documents(query)

        # Aggregation pipeline to join customer name
        pipeline = [
            {"$match": query},
            {"$lookup": {
                "from": "customers",
                "localField": "customer_id",
                "foreignField": "_id",
                "as": "customer_info"
            }},
            {"$unwind": {
                "path": "$customer_info",
                "preserveNullAndEmptyArrays": True
            }},
            {"$project": {
                "_id": 1,
                "customer_id": 1,
                "customer_name": {"$ifNull": ["$customer_info.name", "Unknown"]},
                "amount": 1,
                "category": 1,
                "order_date": 1
            }},
            {"$sort": {sort_field: sort_order}},
            {"$skip": skip},
            {"$limit": limit}
        ]

        orders = list(orders_col.aggregate(pipeline))

        return jsonify({
            "status": "success",
            "total": total,
            "page": page,
            "limit": limit,
            "data": orders
        }), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500
