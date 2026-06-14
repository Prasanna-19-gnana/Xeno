from flask import Blueprint, request, jsonify
from models import customers_col, orders_col, communications_col, serialize_to_json
from seed_data import seed_database

customers_bp = Blueprint("customers", __name__)

@customers_bp.route("/generate", methods=["POST"])
def generate_customers():
    try:
        num_cust, num_ord = seed_database()
        return jsonify({
            "status": "success",
            "message": f"Seeded {num_cust} customers and {num_ord} orders successfully."
        }), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Seeding failed: {str(e)}"
        }), 500

@customers_bp.route("", methods=["GET"])
def get_customers():
    try:
        # Pagination
        page = int(request.args.get("page", 1))
        limit = int(request.args.get("limit", 20))
        skip = (page - 1) * limit

        # Filtering
        query = {}
        search = request.args.get("search", "")
        if search:
            query["$or"] = [
                {"name": {"$regex": search, "$options": "i"}},
                {"email": {"$regex": search, "$options": "i"}},
                {"phone": {"$regex": search, "$options": "i"}},
                {"city": {"$regex": search, "$options": "i"}}
            ]
        
        city = request.args.get("city", "")
        if city:
            query["city"] = city
            
        gender = request.args.get("gender", "")
        if gender:
            query["gender"] = gender

        # Sorting
        sort_by = request.args.get("sort_by", "total_spend")
        sort_order = int(request.args.get("sort_order", -1))  # -1 for desc, 1 for asc
        
        # Validate sort field to avoid DB errors
        allowed_sorts = ["name", "city", "gender", "age", "total_spend", "total_orders", "last_order_date"]
        if sort_by not in allowed_sorts:
            sort_by = "total_spend"

        total = customers_col.count_documents(query)
        cursor = customers_col.find(query).sort(sort_by, sort_order).skip(skip).limit(limit)
        
        customers = list(cursor)
        
        return jsonify({
            "status": "success",
            "total": total,
            "page": page,
            "limit": limit,
            "data": customers
        }), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@customers_bp.route("/<string:customer_id>", methods=["GET"])
def get_customer_by_id(customer_id):
    try:
        customer = customers_col.find_one({"_id": customer_id})
        if not customer:
            return jsonify({
                "status": "error",
                "message": f"Customer with ID {customer_id} not found."
            }), 404

        # Fetch customer's orders
        orders = list(orders_col.find({"customer_id": customer_id}).sort("order_date", -1))
        
        # Fetch customer's communications
        communications = list(communications_col.find({"customer_id": customer_id}).sort("created_at", -1))

        return jsonify({
            "status": "success",
            "data": {
                "customer": customer,
                "orders": orders,
                "communications": communications
            }
        }), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500
