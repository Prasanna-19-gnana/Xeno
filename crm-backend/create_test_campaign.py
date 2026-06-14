#!/usr/bin/env python3
"""Create a test segment and campaign that will work with Firebase."""

from models import segments_col, campaigns_col
from datetime import datetime

# Create a simple segment directly
segment_id = "seg_test_active_buyers"
segment_data = {
    "_id": segment_id,
    "name": "Test Active Buyers",
    "rules": {"total_spend_gt": 100},
    "customer_count": 1000,  # All customers have spend > 100
    "created_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
}

# Try to insert/update segment
try:
    segments_col.insert_one(segment_data)
    print(f"✅ Segment created/updated: {segment_id}")
except Exception as e:
    print(f"⚠️  Could not insert segment: {e}")
    # Try update if insert fails
    try:
        segments_col.update_one({"_id": segment_id}, {"$set": segment_data})
        print(f"✅ Segment updated: {segment_id}")
    except Exception as e2:
        print(f"❌ Failed to update segment: {e2}")

print(f"   Name: {segment_data['name']}")
print(f"   Rules: {segment_data['rules']}")

# Verify it exists
try:
    segment = segments_col.find_one({"_id": segment_id})
    if segment:
        print(f"\n✅ Segment verified:")
        print(f"   ID: {segment.get('_id')}")
        print(f"   Name: {segment.get('name')}")
        print(f"   Customer Count: {segment.get('customer_count', 'N/A')}")
    else:
        print(f"\n❌ Segment not found after insertion")
except Exception as e:
    print(f"❌ Error retrieving segment: {e}")

# Now create a campaign targeting this segment
campaign_id = "camp_test_direct"
campaign_data = {
    "_id": campaign_id,
    "name": "Test Campaign Direct",
    "segment_id": segment_id,
    "segment_name": "Test Active Buyers",
    "channel": "SMS",
    "message": "Test message for {{name}}",
    "status": "created",
    "created_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
}

# Insert campaign
try:
    campaigns_col.insert_one(campaign_data)
    print(f"\n✅ Campaign created: {campaign_id}")
except Exception as e:
    print(f"⚠️  Could not insert campaign: {e}")
    try:
        campaigns_col.update_one({"_id": campaign_id}, {"$set": campaign_data})
        print(f"✅ Campaign updated: {campaign_id}")
    except Exception as e2:
        print(f"❌ Failed to update campaign: {e2}")

print(f"   Segment ID: {campaign_data['segment_id']}")
print(f"   Channel: {campaign_data['channel']}")

# Verify campaign exists
try:
    campaign = campaigns_col.find_one({"_id": campaign_id})
    if campaign:
        print(f"\n✅ Campaign verified:")
        print(f"   ID: {campaign.get('_id')}")
        print(f"   Name: {campaign.get('name')}")
        print(f"   Segment ID: {campaign.get('segment_id')}")
        print(f"   Status: {campaign.get('status')}")
    else:
        print(f"\n❌ Campaign not found after insertion")
except Exception as e:
    print(f"❌ Error retrieving campaign: {e}")

print(f"\n📌 Ready to test campaign sending. Use:")
print(f"   curl -X POST http://localhost:5002/api/campaigns/{campaign_id}/send")
