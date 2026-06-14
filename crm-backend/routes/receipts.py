import random
import uuid
from datetime import datetime
from flask import Blueprint, request, jsonify
from models import communications_col, customers_col, orders_col, campaigns_col, log_activity, serialize_to_json

receipts_bp = Blueprint("receipts", __name__)

CATEGORIES = ["T-Shirts", "Jeans", "Shoes", "Dresses", "Accessories"]
CATEGORY_PRICE_RANGES = {
    "T-Shirts": (399, 1499),
    "Jeans": (999, 3499),
    "Shoes": (1499, 5999),
    "Dresses": (899, 4599),
    "Accessories": (199, 1999)
}

@receipts_bp.route("", methods=["POST"])
def receive_receipt():
    try:
        data = request.json or {}
        comm_id = data.get("communication_id")
        status = data.get("status")

        if not comm_id or not status:
            return jsonify({
                "status": "error",
                "message": "communication_id and status are required."
            }), 400

        # Find communication
        comm = communications_col.find_one({"_id": comm_id})
        if not comm:
            return jsonify({
                "status": "error",
                "message": f"Communication with ID {comm_id} not found."
            }), 404

        # Update status and events list
        communications_col.update_one(
            {"_id": comm_id},
            {
                "$set": {"status": status},
                "$addToSet": {"events": status}
            }
        )

        try:
            log_activity(
                event_type="receipt_processed",
                entity_type="communication",
                resource_id=comm_id,
                metadata={
                    "status": status,
                    "campaign_id": comm.get("campaign_id"),
                    "customer_id": comm.get("customer_id")
                },
                source="system"
            )
        except Exception as audit_error:
            print(f"Warning: failed to persist receipt log for {comm_id}: {audit_error}")

        # Conversion simulation: if click is received, simulate 25% chance of purchase
        if status == "clicked" and random.random() < 0.25:
            # Update communication to converted
            communications_col.update_one(
                {"_id": comm_id},
                {
                    "$set": {"status": "converted"},
                    "$addToSet": {"events": "converted"}
                }
            )

            # Get customer details to generate realistic purchase
            customer_id = comm["customer_id"]
            customer = customers_col.find_one({"_id": customer_id})
            
            if customer:
                # Find campaigns category or pick random
                campaign = campaigns_col.find_one({"_id": comm["campaign_id"]})
                category = "Accessories"
                
                # Check if campaign has target category from name or description
                if campaign:
                    camp_name = campaign["name"].lower()
                    for cat in CATEGORIES:
                        if cat.lower() in camp_name:
                            category = cat
                            break
                    else:
                        category = random.choice(CATEGORIES)
                else:
                    category = random.choice(CATEGORIES)

                price_range = CATEGORY_PRICE_RANGES[category]
                amount = random.randint(price_range[0], price_range[1])
                
                order_id = f"ord_{uuid.uuid4().hex[:12]}"
                today_str = datetime.utcnow().strftime("%Y-%m-%d")
                
                new_order = {
                    "_id": order_id,
                    "customer_id": customer_id,
                    "campaign_id": comm["campaign_id"],
                    "communication_id": comm_id,
                    "amount": amount,
                    "category": category,
                    "order_date": today_str
                }
                
                # Insert order
                orders_col.insert_one(new_order)

                try:
                    log_activity(
                        event_type="order_created_from_campaign",
                        entity_type="order",
                        resource_id=order_id,
                        metadata={
                            "campaign_id": comm["campaign_id"],
                            "communication_id": comm_id,
                            "customer_id": customer_id,
                            "amount": amount,
                            "category": category
                        },
                        source="system"
                    )
                except Exception as audit_error:
                    print(f"Warning: failed to persist order creation log for {order_id}: {audit_error}")

                # Update customer spend and total orders
                customers_col.update_one(
                    {"_id": customer_id},
                    {
                        "$inc": {
                            "total_spend": amount,
                            "total_orders": 1
                        },
                        "$set": {
                            "last_order_date": today_str
                        }
                    }
                )
                print(f"Simulated conversion order {order_id} (amount {amount}) for customer {customer_id}")

        return jsonify({
            "status": "success",
            "message": f"Receipt processed successfully for communication {comm_id}"
        }), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500
