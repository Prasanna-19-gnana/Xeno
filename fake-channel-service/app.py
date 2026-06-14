import os
import time
import random
import threading
import requests
from flask import Flask, request, jsonify
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

def post_callback(callback_url, comm_id, campaign_id, customer_id, status):
    """Sends a receipt status update back to the CRM backend."""
    try:
        payload = {
            "communication_id": comm_id,
            "campaign_id": campaign_id,
            "customer_id": customer_id,
            "status": status
        }
        headers = {"Content-Type": "application/json"}
        # Send callback
        res = requests.post(callback_url, json=payload, headers=headers, timeout=5)
        print(f"Callback status '{status}' for {comm_id}: Response Code {res.status_code}")
        return res.status_code == 200
    except Exception as e:
        print(f"Error posting callback '{status}' for {comm_id}: {e}")
        return False

def simulate_delivery_lifecycle(callback_url, comm_id, campaign_id, customer_id):
    """Simulates the message status progression with randomized delays."""
    
    # 1. Delivery Phase (wait 1 second)
    time.sleep(1.0)
    
    # 8% failure rate, 92% delivery rate
    is_failed = random.random() < 0.08
    status = "failed" if is_failed else "delivered"
    
    success = post_callback(callback_url, comm_id, campaign_id, customer_id, status)
    if is_failed or not success:
        return # Stop if delivery failed

    # 2. Open Phase (wait 2 seconds)
    time.sleep(2.0)
    
    # 70% open rate
    is_opened = random.random() < 0.70
    if is_opened:
        success = post_callback(callback_url, comm_id, campaign_id, customer_id, "opened")
        if not success:
            return
            
        # 3. Click Phase (wait another 2 seconds)
        time.sleep(2.0)
        
        # 40% click rate
        is_clicked = random.random() < 0.40
        if is_clicked:
            post_callback(callback_url, comm_id, campaign_id, customer_id, "clicked")

@app.route("/send-message", methods=["POST"])
def send_message():
    try:
        data = request.json or {}
        comm_id = data.get("communication_id")
        campaign_id = data.get("campaign_id")
        customer_id = data.get("customer_id")
        recipient = data.get("recipient")
        channel = data.get("channel")
        message = data.get("message")
        
        # Determine callback URL: payload callback_url has priority, then environment, then fallback
        callback_url = data.get("callback_url") or os.getenv("CRM_CALLBACK_URL") or "http://localhost:5000/api/receipts"

        if not comm_id or not recipient or not channel or not message:
            return jsonify({
                "status": "error",
                "message": "Missing required parameters (communication_id, recipient, channel, message)"
            }), 400

        print(f"Fake Channel: Received request for {channel} to {recipient} (Comm ID: {comm_id})")

        # Start asynchronous lifecycle thread
        thread = threading.Thread(
            target=simulate_delivery_lifecycle,
            args=(callback_url, comm_id, campaign_id, customer_id)
        )
        thread.start()

        return jsonify({
            "status": "success",
            "message": "Message successfully queued for sending.",
            "communication_id": comm_id
        }), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "healthy",
        "service": "TrendWear Fake Channel Service"
    }), 200

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5001))
    print(f"Starting Fake Channel Service on port {port}...")
    app.run(host="0.0.0.0", port=port, debug=False)
