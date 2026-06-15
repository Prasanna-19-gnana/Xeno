import os
import csv
import uuid
import random
from datetime import datetime, timedelta
from models import customers_col, orders_col, segments_col, campaigns_col, communications_col, init_db

def seed_database():
    print("Clearing existing data...")
    customers_col.delete_many({})
    orders_col.delete_many({})
    segments_col.delete_many({})
    campaigns_col.delete_many({})
    communications_col.delete_many({})

    print("Re-initializing indexes...")
    init_db()

    csv_path = os.path.join(os.path.dirname(__file__), "..", "shopping_trends (1).csv")
    if not os.path.exists(csv_path):
        print(f"Error: Dataset not found at {csv_path}")
        return 0, 0

    print("Parsing dataset...")
    customers = []
    orders = []
    
    # We will track customer stats to append to customer profile
    customer_stats = {}
    today = datetime.utcnow()
    
    with open(csv_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # CSV rows represent orders/transactions linked to a customer
            # Headers: Customer ID,Age,Gender,Item Purchased,Category,Purchase Amount (USD),Location,Size,Color,Season,Review Rating,Subscription Status,Payment Method,Shipping Type,Discount Applied,Promo Code Used,Previous Purchases,Preferred Payment Method,Frequency of Purchases
            
            raw_cid = row.get("Customer ID")
            cust_id = f"cust_{raw_cid}"
            
            # Since the CSV might have multiple rows for one customer, we create the customer once
            if cust_id not in customer_stats:
                # Create base customer
                customers.append({
                    "_id": cust_id,
                    "name": f"Customer {raw_cid}",
                    "email": f"customer.{raw_cid}@example.com",
                    "phone": f"9{''.join([str(random.randint(0, 9)) for _ in range(9)])}",
                    "city": row.get("Location", "Unknown"),
                    "gender": row.get("Gender", "Unknown"),
                    "age": int(row.get("Age", 0)),
                    "subscription_status": row.get("Subscription Status", "No"),
                    "frequency_of_purchases": row.get("Frequency of Purchases", "Unknown"),
                    "preferred_payment_method": row.get("Preferred Payment Method", "Unknown"),
                    "total_spend": 0,
                    "total_orders": 0,
                    "last_order_date": ""
                })
                customer_stats[cust_id] = {"spend": 0, "orders_count": 0, "dates": []}
            
            # Create the order
            amount = float(row.get("Purchase Amount (USD)", 0))
            
            # Assign a random date in the last year
            days_ago = random.randint(0, 365)
            order_date = (today - timedelta(days=days_ago)).strftime("%Y-%m-%d")
            
            order = {
                "_id": f"ord_{uuid.uuid4().hex[:12]}",
                "customer_id": cust_id,
                "amount": amount,
                "item_purchased": row.get("Item Purchased", "Unknown"),
                "category": row.get("Category", "Unknown"),
                "size": row.get("Size", "Unknown"),
                "color": row.get("Color", "Unknown"),
                "season": row.get("Season", "Unknown"),
                "review_rating": float(row.get("Review Rating", 0)),
                "shipping_type": row.get("Shipping Type", "Unknown"),
                "discount_applied": row.get("Discount Applied", "No"),
                "promo_code_used": row.get("Promo Code Used", "No"),
                "order_date": order_date
            }
            orders.append(order)
            
            customer_stats[cust_id]["spend"] += amount
            customer_stats[cust_id]["orders_count"] += 1
            customer_stats[cust_id]["dates"].append(order_date)

    # Update aggregated stats on customers
    for customer in customers:
        cid = customer["_id"]
        stats = customer_stats[cid]
        customer["total_spend"] = stats["spend"]
        customer["total_orders"] = stats["orders_count"]
        if stats["dates"]:
            customer["last_order_date"] = max(stats["dates"])

    print("Inserting data into database...")
    if customers:
        customers_col.insert_many(customers)
    if orders:
        orders_col.insert_many(orders)
    
    print(f"Database seeded successfully with {len(customers)} customers and {len(orders)} orders.")
    return len(customers), len(orders)

if __name__ == "__main__":
    seed_database()
