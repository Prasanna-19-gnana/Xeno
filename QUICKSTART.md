# Quick Start Guide - MongoDB Atlas & JSON Integration

## ⚡ 5-Minute Setup

### 1. Get MongoDB Atlas Connection String
```
mongodb+srv://your_username:your_password@cluster0.xxxxx.mongodb.net/?appName=YourApp
```

### 2. Update `.env` File
```bash
cd crm-backend
# Edit .env and update MONGO_URI with your connection string
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run Backend
```bash
python app.py
```

Expected output:
```
📊 Connecting to MongoDB Atlas...
Database: trendwear_crm
✅ Successfully connected to MongoDB Atlas!
```

---

## 🔑 Key Features

✅ **MongoDB Atlas Only** - No local fallback
✅ **JSON Data Format** - BSON automatically converted
✅ **Automatic Serialization** - ObjectId & datetime handled
✅ **Error on Startup** - Clear messages if configuration missing

---

## 📝 Environment Variables

```
MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/?appName=YourApp
DEV_MODE=true
FIREBASE_CREDENTIALS=./firebase-service-account.json
FIREBASE_PROJECT_ID=your-firebase-project-id
GEMINI_API_KEY=your_api_key_here
FAKE_CHANNEL_URL=http://localhost:5001/send-message
CRM_CALLBACK_URL=http://localhost:5002/api/receipts
```

### Firebase fallback database

The backend now tries databases in this order:

1. MongoDB Atlas from `MONGO_URI`
2. Firebase Firestore from `FIREBASE_CREDENTIALS`
3. Local MongoDB, only when `DEV_MODE=true`

To enable Firebase fallback:

1. Create a Firebase project.
2. Enable Firestore Database.
3. In Firebase Console, open Project settings → Service accounts.
4. Generate a new private key.
5. Save it as:

```bash
crm-backend/firebase-service-account.json
```

6. Add these values to `crm-backend/.env`:

```bash
FIREBASE_CREDENTIALS=./firebase-service-account.json
FIREBASE_PROJECT_ID=your-firebase-project-id
```

The service-account JSON is ignored by `.gitignore`; do not commit it.

---

## 🧪 Test Data

Generate 1000 customers with orders:
```bash
curl -X POST http://localhost:5002/api/customers/generate
```

---

## 📚 Full Documentation

See `MONGODB_ATLAS_SETUP.md` for detailed step-by-step instructions
See `MIGRATION_SUMMARY.md` for complete implementation details

---

## ✨ Data Format Example

### Customer Document (JSON)
```json
{
  "_id": "cust_abc123",
  "name": "John Doe",
  "email": "john@example.com",
  "total_spend": 15999.50,
  "created_at": "2024-01-15T10:30:00"
}
```

### API Response (JSON)
```json
{
  "status": "success",
  "data": [{ "customer": "documents" }]
}
```

---

## 🚀 Next Steps

1. Create MongoDB Atlas account (free tier available)
2. Deploy cluster
3. Create database user
4. Update `.env` with connection string
5. Run `python app.py`
6. Test endpoints

That's it! All data is now stored in MongoDB Atlas as JSON.

---

## 🆘 Common Issues

| Problem | Solution |
|---------|----------|
| MONGO_URI missing | Add to `.env` file |
| Connection failed | Check IP whitelist in Atlas Network Access |
| Auth error | Verify username/password, use URI generator |

---

**Status**: ✅ Ready for production
**Database**: MongoDB Atlas (cloud-native)
**Data Format**: JSON (fully serialized)
**Fallback**: None (strict Atlas only)
