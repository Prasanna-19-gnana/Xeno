#!/usr/bin/env python3
"""Diagnostic script to debug segment/campaign sending issues."""

from models import segments_col, customers_col, campaigns_col
from routes.segments import compile_segment_rules

# Get all segments
print("=" * 60)
print("SEGMENTS IN DATABASE:")
print("=" * 60)
segments = list(segments_col.find())
for seg in segments:
    print(f"\nSegment ID: {seg['_id']}")
    print(f"  Name: {seg['name']}")
    print(f"  Rules: {seg.get('rules', {})}")
    print(f"  Stored customer_count: {seg.get('customer_count', 'N/A')}")
    
    # Recompile rules and count
    mongo_query = compile_segment_rules(seg.get('rules', {}))
    print(f"  Compiled MongoDB query: {mongo_query}")
    actual_count = customers_col.count_documents(mongo_query)
    print(f"  Actual customer count from query: {actual_count}")

# Get all campaigns
print("\n" + "=" * 60)
print("CAMPAIGNS IN DATABASE:")
print("=" * 60)
campaigns = list(campaigns_col.find())
for camp in campaigns:
    print(f"\nCampaign ID: {camp['_id']}")
    print(f"  Name: {camp['name']}")
    print(f"  Segment ID: {camp.get('segment_id', 'N/A')}")
    print(f"  Status: {camp.get('status', 'N/A')}")
    print(f"  Error: {camp.get('error', 'N/A')}")

# Sample customers
print("\n" + "=" * 60)
print("SAMPLE CUSTOMERS:")
print("=" * 60)
sample_customers = list(customers_col.find().limit(5))
for cust in sample_customers:
    print(f"\nCustomer ID: {cust['_id']}")
    print(f"  Name: {cust.get('name', 'N/A')}")
    print(f"  Total Spend: {cust.get('total_spend', 0)}")
    print(f"  Total Orders: {cust.get('total_orders', 0)}")
    print(f"  City: {cust.get('city', 'N/A')}")

# Total customer count
total = customers_col.count_documents({})
print(f"\nTotal customers in database: {total}")

# Check query with total_spend_gt: 100
print("\n" + "=" * 60)
print("QUERY TEST - total_spend > 100:")
print("=" * 60)
test_query = {"total_spend": {"$gt": 100}}
test_count = customers_col.count_documents(test_query)
print(f"Query: {test_query}")
print(f"Count: {test_count}")
sample = list(customers_col.find(test_query).limit(3))
print(f"Sample results: {len(sample)} found")
for s in sample:
    print(f"  - {s['_id']}: {s.get('total_spend', 0)}")
