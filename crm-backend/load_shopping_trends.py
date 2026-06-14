"""
Load Shopping Trends dataset into the CRM database
Maps shopping trends data to customers and orders collections
"""
import pandas as pd
import uuid
from datetime import datetime, timedelta
from models import customers_col, orders_col, init_db

def load_shopping_trends_dataset():
    """Load shopping trends CSV and populate database"""
    print("📊 Reading shopping_trends.csv...")
    
    # Read the CSV
    df = pd.read_csv('shopping_trends.csv')
    print(f"✅ Loaded {len(df)} records from CSV")
    
    print("Clearing existing data...")
    customers_col.delete_many({})
    orders_col.delete_many({})
    
    print("Re-initializing indexes...")
    init_db()
    
    # Map category names to match the system
    category_mapping = {
        'Clothing': 'T-Shirts',
        'Footwear': 'Shoes',
        'Accessories': 'Accessories',
        'Outerwear': 'Dresses'
    }
    
    # Group by Customer ID to create unique customers
    print("Processing customers from dataset...")
    customers = []
    customer_map = {}  # Map dataset customer IDs to generated IDs
    
    unique_customers = df.drop_duplicates(subset=['Customer ID'])
    
    for idx, row in unique_customers.iterrows():
        cust_id = f"cust_{uuid.uuid4().hex[:12]}"
        customer_map[int(row['Customer ID'])] = cust_id
        
        # Generate name from dataset attributes
        name = f"Customer {row['Customer ID']}"
        
        customer = {
            "_id": cust_id,
            "name": name,
            "email": f"customer.{row['Customer ID']}@trendwear.com",
            "phone": f"{9}{str(row['Customer ID']).zfill(9)[-9:]}",  # Generate phone from ID
            "city": row['Location'],
            "gender": row['Gender'],
            "age": int(row['Age']),
            "total_spend": 0,
            "total_orders": 0,
            "last_order_date": "",
            "subscription_status": row['Subscription Status'],
            "review_rating": float(row['Review Rating']),
            "preferred_payment": row['Preferred Payment Method'],
            "purchase_frequency": row['Frequency of Purchases']
        }
        customers.append(customer)
    
    print(f"✅ Created {len(customers)} customer records")
    
    # Create orders from all transactions in the dataset
    print("Processing orders from dataset...")
    orders = []
    customer_stats = {cid: {"spend": 0, "orders_count": 0, "dates": []} for cid in customer_map.values()}
    
    base_date = datetime.utcnow()
    
    for idx, row in df.iterrows():
        dataset_cust_id = int(row['Customer ID'])
        cust_id = customer_map[dataset_cust_id]
        
        order_id = f"ord_{uuid.uuid4().hex[:12]}"
        
        # Map category
        original_category = row['Category']
        category = category_mapping.get(original_category, 'T-Shirts')
        
        # Use purchase amount
        amount = int(row['Purchase Amount (USD)'])
        
        # Generate order date based on frequency of purchases
        frequency_days = {
            'Weekly': 7,
            'Fortnightly': 14,
            'Bi-Weekly': 14,
            'Monthly': 30,
            'Quarterly': 90,
            'Every 3 Months': 90,
            'Annually': 365
        }
        
        days_ago = frequency_days.get(row['Frequency of Purchases'], 30)
        days_ago += int(row['Previous Purchases']) * 30  # Add historical depth
        days_ago = min(days_ago, 365)  # Cap at 1 year
        
        order_date = (base_date - timedelta(days=days_ago)).strftime("%Y-%m-%d")
        
        order = {
            "_id": order_id,
            "customer_id": cust_id,
            "amount": amount,
            "category": category,
            "order_date": order_date,
            "item": row['Item Purchased'],
            "size": row['Size'],
            "color": row['Color'],
            "season": row['Season'],
            "discount_applied": row['Discount Applied'] == 'Yes',
            "promo_used": row['Promo Code Used'] == 'Yes',
            "shipping_type": row['Shipping Type']
        }
        orders.append(order)
        
        # Update customer stats
        customer_stats[cust_id]["spend"] += amount
        customer_stats[cust_id]["orders_count"] += 1
        customer_stats[cust_id]["dates"].append(order_date)
    
    print(f"✅ Created {len(orders)} order records")
    
    # Update customer documents with aggregated stats
    for customer in customers:
        cust_id = customer["_id"]
        stats = customer_stats[cust_id]
        customer["total_spend"] = stats["spend"]
        customer["total_orders"] = stats["orders_count"]
        if stats["dates"]:
            customer["last_order_date"] = max(stats["dates"])
    
    # Insert into database
    print("💾 Inserting customers into database...")
    customers_col.insert_many(customers)
    
    print("💾 Inserting orders into database...")
    orders_col.insert_many(orders)
    
    print(f"""
✅ Shopping Trends Dataset Loaded Successfully!
   📊 Customers: {len(customers)}
   📦 Orders: {len(orders)}
   💰 Total Revenue: ${sum(o['amount'] for o in orders):,}
    """)
    
    return len(customers), len(orders)

if __name__ == "__main__":
    load_shopping_trends_dataset()
