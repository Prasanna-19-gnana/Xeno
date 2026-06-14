import json
import time
import unittest
from app import app
from models import db, customers_col, orders_col, segments_col, campaigns_col, communications_col

class CRMIntegrationTests(unittest.TestCase):
    def setUp(self):
        # Set up Flask test client
        self.app = app.test_client()
        self.app.testing = True

    def test_01_health_check(self):
        print("\n--- Running Test 1: Health Check ---")
        response = self.app.get('/api/health')
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['status'], 'success')
        is_connected = any(term in data['message'] for term in ['MongoDB is connected', 'Database backend is'])
        self.assertTrue(is_connected, f"Unexpected health check message: {data['message']}")
        print("Health Check Passed.")

    def test_02_database_seeding(self):
        print("\n--- Running Test 2: Database Seeding ---")
        # Trigger seeder POST endpoint
        response = self.app.post('/api/customers/generate')
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['status'], 'success')
        self.assertIn('Seeded', data['message'])
        
        # Verify database counts
        num_customers = customers_col.count_documents({})
        num_orders = orders_col.count_documents({})
        self.assertEqual(num_customers, 1000)
        self.assertEqual(num_orders, 5000)
        print(f"Database Seeding Passed. Found {num_customers} customers and {num_orders} orders.")

    def test_03_query_customers_and_orders(self):
        print("\n--- Running Test 3: Querying Lists ---")
        # Test paginated customers
        response = self.app.get('/api/customers?limit=5')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data['data']), 5)
        self.assertTrue(data['total'] >= 5)

        # Test paginated orders
        response = self.app.get('/api/orders?limit=5')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data['data']), 5)
        self.assertTrue(data['total'] >= 5)
        print("Customer and Order Querying Passed.")

    def test_04_create_and_fetch_segment(self):
        print("\n--- Running Test 4: Segment Creation & Rules ---")
        # Define segment rules
        segment_payload = {
            "name": "Chennai Footwear Buyers",
            "rules": {
                "city_eq": "Chennai",
                "category_bought": "Shoes"
            }
        }
        
        response = self.app.post('/api/segments', 
                                 data=json.dumps(segment_payload), 
                                 content_type='application/json')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(data['status'], 'success')
        
        segment_id = data['data']['_id']
        customer_count = data['data']['customer_count']
        self.assertTrue(customer_count >= 0)
        
        # Fetch customers in segment
        cust_response = self.app.get(f'/api/segments/{segment_id}/customers?limit=5')
        cust_data = json.loads(cust_response.data)
        self.assertEqual(cust_response.status_code, 200)
        self.assertEqual(cust_data['total'], customer_count)
        
        # Save variables on test instance for subsequent tests
        CRMIntegrationTests.test_segment_id = segment_id
        print(f"Segment Creation Passed. Segment ID: {segment_id}, Matching Shoppers: {customer_count}")

    def test_05_create_and_send_campaign(self):
        print("\n--- Running Test 5: Campaign Dispatch ---")
        self.assertIsNotNone(CRMIntegrationTests.test_segment_id)
        
        # Create campaign draft
        campaign_payload = {
            "name": "Summer Sneakers Launch",
            "segment_id": CRMIntegrationTests.test_segment_id,
            "channel": "sms",
            "message": "Hi {{name}}! Check out our new sneaker collection at TrendWear."
        }
        
        response = self.app.post('/api/campaigns', 
                                 data=json.dumps(campaign_payload), 
                                 content_type='application/json')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 201)
        
        campaign_id = data['data']['_id']
        CRMIntegrationTests.test_campaign_id = campaign_id
        
        # Send campaign
        send_response = self.app.post(f'/api/campaigns/{campaign_id}/send')
        send_data = json.loads(send_response.data)
        self.assertEqual(send_response.status_code, 200)
        self.assertEqual(send_data['status'], 'success')
        
        # Wait slightly for background thread to run database inserts
        time.sleep(0.5)
        
        # Check that communications were created
        comms_count = communications_col.count_documents({"campaign_id": campaign_id})
        self.assertTrue(comms_count > 0)
        print(f"Campaign Dispatch Passed. Created campaign {campaign_id} with {comms_count} outbox communications.")

    def test_06_receipt_callbacks_and_funnel(self):
        print("\n--- Running Test 6: Receipt Callback & Funnel Stats ---")
        self.assertIsNotNone(CRMIntegrationTests.test_campaign_id)
        camp_id = CRMIntegrationTests.test_campaign_id
        
        # Find one communication sent
        comm = communications_col.find_one({"campaign_id": camp_id})
        self.assertIsNotNone(comm)
        comm_id = comm["_id"]
        
        # Simulate 'delivered' callback receipt
        callback_payload = {
            "communication_id": comm_id,
            "campaign_id": camp_id,
            "customer_id": comm["customer_id"],
            "status": "delivered"
        }
        
        res = self.app.post('/api/receipts', 
                            data=json.dumps(callback_payload), 
                            content_type='application/json')
        self.assertEqual(res.status_code, 200)
        
        # Verify status updated
        updated_comm = communications_col.find_one({"_id": comm_id})
        self.assertEqual(updated_comm["status"], "delivered")
        self.assertIn("delivered", updated_comm["events"])
        
        # Simulate 'clicked' callback receipt
        callback_payload["status"] = "clicked"
        res = self.app.post('/api/receipts', 
                            data=json.dumps(callback_payload), 
                            content_type='application/json')
        self.assertEqual(res.status_code, 200)
        
        # Verify status is clicked or converted
        updated_comm = communications_col.find_one({"_id": comm_id})
        self.assertIn(updated_comm["status"], ["clicked", "converted"])
        self.assertIn("clicked", updated_comm["events"])
        
        # Fetch campaign stats to check funnel numbers
        stats_res = self.app.get(f'/api/campaigns/{camp_id}/stats')
        stats_data = json.loads(stats_res.data)
        self.assertEqual(stats_res.status_code, 200)
        
        funnel = stats_data["funnel"]
        self.assertTrue(funnel["delivered"] >= 1)
        self.assertTrue(funnel["opened"] >= 1 or funnel["clicked"] >= 1)
        
        print("Receipt Callback and Funnel Stats Passed.")

if __name__ == '__main__':
    unittest.main()
