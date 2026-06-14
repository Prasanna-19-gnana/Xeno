"""
Fix campaigns to use correct segment IDs
Updates all campaign segment references to match existing segments
"""
from models import campaigns_col, segments_col

def fix_campaign_segments():
    """Update campaigns to reference correct segments"""
    print("🔧 Fixing campaign segment references...")
    
    # Get all campaigns
    campaigns = list(campaigns_col.find())
    
    # Get all segments with their names and IDs
    segments = list(segments_col.find({}, {"_id": 1, "name": 1}))
    segment_map = {seg["name"]: seg["_id"] for seg in segments}
    
    print(f"Found {len(campaigns)} campaigns and {len(segments)} segments")
    print("Segment mapping:")
    for name, seg_id in sorted(segment_map.items()):
        print(f"  • {name} -> {seg_id}")
    
    # Update campaigns based on their names
    fixes = {
        # VIP campaigns
        "VIP Early Access - New Arrivals": "seg_vip_shoppers",
        "VIP Exclusive Membership": "seg_vip_shoppers",
        
        # Male customers campaigns  
        "TrendWear Valentine's Day Guide for Men": "seg_male_buyers",
        
        # Inactive/win-back
        "Win-back Inactive Shoppers": "seg_inactive",
        "Inactive Shoppers - 30 Days": "seg_inactive",
        "Reactivate Dormant Customers": "seg_inactive",
        
        # High spend
        "Flash Sale - Limited Stock": "seg_high_spend",
        "Summer Sneakers Launch": "seg_high_spend",
        
        # New customers
        "Welcome New Customers": "seg_new",
        "First Purchase Offer": "seg_new",
        
        # Regular/general
        "summer sale": "seg_regular",
        "TrendWear Sizzling Summer Sale": "seg_regular",
        "Abandoned Cart Reminder - Week 1": "seg_regular",
    }
    
    updated_count = 0
    for campaign in campaigns:
        campaign_name = campaign.get("name", "")
        
        # Try exact match first
        if campaign_name in fixes:
            new_segment_id = fixes[campaign_name]
            campaigns_col.update_one(
                {"_id": campaign["_id"]},
                {"$set": {"segment_id": new_segment_id}}
            )
            updated_count += 1
            print(f"✅ Updated '{campaign_name}' -> {new_segment_id}")
        else:
            # Try to find a segment based on campaign name keywords
            campaign_lower = campaign_name.lower()
            assigned = False
            
            if any(word in campaign_lower for word in ["vip", "exclusive", "premium"]):
                campaigns_col.update_one(
                    {"_id": campaign["_id"]},
                    {"$set": {"segment_id": "seg_vip_shoppers"}}
                )
                assigned = True
                print(f"⚠️  Assigned '{campaign_name}' -> seg_vip_shoppers (keyword match)")
            elif any(word in campaign_lower for word in ["male", "men", "guy", "man"]):
                campaigns_col.update_one(
                    {"_id": campaign["_id"]},
                    {"$set": {"segment_id": "seg_male_buyers"}}
                )
                assigned = True
                print(f"⚠️  Assigned '{campaign_name}' -> seg_male_buyers (keyword match)")
            elif any(word in campaign_lower for word in ["inactive", "win-back", "reactivate", "dormant"]):
                campaigns_col.update_one(
                    {"_id": campaign["_id"]},
                    {"$set": {"segment_id": "seg_inactive"}}
                )
                assigned = True
                print(f"⚠️  Assigned '{campaign_name}' -> seg_inactive (keyword match)")
            elif any(word in campaign_lower for word in ["new customer", "welcome", "first purchase"]):
                campaigns_col.update_one(
                    {"_id": campaign["_id"]},
                    {"$set": {"segment_id": "seg_new"}}
                )
                assigned = True
                print(f"⚠️  Assigned '{campaign_name}' -> seg_new (keyword match)")
            elif any(word in campaign_lower for word in ["high spend", "flash sale", "premium", "exclusive"]):
                campaigns_col.update_one(
                    {"_id": campaign["_id"]},
                    {"$set": {"segment_id": "seg_high_spend"}}
                )
                assigned = True
                print(f"⚠️  Assigned '{campaign_name}' -> seg_high_spend (keyword match)")
            else:
                # Default to regular customers
                campaigns_col.update_one(
                    {"_id": campaign["_id"]},
                    {"$set": {"segment_id": "seg_regular"}}
                )
                assigned = True
                print(f"⚠️  Assigned '{campaign_name}' -> seg_regular (default)")
            
            if assigned:
                updated_count += 1
    
    print(f"\n✅ Fixed {updated_count} campaigns!")
    return updated_count

if __name__ == "__main__":
    fix_campaign_segments()
