"""
Create campaign-specific segments from customer data
Maps customers to segments for campaign targeting
"""
from models import customers_col, segments_col, orders_col, campaigns_col, communications_col
from datetime import datetime, timedelta

def create_campaign_segments():
    """Create segments for campaign targeting"""
    print("📊 Creating campaign-specific segments...")
    
    # Clear existing segments and related campaigns/communications
    segments_col.delete_many({})
    campaigns_col.delete_many({})  # Clear old campaigns that reference old segments
    communications_col.delete_many({})  # Clear communications from old campaigns
    
    base_date = datetime.utcnow()
    segments_created = {}
    
    # Helper function to get customers who bought a specific category
    def get_customers_by_category(category):
        """Get list of customers who have purchased a specific product category"""
        customer_ids = orders_col.distinct("customer_id", {"category": category})
        return list(customers_col.find({"_id": {"$in": customer_ids}})) if customer_ids else []
    
    # 2. Female Customers - Past Buyers (NEW)
    female_buyers = list(customers_col.find({
        "gender": "Female",
        "total_orders": {"$gte": 1}
    }))
    
    if female_buyers:
        female_segment = {
            "_id": "seg_female_buyers",
            "name": "Female Customers - Past Buyers",
            "description": "Female customers with purchase history",
            "criteria": {
                "gender": "Female",
                "total_orders": {"$gte": 1}
            },
            "customer_count": len(female_buyers),
            "customer_ids": [c["_id"] for c in female_buyers],
            "created_at": base_date.isoformat(),
            "updated_at": base_date.isoformat()
        }
        segments_col.insert_one(female_segment)
        segments_created["Female Buyers"] = len(female_buyers)
    
    # 2b. Male Customers - Past Buyers
    male_buyers = list(customers_col.find({
        "gender": "Male",
        "total_orders": {"$gte": 1}
    }))
    
    if male_buyers:
        male_segment = {
            "_id": "seg_male_buyers",
            "name": "Male Customers - Past Buyers",
            "description": "Male customers with purchase history",
            "criteria": {
                "gender": "Male",
                "total_orders": {"$gte": 1}
            },
            "customer_count": len(male_buyers),
            "customer_ids": [c["_id"] for c in male_buyers],
            "created_at": base_date.isoformat(),
            "updated_at": base_date.isoformat()
        }
        segments_col.insert_one(male_segment)
        segments_created["Male Buyers"] = len(male_buyers)
    
    # 3. High-Order Frequency Shoppers (NEW - customers with many orders)
    # Threshold: customers with total_orders >= 3 (frequent orderers)
    high_order_customers = list(customers_col.find({
        "total_orders": {"$gte": 3}
    }))
    
    if high_order_customers:
        high_order_segment = {
            "_id": "seg_high_frequency",
            "name": "High-Order Frequency Shoppers",
            "description": "Customers with 5 or more purchases (frequent orderers)",
            "criteria": {"total_orders": {"$gte": 5}},
            "customer_count": len(high_order_customers),
            "customer_ids": [c["_id"] for c in high_order_customers],
            "created_at": base_date.isoformat(),
            "updated_at": base_date.isoformat()
        }
        segments_col.insert_one(high_order_segment)
        segments_created["High-Order Frequency"] = len(high_order_customers)
    
    # 4. T-Shirt Buyers (NEW - product category based)
    tshirt_buyers = get_customers_by_category("T-Shirts")
    
    if tshirt_buyers:
        tshirt_segment = {
            "_id": "seg_tshirt_buyers",
            "name": "T-Shirt Buyers",
            "description": "Customers who have previously purchased T-Shirts",
            "criteria": {"category_bought": "T-Shirts"},
            "customer_count": len(tshirt_buyers),
            "customer_ids": [c["_id"] for c in tshirt_buyers],
            "created_at": base_date.isoformat(),
            "updated_at": base_date.isoformat()
        }
        segments_col.insert_one(tshirt_segment)
        segments_created["T-Shirt Buyers"] = len(tshirt_buyers)
    
    # 5. Jeans Buyers (NEW - product category based)
    jeans_buyers = get_customers_by_category("Jeans")
    
    if jeans_buyers:
        jeans_segment = {
            "_id": "seg_jeans_buyers",
            "name": "Jeans Buyers",
            "description": "Customers who have previously purchased Jeans",
            "criteria": {"category_bought": "Jeans"},
            "customer_count": len(jeans_buyers),
            "customer_ids": [c["_id"] for c in jeans_buyers],
            "created_at": base_date.isoformat(),
            "updated_at": base_date.isoformat()
        }
        segments_col.insert_one(jeans_segment)
        segments_created["Jeans Buyers"] = len(jeans_buyers)
    
    # 6. Shoes Buyers (NEW - product category based)
    shoes_buyers = get_customers_by_category("Shoes")
    
    if shoes_buyers:
        shoes_segment = {
            "_id": "seg_shoes_buyers",
            "name": "Shoes Buyers",
            "description": "Customers who have previously purchased Shoes",
            "criteria": {"category_bought": "Shoes"},
            "customer_count": len(shoes_buyers),
            "customer_ids": [c["_id"] for c in shoes_buyers],
            "created_at": base_date.isoformat(),
            "updated_at": base_date.isoformat()
        }
        segments_col.insert_one(shoes_segment)
        segments_created["Shoes Buyers"] = len(shoes_buyers)
    
    # 7. Dresses Buyers (NEW - product category based)
    dresses_buyers = get_customers_by_category("Dresses")
    
    if dresses_buyers:
        dresses_segment = {
            "_id": "seg_dresses_buyers",
            "name": "Dresses Buyers",
            "description": "Customers who have previously purchased Dresses",
            "criteria": {"category_bought": "Dresses"},
            "customer_count": len(dresses_buyers),
            "customer_ids": [c["_id"] for c in dresses_buyers],
            "created_at": base_date.isoformat(),
            "updated_at": base_date.isoformat()
        }
        segments_col.insert_one(dresses_segment)
        segments_created["Dresses Buyers"] = len(dresses_buyers)
    
    # 8. Accessories Buyers (NEW - product category based)
    accessories_buyers = get_customers_by_category("Accessories")
    
    if accessories_buyers:
        accessories_segment = {
            "_id": "seg_accessories_buyers",
            "name": "Accessories Buyers",
            "description": "Customers who have previously purchased Accessories",
            "criteria": {"category_bought": "Accessories"},
            "customer_count": len(accessories_buyers),
            "customer_ids": [c["_id"] for c in accessories_buyers],
            "created_at": base_date.isoformat(),
            "updated_at": base_date.isoformat()
        }
        segments_col.insert_one(accessories_segment)
        segments_created["Accessories Buyers"] = len(accessories_buyers)
    
    # 9. High-Frequency VIP Shoppers
    # Criteria: High-Value segment + frequent purchases + subscription
    vip_customers = list(customers_col.find({
        "segment": "High-Value Customers",
        "subscription_status": "Yes",
        "review_rating": {"$gte": 4.0}
    }))
    
    if vip_customers:
        vip_segment = {
            "_id": "seg_vip_shoppers",
            "name": "High-Frequency VIP Shoppers",
            "description": "High-value customers with frequent purchases and premium subscription",
            "criteria": {
                "segment": "High-Value Customers",
                "subscription_status": "Yes",
                "review_rating": {"$gte": 4.0}
            },
            "customer_count": len(vip_customers),
            "customer_ids": [c["_id"] for c in vip_customers],
            "created_at": base_date.isoformat(),
            "updated_at": base_date.isoformat()
        }
        segments_col.insert_one(vip_segment)
        segments_created["VIP Shoppers"] = len(vip_customers)
    
    # 10. At-Risk Customers
    at_risk = list(customers_col.find({"segment": "At-Risk Customers"}))
    
    if at_risk:
        at_risk_segment = {
            "_id": "seg_at_risk",
            "name": "At-Risk Customers",
            "description": "Customers showing signs of churn (low recent activity)",
            "criteria": {"segment": "At-Risk Customers"},
            "customer_count": len(at_risk),
            "customer_ids": [c["_id"] for c in at_risk],
            "created_at": base_date.isoformat(),
            "updated_at": base_date.isoformat()
        }
        segments_col.insert_one(at_risk_segment)
        segments_created["At-Risk"] = len(at_risk)
    
    # 11. High-Spend Customers
    high_spend = list(customers_col.find({"total_spend": {"$gte": 80}}))
    
    if high_spend:
        high_spend_segment = {
            "_id": "seg_high_spend",
            "name": "High-Spend Customers",
            "description": "Customers with total spending of $80 or more",
            "criteria": {"total_spend": {"$gte": 80}},
            "customer_count": len(high_spend),
            "customer_ids": [c["_id"] for c in high_spend],
            "created_at": base_date.isoformat(),
            "updated_at": base_date.isoformat()
        }
        segments_col.insert_one(high_spend_segment)
        segments_created["High-Spend"] = len(high_spend)
    
    # 12. New Customers
    new_customers = list(customers_col.find({"segment": "New Customers"}))
    
    if new_customers:
        new_segment = {
            "_id": "seg_new",
            "name": "New Customers",
            "description": "Recently acquired customers with limited purchase history",
            "criteria": {"segment": "New Customers"},
            "customer_count": len(new_customers),
            "customer_ids": [c["_id"] for c in new_customers],
            "created_at": base_date.isoformat(),
            "updated_at": base_date.isoformat()
        }
        segments_col.insert_one(new_segment)
        segments_created["New Customers"] = len(new_customers)
    
    # 13. Regular Customers
    regular = list(customers_col.find({"segment": "Regular Customers"}))
    
    if regular:
        regular_segment = {
            "_id": "seg_regular",
            "name": "Regular Customers",
            "description": "Consistent customers with moderate activity",
            "criteria": {"segment": "Regular Customers"},
            "customer_count": len(regular),
            "customer_ids": [c["_id"] for c in regular],
            "created_at": base_date.isoformat(),
            "updated_at": base_date.isoformat()
        }
        segments_col.insert_one(regular_segment)
        segments_created["Regular"] = len(regular)
    
    # 14. Inactive Customers (no order in 90+ days)
    cutoff_date = (base_date - timedelta(days=90)).strftime("%Y-%m-%d")
    inactive = list(customers_col.find({
        "$or": [
            {"last_order_date": {"$lt": cutoff_date}},
            {"last_order_date": ""}
        ]
    }))
    
    if inactive:
        inactive_segment = {
            "_id": "seg_inactive",
            "name": "Inactive Customers",
            "description": "Customers with no purchases in last 90 days",
            "criteria": {
                "$or": [
                    {"last_order_date": {"$lt": cutoff_date}},
                    {"last_order_date": ""}
                ]
            },
            "customer_count": len(inactive),
            "customer_ids": [c["_id"] for c in inactive],
            "created_at": base_date.isoformat(),
            "updated_at": base_date.isoformat()
        }
        segments_col.insert_one(inactive_segment)
        segments_created["Inactive"] = len(inactive)
    
    print("✅ Campaign segments created successfully!")
    for seg_name, count in segments_created.items():
        print(f"   • {seg_name}: {count} customers")
    
    return segments_created

if __name__ == "__main__":
    create_campaign_segments()
