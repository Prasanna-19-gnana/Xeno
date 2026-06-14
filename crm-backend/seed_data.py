import random
import uuid
from datetime import datetime, timedelta
from faker import Faker
from models import customers_col, orders_col, segments_col, campaigns_col, communications_col, init_db

fake = Faker("en_IN")  # Use Indian locale for localized names/cities

CITIES = ["Chennai", "Mumbai", "Bangalore", "Delhi", "Hyderabad", "Kolkata", "Pune", "Ahmedabad"]
CATEGORIES = ["T-Shirts", "Jeans", "Shoes", "Dresses", "Accessories"]
GENDERS = ["Male", "Female", "Non-binary"]

CATEGORY_PRICE_RANGES = {
    "T-Shirts": (399, 1499),
    "Jeans": (999, 3499),
    "Shoes": (1499, 5999),
    "Dresses": (899, 4599),
    "Accessories": (199, 1999)
}

def seed_database():
    print("Clearing existing data...")
    customers_col.delete_many({})
    orders_col.delete_many({})
    segments_col.delete_many({})
    campaigns_col.delete_many({})
    communications_col.delete_many({})

    print("Re-initializing indexes...")
    init_db()

    print("Generating 1000 customers...")
    customers = []
    customer_ids = []
    
    for i in range(1000):
        cust_id = f"cust_{uuid.uuid4().hex[:12]}"
        gender = random.choice(GENDERS)
        
        # Match gender to names for realism
        if gender == "Female":
            name = fake.name_female()
        elif gender == "Male":
            name = fake.name_male()
        else:
            name = fake.name()
            
        customer = {
            "_id": cust_id,
            "name": name,
            "email": f"{name.lower().replace(' ', '.')}.{i}@example.com",
            # Generate a 10 digit phone starting with 6-9
            "phone": f"{random.randint(6, 9)}{''.join([str(random.randint(0, 9)) for _ in range(9)])}",
            "city": random.choice(CITIES),
            "gender": gender,
            "age": random.randint(18, 65),
            "total_spend": 0,
            "total_orders": 0,
            "last_order_date": ""
        }
        customers.append(customer)
        customer_ids.append(cust_id)

    print("Generating 5000 orders...")
    orders = []
    
    # Track order stats per customer
    customer_stats = {cid: {"spend": 0, "orders_count": 0, "dates": []} for cid in customer_ids}
    
    # We want to make sure every customer gets at least one order to avoid empty stats,
    # then distribute the remaining 4000 orders randomly.
    # This guarantees healthy seed data.
    
    # First 1000 orders: 1 per customer
    today = datetime.utcnow()  # Use current date dynamically
    for cid in customer_ids:
        order_id = f"ord_{uuid.uuid4().hex[:12]}"
        category = random.choice(CATEGORIES)
        price_range = CATEGORY_PRICE_RANGES[category]
        amount = random.randint(price_range[0], price_range[1])
        
        # Order date in the last 365 days
        days_ago = random.randint(0, 365)
        order_date = (today - timedelta(days=days_ago)).strftime("%Y-%m-%d")
        
        order = {
            "_id": order_id,
            "customer_id": cid,
            "amount": amount,
            "category": category,
            "order_date": order_date
        }
        orders.append(order)
        
        customer_stats[cid]["spend"] += amount
        customer_stats[cid]["orders_count"] += 1
        customer_stats[cid]["dates"].append(order_date)

    # Remaining 4000 orders: distributed randomly
    for _ in range(4000):
        cid = random.choice(customer_ids)
        order_id = f"ord_{uuid.uuid4().hex[:12]}"
        category = random.choice(CATEGORIES)
        price_range = CATEGORY_PRICE_RANGES[category]
        amount = random.randint(price_range[0], price_range[1])
        
        days_ago = random.randint(0, 365)
        order_date = (today - timedelta(days=days_ago)).strftime("%Y-%m-%d")
        
        order = {
            "_id": order_id,
            "customer_id": cid,
            "amount": amount,
            "category": category,
            "order_date": order_date
        }
        orders.append(order)
        
        customer_stats[cid]["spend"] += amount
        customer_stats[cid]["orders_count"] += 1
        customer_stats[cid]["dates"].append(order_date)

    # Update customer documents with stats
    for customer in customers:
        cid = customer["_id"]
        stats = customer_stats[cid]
        customer["total_spend"] = stats["spend"]
        customer["total_orders"] = stats["orders_count"]
        # Find latest order date
        if stats["dates"]:
            customer["last_order_date"] = max(stats["dates"])

    print("Inserting data into database...")
    customers_col.insert_many(customers)
    orders_col.insert_many(orders)
    
    print(f"Database seeded successfully with {len(customers)} customers and {len(orders)} orders.")
    return len(customers), len(orders)

if __name__ == "__main__":
    seed_database()
