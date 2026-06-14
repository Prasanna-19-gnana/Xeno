# 🚀 Xeno CRM ML Integration - Quick Reference

## System Status
- ✅ Backend: Port 5002 (Running)
- ✅ Frontend: Port 5174 (Running)
- ✅ Database: 3,900 customers
- ✅ Models: 3 trained + loaded
- ✅ Endpoints: 4 ML APIs

## One-Line Start
```bash
# Terminal 1
cd /Users/gnanaprasanna/Desktop/Xeno_project/crm-backend && python3 app.py

# Terminal 2
cd /Users/gnanaprasanna/Desktop/Xeno_project/frontend && npm run dev
```

## Test Commands

### Get Customer ID
```bash
CUST_ID=$(curl -s http://localhost:5002/api/customers?limit=1 | \
  python3 -c "import sys,json; print(json.load(sys.stdin)['data'][0]['_id'])")
echo $CUST_ID
```

### Test Segmentation
```bash
curl http://localhost:5002/api/ml/predict/segment/$CUST_ID | python3 -m json.tool
```

### Test Churn
```bash
curl http://localhost:5002/api/ml/predict/churn/$CUST_ID | python3 -m json.tool
```

### Test LTV
```bash
curl http://localhost:5002/api/ml/predict/ltv/$CUST_ID | python3 -m json.tool
```

### Bulk Prediction
```bash
curl -X POST http://localhost:5002/api/ml/bulk-predict \
  -H 'Content-Type: application/json' -d '{"limit": 50}' | \
  python3 -m json.tool
```

## Key Files

| File | Purpose |
|------|---------|
| `shopping_trends.csv` | 3,900 customer records |
| `load_shopping_trends.py` | Load CSV to database |
| `train_models.py` | Train ML models |
| `routes/ml.py` | ML prediction endpoints |
| `models/*.pkl` | Trained models |
| `ML_MODELS_README.md` | Full documentation |

## Database Info

### Collections
- **customers** (3,900 docs)
  - Fields: age, gender, city, segment, total_spend, total_orders, etc.
- **orders** (3,900 docs)
  - Fields: customer_id, amount, category, order_date, etc.

### Segments
- 🌟 High-Value: 972 customers
- 👥 Regular: 1,268 customers
- ⚠️ At-Risk: 1,271 customers
- 🆕 New: 389 customers

## API Endpoints

### ML Predictions
```
GET  /api/ml/predict/segment/<customer_id>
GET  /api/ml/predict/churn/<customer_id>
GET  /api/ml/predict/ltv/<customer_id>
POST /api/ml/bulk-predict
```

### Existing Endpoints (All still available)
```
GET    /api/customers           - List customers
GET    /api/orders              - List orders
GET    /api/segments            - List segments
GET    /api/campaigns           - List campaigns
POST   /api/ai/campaign-assistant - AI help
GET    /api/health              - System health
```

## Reinstall/Reset Commands

### Reload Dataset
```bash
cd crm-backend && python3 load_shopping_trends.py
```

### Retrain Models
```bash
cd crm-backend && python3 train_models.py
```

### Check Health
```bash
curl http://localhost:5002/api/health | python3 -m json.tool
```

### Kill & Restart Backend
```bash
pkill -f "python3 app.py" && sleep 2 && cd crm-backend && python3 app.py
```

## Response Examples

### Segment Prediction
```json
{
  "segment": "High-Value Customers",
  "segment_id": 0,
  "description": "High spending, frequent purchases, low churn risk",
  "customer_data": {
    "name": "Customer 43",
    "spend": 100,
    "orders": 1,
    "age": 20
  },
  "status": "success"
}
```

### Churn Prediction
```json
{
  "churn_probability": 1.0,
  "churn_risk_level": "High",
  "recommendation": "High priority: Send personalized offer or loyalty reward",
  "customer_id": "cust_...",
  "status": "success"
}
```

### LTV Prediction
```json
{
  "current_ltv": 100.0,
  "predicted_ltv": 100.0,
  "potential_growth": 0.0,
  "confidence": "High",
  "customer_id": "cust_...",
  "status": "success"
}
```

## Dependencies

Automatically installed:
- pandas==2.0.3
- scikit-learn==1.3.2
- mongomock==4.1.2

## URLs

| Service | URL |
|---------|-----|
| Frontend | http://localhost:5174 |
| Backend | http://localhost:5002 |
| API Docs | Via curl (REST) |
| Health Check | http://localhost:5002/api/health |

## Tips & Tricks

### Get Customer for Testing
```bash
curl -s http://localhost:5002/api/customers | \
  python3 -c "import sys,json; print(json.load(sys.stdin)['data'][0]['_id'])"
```

### View All Segments
```bash
curl http://localhost:5002/api/segments | python3 -m json.tool
```

### View Model Metrics
```bash
cat crm-backend/models/model_metrics.json | python3 -m json.tool
```

### Check Running Processes
```bash
ps aux | grep "python3 app.py\|npm run dev" | grep -v grep
```

## Common Issues

| Issue | Solution |
|-------|----------|
| Port 5002 in use | `lsof -ti:5002 \| xargs kill -9` |
| Port 5174 in use | `lsof -ti:5174 \| xargs kill -9` |
| Models missing | Run `python3 train_models.py` |
| Database connection | Check `curl http://localhost:5002/api/health` |
| Frontend won't load | Verify `npm install` completed |

## Documentation Files

- **ML_INTEGRATION_SUMMARY.md** - Complete overview (this folder)
- **SHOPPING_TRENDS_INTEGRATION.md** - Integration details (this folder)
- **crm-backend/ML_MODELS_README.md** - ML models documentation

---

**Everything is ready! Start the system and enjoy your ML-powered CRM!** 🚀
