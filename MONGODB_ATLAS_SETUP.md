# MongoDB Atlas Setup Guide

Your CRM backend is now configured to **strictly connect to MongoDB Atlas** and store all data in **JSON format**.

## Prerequisites

1. MongoDB Atlas account (free tier available at [cloud.mongodb.com](https://cloud.mongodb.com))
2. Python 3.8+ with pip
3. Your Atlas cluster deployed and running

## Step 1: Create MongoDB Atlas Cluster

1. Go to [MongoDB Atlas](https://cloud.mongodb.com)
2. Sign in or create a free account
3. Click "Create a Deployment" → Select **M0 Shared** (Free tier)
4. Choose your region and cluster name
5. Wait for cluster to be deployed (usually 1-2 minutes)

## Step 2: Set Up Database User

1. In Atlas dashboard, go to **Database Access** (left sidebar)
2. Click **Add New Database User**
3. Create credentials:
   - **Username**: `your_username`
   - **Password**: Generate a strong password (copy it!)
   - **Database User Privileges**: Select "Atlas admin"
4. Click **Add User**

## Step 3: Allow IP Access

1. Go to **Network Access** (left sidebar)
2. Click **Add IP Address**
3. Choose:
   - **Allow access from anywhere** (0.0.0.0/0) for development
   - OR add your specific IP for production
4. Click **Confirm**

## Step 4: Get Connection String

1. Go to **Databases** → Click your cluster
2. Click **Connect** button
3. Select **Drivers** → **Python** → **Version 4.6 or later**
4. Copy the connection string (looks like):
   ```
   mongodb+srv://username:password@cluster.mongodb.net/?appName=MyApp
   ```
5. Replace `<password>` with your actual password
6. Replace `<username>` with your actual username

## Step 5: Configure Your Application

1. Navigate to the backend folder:
   ```bash
   cd /Users/gnanaprasanna/Desktop/Xeno_project/crm-backend
   ```

2. Update the `.env` file with your MongoDB Atlas connection string:
   ```
   MONGO_URI=mongodb+srv://your_username:your_password@cluster0.xxxxx.mongodb.net/?appName=Cluster0Xeno
   GEMINI_API_KEY=your_api_key
   FAKE_CHANNEL_URL=http://localhost:5001/send-message
   CRM_CALLBACK_URL=http://localhost:5002/api/receipts
   ```

## Step 6: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 7: Run the Application

```bash
python app.py
```

You should see:
```
📊 Connecting to MongoDB Atlas...
Database: trendwear_crm
✅ Successfully connected to MongoDB Atlas!
```

## Data Storage Format

All data is stored in **JSON-compatible format** in MongoDB:

- **Documents**: MongoDB stores data as BSON (binary JSON), which is automatically converted to JSON
- **Serialization**: All API responses use automatic JSON conversion
- **Data Types**:
  - `_id`: Unique identifier (string format)
  - `created_at`, `updated_at`: ISO 8601 datetime strings
  - `metadata`: JSON objects for flexible data storage

## Example Document Structure

```json
{
  "_id": "cust_a1b2c3d4e5f6",
  "name": "John Doe",
  "email": "john@example.com",
  "phone": "+91-9876543210",
  "gender": "Male",
  "age": 28,
  "city": "Mumbai",
  "total_spend": 15999.50,
  "total_orders": 5,
  "last_order_date": "2024-01-15T10:30:00",
  "created_at": "2023-12-01T14:25:33",
  "metadata": {
    "subscription_status": "active",
    "preferences": {
      "email_notifications": true,
      "sms_notifications": false
    }
  }
}
```

## Troubleshooting

### "MONGO_URI environment variable is required"
- Make sure `.env` file exists in `crm-backend/` folder
- Verify `MONGO_URI` is set with a valid MongoDB Atlas connection string

### "Failed to connect to MongoDB Atlas"
- Check if your IP is in the **Network Access** whitelist
- Verify username and password are correct in the connection string
- Ensure cluster is deployed and running in Atlas dashboard
- Check internet connection

### "Authentication failed"
- Ensure password is correctly URL-encoded in connection string
- Special characters in password should be URL-encoded (e.g., `@` → `%40`)
- Use MongoDB URI Generator in Atlas for correct encoding

## Verified Configuration

✅ **MongoDB Atlas** (required)
✅ **JSON Data Format** (automatic)
✅ **PyMongo 4.6.2** (installed)
✅ **Custom JSON Encoder** (configured)
✅ **Connection Validation** (on startup)

## Next Steps

1. Generate seed data: `POST /api/customers/generate`
2. Verify data in MongoDB Atlas → Collections
3. Query data: `GET /api/customers`

All responses are in valid JSON format for seamless frontend integration!
