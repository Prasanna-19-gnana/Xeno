# 🚀 Xeno CRM Project - Complete Run Commands

## 📋 Project Overview

This is a full-stack CRM application with:
- **Backend**: Python Flask API connected to MongoDB Atlas
- **Frontend**: React with Vite
- **Fake Channel Service**: Mock messaging service
- **Data Storage**: MongoDB Atlas with JSON format

---

## 🛠️ Prerequisites

### Required Software
- **Python 3.8+** (`/usr/bin/python3`)
- **Node.js 20+** and **npm 11+**
- **MongoDB Atlas Account** (free tier available)
- **macOS** environment

### Verify Installation
```bash
/usr/bin/python3 --version    # Should show Python 3.9+
node --version                 # Should show v24+
npm --version                  # Should show npm 11+
```

---

## 📁 Project Structure

```
Xeno_project/
├── crm-backend/              # Flask backend API
│   ├── app.py
│   ├── models.py
│   ├── requirements.txt
│   ├── seed_data.py
│   ├── routes/
│   └── .env                  # ← Configure MongoDB Atlas here
├── frontend/                 # React + Vite frontend
│   ├── package.json
│   ├── vite.config.js
│   └── src/
├── fake-channel-service/     # Mock messaging service
│   ├── app.py
│   └── requirements.txt
└── README.md
```

---

## 🚀 Quick Start (All Services in One Go)

### Option 1: Run Everything (Recommended)

Open **3 separate terminals** and run these commands in order:

**Terminal 1 - Backend (Port 5002)**
```bash
cd /Users/gnanaprasanna/Desktop/Xeno_project/crm-backend
/usr/bin/python3 app.py
```

**Terminal 2 - Frontend (Port 5173)**
```bash
cd /Users/gnanaprasanna/Desktop/Xeno_project/frontend
npm run dev
```

**Terminal 3 - Fake Channel Service (Port 5001)**
```bash
cd /Users/gnanaprasanna/Desktop/Xeno_project/fake-channel-service
/usr/bin/python3 app.py
```

Then open your browser:
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:5002
- **Fake Channel**: http://localhost:5001

---

## 📦 Installation Commands

### 1️⃣ Backend Setup

```bash
# Navigate to backend
cd /Users/gnanaprasanna/Desktop/Xeno_project/crm-backend

# Install Python dependencies
/usr/bin/python3 -m pip install -r requirements.txt

# Verify installation
/usr/bin/python3 -c "import flask; import pymongo; print('✅ Dependencies installed')"
```

### 2️⃣ Frontend Setup

```bash
# Navigate to frontend
cd /Users/gnanaprasanna/Desktop/Xeno_project/frontend

# Install Node dependencies
npm install

# Verify installation
npm list react react-dom vite
```

### 3️⃣ Fake Channel Service Setup

```bash
# Navigate to fake-channel-service
cd /Users/gnanaprasanna/Desktop/Xeno_project/fake-channel-service

# Install Python dependencies
/usr/bin/python3 -m pip install -r requirements.txt
```

---

## 🎯 Individual Service Commands

### Backend (Flask API)

**Start Backend**
```bash
cd /Users/gnanaprasanna/Desktop/Xeno_project/crm-backend
/usr/bin/python3 app.py
```

**Expected Output:**
```
📊 Connecting to MongoDB Atlas...
Database: trendwear_crm
✅ Successfully connected to MongoDB Atlas!
Database indexes successfully initialized.
 * Running on http://127.0.0.1:5002
```

**Test Backend**
```bash
# Health check
curl http://localhost:5002/api/customers

# Generate seed data (1000 customers)
curl -X POST http://localhost:5002/api/customers/generate

# Get customers with pagination
curl "http://localhost:5002/api/customers?page=1&limit=10"

# Search customers
curl "http://localhost:5002/api/customers?search=John&city=Mumbai"
```

---

### Frontend (React + Vite)

**Start Frontend (Development)**
```bash
cd /Users/gnanaprasanna/Desktop/Xeno_project/frontend
npm run dev
```

**Expected Output:**
```
  VITE v8.0.16  ready in 258 ms
  ➜  Local:   http://localhost:5173/
  ➜  press h + enter to show help
```

**Build for Production**
```bash
cd /Users/gnanaprasanna/Desktop/Xeno_project/frontend
npm run build
```

**Preview Production Build**
```bash
cd /Users/gnanaprasanna/Desktop/Xeno_project/frontend
npm run preview
```

**Lint Check**
```bash
cd /Users/gnanaprasanna/Desktop/Xeno_project/frontend
npm run lint
```

---

### Fake Channel Service

**Start Fake Channel Service**
```bash
cd /Users/gnanaprasanna/Desktop/Xeno_project/fake-channel-service
/usr/bin/python3 app.py
```

**Expected Output:**
```
 * Running on http://127.0.0.1:5001
```

---

## 🗄️ MongoDB Atlas Setup

### Configure Connection String

1. **Get MongoDB Atlas URI from your cluster dashboard**
2. **Update `.env` file** in `crm-backend/`:

```bash
# Edit the file
nano /Users/gnanaprasanna/Desktop/Xeno_project/crm-backend/.env

# Update MONGO_URI line with your connection string
MONGO_URI=mongodb+srv://your_username:your_password@cluster0.xxxxx.mongodb.net/?appName=Cluster0Xeno
```

### Connection Modes

**Development Mode** (with local fallback)
```bash
# Edit .env
DEV_MODE=true
```
This allows the app to fall back to local MongoDB if Atlas is unavailable.

**Production Mode** (strict Atlas only)
```bash
# Edit .env
DEV_MODE=false
```
This requires MongoDB Atlas to be running.

---

## 📊 API Endpoints

### Customer Endpoints

```bash
# Get all customers
GET /api/customers?page=1&limit=20

# Get single customer
GET /api/customers/{customer_id}

# Generate seed data
POST /api/customers/generate

# Search customers
GET /api/customers?search=name&city=Mumbai
```

### Order Endpoints

```bash
# Get all orders
GET /api/orders

# Get order by ID
GET /api/orders/{order_id}
```

### Campaign Endpoints

```bash
# Get all campaigns
GET /api/campaigns

# Create campaign
POST /api/campaigns

# Get campaign by ID
GET /api/campaigns/{campaign_id}
```

### Segment Endpoints

```bash
# Get all segments
GET /api/segments

# Create segment
POST /api/segments
```

### Other Endpoints

```bash
# Get communications
GET /api/communications

# Get receipts
GET /api/receipts

# AI suggestions
POST /api/ai/suggestions
```

---

## 🧪 Testing Commands

### Test All Services Running

```bash
# Check backend
curl http://localhost:5002/api/customers | head -c 100

# Check frontend
curl -s http://localhost:5173/ | head -c 50

# Check fake channel
curl http://localhost:5001/ | head -c 50
```

### Generate Sample Data

```bash
curl -X POST http://localhost:5002/api/customers/generate
```

### View Database Collections (in MongoDB Atlas)

1. Go to [MongoDB Atlas](https://cloud.mongodb.com)
2. Click your cluster
3. Click **Collections** tab
4. View data in:
   - `customers`
   - `orders`
   - `segments`
   - `campaigns`
   - `communications`
   - `activity_logs`

---

## 🔧 Troubleshooting

### Backend Won't Start

**Problem**: `MONGO_URI environment variable is required`
```bash
# Solution: Check .env file exists and has MONGO_URI
cat /Users/gnanaprasanna/Desktop/Xeno_project/crm-backend/.env
```

**Problem**: `Failed to connect to MongoDB Atlas`
```bash
# Solution 1: Check your IP is whitelisted in Atlas Network Access
# Solution 2: Try with DEV_MODE=true in .env to use local MongoDB
# Solution 3: Verify MONGO_URI is correct and credentials work
```

**Problem**: `No module named 'pymongo'`
```bash
# Solution: Install dependencies again
cd /Users/gnanaprasanna/Desktop/Xeno_project/crm-backend
/usr/bin/python3 -m pip install -r requirements.txt
```

---

### Frontend Won't Start

**Problem**: `npm: command not found`
```bash
# Solution: Use npm directly (should be available)
which npm
```

**Problem**: `Cannot find module 'vite'`
```bash
# Solution: Install dependencies
cd /Users/gnanaprasanna/Desktop/Xeno_project/frontend
npm install
```

**Problem**: Port 5173 already in use
```bash
# Solution: Use different port
npm run dev -- --port 5174
```

---

### Connection Issues

**Backends not communicating**
```bash
# Check if fake-channel-service is running on port 5001
lsof -i :5001

# Check if frontend can reach backend
curl http://localhost:5002/api/customers
```

**MongoDB Connection Timeout**
```bash
# Check internet connection
ping 8.8.8.8

# Check MongoDB Atlas cluster status in dashboard

# Try with local MongoDB (requires installation)
# Update .env: DEV_MODE=true
```

---

## 📈 Development Workflow

### During Development

```bash
# Terminal 1: Run Backend
cd crm-backend && /usr/bin/python3 app.py

# Terminal 2: Run Frontend
cd frontend && npm run dev

# Terminal 3: Run Tests/Make Changes
# Edit files and see live reload
```

### Before Production

```bash
# Build frontend
cd frontend && npm run build

# Test production build
npm run preview

# Check backend logs
# Verify MongoDB Atlas connection
# Test all API endpoints
```

---

## 🔐 Environment Configuration

### `.env` File Location
```
/Users/gnanaprasanna/Desktop/Xeno_project/crm-backend/.env
```

### Required Variables

```bash
PORT=5002
MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/?appName=Cluster0Xeno
DEV_MODE=false                    # Set to true for development with fallback
GEMINI_API_KEY=your_api_key       # Optional, for AI features
FAKE_CHANNEL_URL=http://localhost:5001/send-message
CRM_CALLBACK_URL=http://localhost:5002/api/receipts
```

---

## 📚 Documentation References

- [MongoDB Atlas Setup Guide](./MONGODB_ATLAS_SETUP.md)
- [Migration Summary](./MIGRATION_SUMMARY.md)
- [Quick Start](./QUICKSTART.md)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [React Documentation](https://react.dev)
- [Vite Documentation](https://vitejs.dev)
- [PyMongo Documentation](https://pymongo.readthedocs.io/)

---

## 🎯 Summary

| Service | Port | Start Command | Status |
|---------|------|---------------|--------|
| **Backend** | 5002 | `python app.py` | Flask API |
| **Frontend** | 5173 | `npm run dev` | React Vite |
| **Fake Channel** | 5001 | `python app.py` | Mock Service |
| **MongoDB** | Cloud | Atlas Cluster | JSON Storage |

---

## ✅ Verification Checklist

- [ ] Python 3.9+ installed
- [ ] Node.js 20+ and npm 11+ installed
- [ ] MongoDB Atlas account created
- [ ] Cluster deployed in Atlas
- [ ] Database user created
- [ ] IP address whitelisted
- [ ] `.env` file updated with MONGO_URI
- [ ] Dependencies installed (`npm install` + `pip install -r requirements.txt`)
- [ ] Backend starts without errors
- [ ] Frontend starts on port 5173
- [ ] Can access http://localhost:5173
- [ ] Can query API endpoints

---

## 🚀 Next Steps

1. **Setup**: Follow "Installation Commands" section above
2. **Configure**: Update `.env` with your MongoDB Atlas connection
3. **Run**: Start all three services in separate terminals
4. **Test**: Access http://localhost:5173 in your browser
5. **Verify**: Generate sample data and view in MongoDB Atlas

**Happy Coding! 🎉**
