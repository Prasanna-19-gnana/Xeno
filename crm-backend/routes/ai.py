import os
import json
import requests
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify
from models import customers_col, orders_col, segments_col, serialize_to_json

ai_bp = Blueprint("ai", __name__)

gemini_api_key = os.getenv("GEMINI_API_KEY")
groq_api_key = os.getenv("GROQ_API_KEY")

print("\n📋 AI Configuration - Three-Tier System:")
print(f"  Tier 1 - Gemini: {'✅ Configured' if gemini_api_key else '❌ Not set'}")
print(f"  Tier 2 - Groq: {'✅ Configured' if groq_api_key else '❌ Not set'}")
print("  Tier 3 - Template Fallback: ✅ Always available\n")


def _normalize_prompt(prompt, system_instruction=None):
    if system_instruction:
        return f"{system_instruction}\n\n{prompt}"
    return prompt


def _extract_text(response):
    if not response:
        return None
    if isinstance(response, str):
        return response.strip()
    if isinstance(response, dict):
        return response.get("text") or response.get("content")
    return getattr(response, "text", None)


def call_gemini(prompt, system_instruction=None):
    """Try Gemini first."""
    if not gemini_api_key:
        return None

    try:
        combined_prompt = _normalize_prompt(prompt, system_instruction)
        preferred_models = [
            "gemini-flash-latest",
            "gemini-2.5-flash",
            "gemini-1.5-flash",
            "gemini-pro",
        ]

        for model_name in preferred_models:
            try:
                print(f"🤖 [Gemini REST] Attempting model: {model_name}")
                response = requests.post(
                    f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent",
                    headers={
                        "Content-Type": "application/json",
                        "X-goog-api-key": gemini_api_key,
                    },
                    json={
                        "contents": [
                            {
                                "parts": [
                                    {
                                        "text": combined_prompt,
                                    }
                                ]
                            }
                        ]
                    },
                    timeout=30,
                )

                if response.status_code == 200:
                    payload = response.json()
                    candidates = payload.get("candidates", [])
                    if candidates:
                        content = candidates[0].get("content", {})
                        parts = content.get("parts", [])
                        text = "".join(part.get("text", "") for part in parts if isinstance(part, dict))
                        if text.strip():
                            print(f"✅ [Gemini REST] Success with {model_name}")
                            return text.strip()
                else:
                    print(f"⚠️  [Gemini REST] {model_name} returned {response.status_code}")
            except Exception as e:
                print(f"⚠️  [Gemini REST] {model_name} failed: {e}")
                continue

        return None
    except Exception as e:
        print(f"❌ [Gemini REST] Error: {e}")
        return None


def call_groq(prompt, system_instruction=None):
    """Try Groq second using the OpenAI-compatible API."""
    if not groq_api_key:
        return None

    try:
        combined_message = _normalize_prompt(prompt, system_instruction)
        print("🤖 [Groq] Attempting API call...")

        candidate_models = [
            "llama-3.1-70b-versatile",
            "llama-3.1-8b-instant",
            "mixtral-8x7b-32768",
        ]

        for model_name in candidate_models:
            try:
                response = requests.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {groq_api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": model_name,
                        "messages": [{"role": "user", "content": combined_message}],
                        "temperature": 0.7,
                        "max_tokens": 1024,
                    },
                    timeout=30,
                )

                if response.status_code == 200:
                    payload = response.json()
                    text = payload.get("choices", [{}])[0].get("message", {}).get("content")
                    if text:
                        print(f"✅ [Groq] Success with {model_name}")
                        return text.strip()
                else:
                    print(f"⚠️  [Groq] {model_name} returned {response.status_code}")
            except Exception as model_error:
                print(f"⚠️  [Groq] {model_name} failed: {model_error}")
                continue

        return None
    except Exception as e:
        print(f"❌ [Groq] Error: {e}")
        return None


def call_ai(prompt, system_instruction=None):
    """Gemini -> Groq -> template fallback."""
    print("\n🔄 Starting AI call (Gemini → Groq → Fallback)...")

    response = call_gemini(prompt, system_instruction)
    if response:
        return response

    response = call_groq(prompt, system_instruction)
    if response:
        return response

    print("ℹ️  All APIs failed, using template-based fallback")
    return None

# ==========================================
# 1. AI Message Generator
# ==========================================
@ai_bp.route("/generate-message", methods=["POST"])
def generate_message():
    try:
        data = request.json or {}
        segment_name = data.get("segment_name", "Valued Shoppers")
        channel = data.get("channel", "sms").lower()
        goal = data.get("goal", "Bring them back with 20% discount")
        brand = "TrendWear"

        system_instruction = (
            f"You are an expert copywriter for '{brand}', a high-end, trendy fashion brand. "
            "Your task is to write high-converting personalized messages for specific customer segments."
        )

        prompt = (
            f"Write a short, engaging campaign message for the segment: '{segment_name}'.\n"
            f"Channel: {channel.upper()}\n"
            f"Campaign Goal: {goal}\n\n"
            "Strict Guidelines:\n"
            "1. You MUST include the personalization placeholder '{{name}}' (case-sensitive) near the beginning.\n"
            "2. Keep the message concise:\n"
            "   - SMS/WhatsApp: Max 2 sentences. Use emoji naturally.\n"
            "   - Email: Start with 'Subject: [Subject Line]' on the first line, followed by the email body.\n"
            "   - RCS: Max 2-3 sentences, punchy call-to-action.\n"
            "3. Do not include markdown formatting, quotes, or conversational explanations. "
            "Return ONLY the direct message text."
        )

        message = call_ai(prompt, system_instruction)
        
        if not message:
            # Fallback mock copy
            print("Using mock fallback for message generation")
            if channel == "email":
                message = (
                    f"Subject: Exclusive TrendWear Offer Inside! ✨\n\n"
                    f"Hi {{{{name}}}},\n\n"
                    f"We miss your style at TrendWear! To help you refresh your wardrobe for the season, "
                    f"here is an exclusive 20% discount. Use code: COMEBACK20 at checkout.\n\n"
                    f"Shop now: https://trendwear.com/new"
                )
            elif channel == "whatsapp":
                message = f"Hi {{{{name}}}}, we miss your style! 🛍️ Grab an exclusive 20% off on TrendWear's new arrivals today. Use code COMEBACK20. Shop now: trendwear.com/new"
            else:  # sms / rcs
                message = f"Hi {{{{name}}}}, we miss you! Get 20% off on TrendWear's new collection. Use code COMEBACK20 at checkout today."

        return jsonify({
            "status": "success",
            "message": message.strip()
        }), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

# ==========================================
# 2. AI Segment Suggester
# ==========================================
@ai_bp.route("/suggest-segments", methods=["POST"])
def suggest_segments():
    try:
        # Collect customer stats to feed into prompt
        total_customers = customers_col.count_documents({})
        total_orders = orders_col.count_documents({})
        
        # Calculate Chennai shoppers
        chennai_count = customers_col.count_documents({"city": "Chennai"})
        
        # Calculate inactive count (older than 30 days from now)
        ref_date = datetime.utcnow()
        cutoff_30 = (ref_date - timedelta(days=30)).strftime("%Y-%m-%d")
        inactive_count = customers_col.count_documents({"last_order_date": {"$lt": cutoff_30, "$ne": ""}})
        
        # Spend breakdown
        high_spenders = customers_col.count_documents({"total_spend": {"$gt": 5000}})
        
        # Category purchased breakdown
        category_counts = {}
        for cat in ["T-Shirts", "Jeans", "Shoes", "Dresses", "Accessories"]:
            cust_ids = orders_col.distinct("customer_id", {"category": cat})
            category_counts[cat] = len(cust_ids)

        data_summary = {
            "total_customers": total_customers,
            "total_orders": total_orders,
            "inactive_30_days": inactive_count,
            "high_spenders_gt_5000": high_spenders,
            "chennai_shoppers": chennai_count,
            "category_purchasers": category_counts
        }

        system_instruction = (
            "You are an advanced CRM Data Scientist. You analyze customer metrics and "
            "suggest targeted marketing segments represented as JSON structures."
        )

        prompt = (
            f"Based on this customer database summary for the fashion brand TrendWear:\n"
            f"{json.dumps(data_summary, indent=2)}\n\n"
            "Suggest 3 highly targeted marketing segments to run campaigns for.\n"
            "Return a strictly valid JSON array of objects. Do not include markdown codeblocks or other text.\n"
            "Each object must contain:\n"
            "- 'name': Short segment name (e.g. 'High-Value Inactive Shoes Buyers')\n"
            "- 'description': Human description explaining why this segment was suggested\n"
            "- 'rules': A dict containing rule parameters. You can ONLY use the following keys in rules:\n"
            "    - 'total_spend_gt' (integer/float)\n"
            "    - 'total_orders_gte' (integer)\n"
            "    - 'city_eq' (string, e.g. 'Chennai')\n"
            "    - 'inactive_days_gt' (integer)\n"
            "    - 'category_bought' (string, e.g. 'Shoes', 'Jeans', 'Dresses', 'Accessories', 'T-Shirts')\n\n"
            "Example output JSON format:\n"
            "[\n"
            "  {\n"
            "    \"name\": \"Sneaker Lovers in Chennai\",\n"
            "    \"description\": \"Shoppers from Chennai who bought shoes and have high spending.\",\n"
            "    \"rules\": { \"city_eq\": \"Chennai\", \"category_bought\": \"Shoes\", \"total_spend_gt\": 3000 }\n"
            "  }\n"
            "]"
        )

        response_text = call_ai(prompt, system_instruction)
        suggestions = None

        if response_text:
            try:
                # Clean markdown wrapper if any
                clean_text = response_text.strip()
                if clean_text.startswith("```"):
                    # Find first [ and last ]
                    start_idx = clean_text.find("[")
                    end_idx = clean_text.rfind("]")
                    if start_idx != -1 and end_idx != -1:
                        clean_text = clean_text[start_idx:end_idx+1]
                suggestions = json.loads(clean_text)
            except Exception as e:
                print(f"Failed to parse Gemini segment suggestion JSON: {e}. Output was: {response_text}")

        if not suggestions:
            # Fallback suggestions
            print("Using mock fallback for segment suggestion")
            suggestions = [
                {
                    "name": "Inactive Premium Shoppers",
                    "description": "High-value customers (spent > ₹5,000) who haven't placed an order in the last 45 days. High priority for a win-back campaign.",
                    "rules": {"total_spend_gt": 5000, "inactive_days_gt": 45}
                },
                {
                    "name": "Chennai Footwear Fans",
                    "description": "Shoppers in Chennai who bought Shoes. Target them with localized summer footwear announcements.",
                    "rules": {"city_eq": "Chennai", "category_bought": "Shoes"}
                },
                {
                    "name": "Frequent Dress Buyers",
                    "description": "Customers who have bought Dresses and have placed at least 5 orders overall. Great for new collection previews.",
                    "rules": {"category_bought": "Dresses", "total_orders_gte": 5}
                }
            ]

        return jsonify({
            "status": "success",
            "data": suggestions
        }), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

# ==========================================
# 3. AI Campaign Assistant
# ==========================================
@ai_bp.route("/campaign-assistant", methods=["POST"])
def campaign_assistant():
    try:
        data = request.json or {}
        message = data.get("message", "")

        if not message:
            return jsonify({
                "status": "error",
                "message": "Message is required."
            }), 400

        system_instruction = (
            "You are an intelligent CRM marketing copilot named TrendBot for the fashion brand TrendWear.\n"
            "You assist marketers in strategizing and creating customer segments and campaign messages.\n"
            "You MUST return a JSON object with two fields:\n"
            "1. 'reply': A markdown-formatted string with your conversational response/advice.\n"
            "2. 'suggested_campaign': An optional dictionary. If the user wants to launch, suggest, or create a campaign, "
            "populate this dictionary with:\n"
            "   - 'name': proposed campaign name\n"
            "   - 'segment_name': proposed segment name\n"
            "   - 'channel': 'sms', 'whatsapp', 'email', or 'rcs'\n"
            "   - 'message': personalized copy containing '{{name}}'\n"
            "   - 'rules': segment rule parameters (using total_spend_gt, total_orders_gte, city_eq, inactive_days_gt, category_bought)\n"
            "If the message is generic greeting, do not populate 'suggested_campaign'."
        )

        prompt = (
            f"The marketer says: '{message}'\n\n"
            "Provide helpful marketing advice. If they express intent to run a campaign, target shoppers, "
            "boost sales, or create segments, recommend a campaign setup and fill the 'suggested_campaign' field. "
            "Ensure you return strict JSON conforming to the instructions."
        )

        response_text = call_ai(prompt, system_instruction)
        result = None

        if response_text:
            try:
                clean_text = response_text.strip()
                if clean_text.startswith("```"):
                    start_idx = clean_text.find("{")
                    end_idx = clean_text.rfind("}")
                    if start_idx != -1 and end_idx != -1:
                        clean_text = clean_text[start_idx:end_idx+1]
                result = json.loads(clean_text)
            except Exception as e:
                print(f"Failed to parse Gemini assistant JSON: {e}. Output was: {response_text}")

        if not result:
            # Smart Mock parsing based on user keywords
            print("Using mock fallback for assistant chat")
            msg_lower = message.lower()
            
            reply = ""
            suggested_campaign = None
            
            if "inactive" in msg_lower or "win back" in msg_lower or "comeback" in msg_lower:
                reply = (
                    "To target inactive shoppers, I recommend creating a **Win-Back Campaign** for customers who haven't "
                    "ordered in the last 45 days. Sending a WhatsApp message with a 20% comeback discount usually drives "
                    "the highest conversion rate for this segment.\n\n"
                    "I have generated a suggested campaign configuration for you below! You can review it and click 'Create' "
                    "to launch."
                )
                suggested_campaign = {
                    "name": "Win-back Inactive Shoppers",
                    "segment_name": "Inactive for 45 Days",
                    "channel": "whatsapp",
                    "message": "Hi {{name}}, we saved something special for you! ✨ Re-style your wardrobe with 20% off our new collections. Use code COMEBACK20. Shop now: trendwear.com",
                    "rules": {"inactive_days_gt": 45}
                }
            elif "shoe" in msg_lower or "sneaker" in msg_lower:
                reply = (
                    "Footwear campaigns convert exceptionally well when sent through SMS with a visual feel, or RCS! "
                    "I suggest targeting customers who bought **Shoes** previously, telling them about our new TrendWear Sneaker Drop.\n\n"
                    "Here is a recommended campaign setup:"
                )
                suggested_campaign = {
                    "name": "TrendWear Sneaker Drop",
                    "segment_name": "Previous Footwear Shoppers",
                    "channel": "sms",
                    "message": "Hey {{name}}! 👟 The wait is over. TrendWear's premium sneaker drop is live. Get early access now at trendwear.com/sneakers",
                    "rules": {"category_bought": "Shoes"}
                }
            elif "chennai" in msg_lower:
                reply = (
                    "Targeting Chennai-based shoppers allows us to run localized promotions. "
                    "Let's create a segment of all shoppers in **Chennai** and send them a summer wardrobe email."
                )
                suggested_campaign = {
                    "name": "Chennai Summer Breeze Preview",
                    "segment_name": "Chennai Shoppers",
                    "channel": "email",
                    "message": "Subject: Beat the heat, {{name}}! ☀️\n\nHi {{name}},\n\nDiscover TrendWear's brand new Summer Breeze collection, tailored for Chennai's tropical vibes. Exclusive preview access inside!\n\nShop now: trendwear.com/chennai-summer",
                    "rules": {"city_eq": "Chennai"}
                }
            else:
                reply = (
                    "Hello! I am **TrendBot**, your CRM assistant. I can help you target the right audience. "
                    "Try asking me things like:\n"
                    "- *'Create a campaign for inactive high-value shoppers.'*\n"
                    "- *'How can I target shoe buyers in Chennai?'*\n"
                    "- *'Suggest a campaign to boost sales for dresses.'*"
                )
                
            result = {
                "reply": reply,
                "suggested_campaign": suggested_campaign
            }

        return jsonify({
            "status": "success",
            "data": result
        }), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500
