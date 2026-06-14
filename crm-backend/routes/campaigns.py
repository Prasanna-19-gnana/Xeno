import uuid
import os
import threading
import requests
from datetime import datetime
from flask import Blueprint, request, jsonify
from models import campaigns_col, communications_col, segments_col, customers_col, orders_col, log_activity, serialize_to_json
from routes.segments import compile_segment_rules


def validate_campaign_segment(campaign_id):
    """Validate that campaign's segment exists, attempt repair if missing"""
    campaign = campaigns_col.find_one({"_id": campaign_id})
    if not campaign:
        return None, "Campaign not found"
    
    segment_id = campaign.get("segment_id")
    segment = segments_col.find_one({"_id": segment_id})
    
    if not segment:
        print(f"⚠️  Segment {segment_id} for campaign {campaign_id} not found. Marking campaign as orphaned.")
        # Mark campaign as failed rather than allowing send
        campaigns_col.update_one(
            {"_id": campaign_id},
            {"$set": {"status": "failed", "error": f"Associated segment {segment_id} not found."}}
        )
        return None, f"Associated segment {segment_id} not found. Segment may have been deleted."
    
    return segment, None

campaigns_bp = Blueprint("campaigns", __name__)

def call_fake_channel(comm):
    """Makes a POST request to the fake channel service."""
    try:
        fake_channel_url = os.getenv("FAKE_CHANNEL_URL", "http://localhost:5001/send-message")
        callback_url = os.getenv("CRM_CALLBACK_URL", "http://localhost:5000/api/receipts")
        
        payload = {
            "communication_id": comm["_id"],
            "campaign_id": comm["campaign_id"],
            "customer_id": comm["customer_id"],
            "recipient": comm["recipient"],
            "channel": comm["channel"],
            "message": comm["message"],
            "callback_url": callback_url
        }
        
        # Send post request to fake channel
        res = requests.post(fake_channel_url, json=payload, timeout=5)
        if res.status_code != 200:
            print(f"Fake channel service returned code {res.status_code} for communication {comm['_id']}")
    except Exception as e:
        print(f"Failed to deliver communication {comm['_id']} to fake channel: {e}")

def process_campaign_sending_async(campaign_id, channel, message_template, customers):
    """Background worker that creates communication records and invokes fake channel service."""
    comms = []
    
    # 1. Create communication records
    for customer in customers:
        comm_id = f"comm_{uuid.uuid4().hex[:12]}"
        
        # Determine recipient based on channel
        recipient = customer.get("email") if channel == "email" else customer.get("phone")
        
        # Personalize message template
        personalized_message = message_template.replace("{{name}}", customer.get("name", "there"))
        
        comm = {
            "_id": comm_id,
            "campaign_id": campaign_id,
            "customer_id": customer["_id"],
            "recipient": recipient,
            "channel": channel,
            "message": personalized_message,
            "status": "sent",
            "events": ["sent"],
            "created_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        }
        comms.append(comm)
        
    if comms:
        # Insert all communications in bulk
        communications_col.insert_many(comms)
        
        # 2. Call fake channel service for each communication
        for comm in comms:
            call_fake_channel(comm)

    try:
        log_activity(
            event_type="campaign_dispatch_completed",
            entity_type="campaign",
            resource_id=campaign_id,
            metadata={
                "channel": channel,
                "communications_created": len(comms)
            },
            source="system"
        )
    except Exception as audit_error:
        print(f"Warning: failed to persist campaign dispatch log for {campaign_id}: {audit_error}")
            
    # Update campaign status to sent after completion
    campaigns_col.update_one(
        {"_id": campaign_id},
        {"$set": {"status": "sent"}}
    )
    print(f"Finished processing and sending campaign {campaign_id}")

@campaigns_bp.route("", methods=["POST"])
def create_campaign():
    try:
        data = request.json or {}
        name = data.get("name")
        segment_id = data.get("segment_id")
        channel = data.get("channel", "sms").lower()
        message = data.get("message")

        if not name or not segment_id or not message:
            return jsonify({
                "status": "error",
                "message": "Campaign name, segment, and message are required."
            }), 400

        # Verify segment exists
        segment = segments_col.find_one({"_id": segment_id})
        if not segment:
            return jsonify({
                "status": "error",
                "message": f"Segment with ID {segment_id} not found."
            }), 404

        campaign_id = f"camp_{uuid.uuid4().hex[:12]}"
        campaign_doc = {
            "_id": campaign_id,
            "name": name,
            "segment_id": segment_id,
            "segment_name": segment["name"],
            "channel": channel,
            "message": message,
            "status": "created",
            "created_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        }

        campaigns_col.insert_one(campaign_doc)

        try:
            log_activity(
                event_type="campaign_created",
                entity_type="campaign",
                resource_id=campaign_id,
                metadata={
                    "name": name,
                    "segment_id": segment_id,
                    "segment_name": segment["name"],
                    "channel": channel
                },
                source="request"
            )
        except Exception as audit_error:
            print(f"Warning: failed to persist campaign creation log for {campaign_id}: {audit_error}")

        return jsonify({
            "status": "success",
            "data": serialize_to_json(campaign_doc)
        }), 201
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@campaigns_bp.route("", methods=["GET"])
def get_campaigns():
    try:
        campaigns = list(campaigns_col.find().sort("created_at", -1))
        serialized_campaigns = [serialize_to_json(camp) for camp in campaigns]
        return jsonify({
            "status": "success",
            "data": serialized_campaigns
        }), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@campaigns_bp.route("/<string:campaign_id>/send", methods=["POST"])
def send_campaign(campaign_id):
    try:
        campaign = campaigns_col.find_one({"_id": campaign_id})
        if not campaign:
            return jsonify({
                "status": "error",
                "message": f"Campaign with ID {campaign_id} not found."
            }), 404

        if campaign["status"] == "sent":
            return jsonify({
                "status": "error",
                "message": "Campaign has already been sent."
            }), 400
        
        if campaign.get("status") == "failed":
            return jsonify({
                "status": "error",
                "message": f"Campaign is in failed state: {campaign.get('error', 'Unknown error')}"
            }), 400

        # Validate segment exists and handle if missing
        segment, error_msg = validate_campaign_segment(campaign_id)
        if not segment:
            return jsonify({
                "status": "error",
                "message": error_msg
            }), 404

        # Handle both rule-based and pre-created segments
        if "customer_ids" in segment and segment["customer_ids"]:
            # Pre-created segments with direct customer IDs
            customers = list(customers_col.find({"_id": {"$in": segment["customer_ids"]}}))
        else:
            # Rule-based segments - compile rules and query
            mongo_query = compile_segment_rules(segment.get("rules", {}))
            customers = list(customers_col.find(mongo_query))

        if not customers:
            return jsonify({
                "status": "error",
                "message": "The target segment contains 0 customers. Cannot send campaign."
            }), 400

        # Update status to sending
        campaigns_col.update_one(
            {"_id": campaign_id},
            {"$set": {"status": "sending"}}
        )

        try:
            log_activity(
                event_type="campaign_send_started",
                entity_type="campaign",
                resource_id=campaign_id,
                metadata={
                    "channel": campaign["channel"],
                    "segment_id": campaign["segment_id"],
                    "target_customers": len(customers)
                },
                source="request"
            )
        except Exception as audit_error:
            print(f"Warning: failed to persist campaign send log for {campaign_id}: {audit_error}")

        # Trigger asynchronous thread to handle sending
        thread = threading.Thread(
            target=process_campaign_sending_async,
            args=(campaign_id, campaign["channel"], campaign["message"], customers)
        )
        thread.start()

        return jsonify({
            "status": "success",
            "message": f"Campaign sending initiated asynchronously for {len(customers)} customers."
        }), 200
    except Exception as e:
        print(f"Error sending campaign {campaign_id}: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@campaigns_bp.route("/<string:campaign_id>/stats", methods=["GET"])
def get_campaign_stats(campaign_id):
    try:
        campaign = campaigns_col.find_one({"_id": campaign_id})
        if not campaign:
            return jsonify({
                "status": "error",
                "message": f"Campaign with ID {campaign_id} not found."
            }), 404

        # Query communications status breakdown
        pipeline = [
            {"$match": {"campaign_id": campaign_id}},
            {"$group": {
                "_id": "$status",
                "count": {"$sum": 1}
            }}
        ]
        results = list(communications_col.aggregate(pipeline))
        
        # Build status counts dictionary
        stats = {
            "sent": 0,
            "delivered": 0,
            "failed": 0,
            "opened": 0,
            "clicked": 0,
            "converted": 0
        }
        
        for item in results:
            status = item["_id"]
            if status in stats:
                stats[status] = item["count"]

        # Calculate helper funnel aggregates (e.g. opened count should include clicked and converted, etc.)
        # Funnel order: sent -> delivered -> opened -> clicked -> converted
        # If a message is clicked, it was opened and delivered.
        # If a message is converted, it was clicked, opened, and delivered.
        # This keeps the funnel logic intuitive for analytics charts.
        
        delivered_total = stats["delivered"] + stats["opened"] + stats["clicked"] + stats["converted"]
        opened_total = stats["opened"] + stats["clicked"] + stats["converted"]
        clicked_total = stats["clicked"] + stats["converted"]
        converted_total = stats["converted"]
        failed_total = stats["failed"]
        sent_total = stats["sent"] + delivered_total + failed_total

        delivered_rate = round((delivered_total / sent_total) * 100, 1) if sent_total else 0
        open_rate = round((opened_total / delivered_total) * 100, 1) if delivered_total else 0
        click_rate = round((clicked_total / opened_total) * 100, 1) if opened_total else 0
        conversion_rate = round((converted_total / clicked_total) * 100, 1) if clicked_total else 0

        attributed_orders = orders_col.count_documents({"campaign_id": campaign_id})
        attributed_revenue_pipeline = [
            {"$match": {"campaign_id": campaign_id}},
            {"$group": {"_id": None, "revenue": {"$sum": "$amount"}}}
        ]
        attributed_revenue_stats = list(orders_col.aggregate(attributed_revenue_pipeline))
        attributed_revenue = attributed_revenue_stats[0]["revenue"] if attributed_revenue_stats else 0
        attributed_aov = round(attributed_revenue / attributed_orders, 2) if attributed_orders > 0 else 0

        # Query recent 50 communications with customer names
        comm_details = list(communications_col.aggregate([
            {"$match": {"campaign_id": campaign_id}},
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
                "customer_name": {"$ifNull": ["$customer_info.name", "Unknown"]},
                "recipient": 1,
                "channel": 1,
                "message": 1,
                "status": 1,
                "events": 1,
                "created_at": 1
            }},
            {"$sort": {"created_at": -1}},
            {"$limit": 50}
        ]))

        return jsonify({
            "status": "success",
            "campaign_name": campaign["name"],
            "channel": campaign["channel"],
            "audience_size": sent_total,
            "raw_stats": stats,
            "rates": {
                "delivery_rate": delivered_rate,
                "open_rate": open_rate,
                "click_rate": click_rate,
                "conversion_rate": conversion_rate,
            },
            "attribution": {
                "orders": attributed_orders,
                "revenue": attributed_revenue,
                "average_order_value": attributed_aov
            },
            "funnel": {
                "sent": sent_total,
                "delivered": delivered_total,
                "failed": failed_total,
                "opened": opened_total,
                "clicked": clicked_total,
                "converted": converted_total
            },
            "recent_communications": comm_details
        }), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500
