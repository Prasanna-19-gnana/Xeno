# Shopping Trends Dataset Integration & ML Model Training

## Overview
The Xeno CRM project has been updated to integrate the shopping trends dataset with full machine learning capabilities. The system now trains models on real customer shopping data and provides AI-powered predictions for customer segmentation, churn risk, and lifetime value.

## What's New

### 1. **Dataset Integration**
- **File**: `shopping_trends.csv` (3,900 customer records)
- **Data Loader**: `load_shopping_trends.py`
- **Loaded Into**:
  - **Customers Collection**: 3,900 unique customers with enriched attributes
  - **Orders Collection**: 3,900 purchase transactions
  - **Total Revenue**: $233,081

### 2. **Machine Learning Models**
Models are trained on the shopping trends dataset and saved in `models/` directory:

#### a. **Customer Segmentation Model** (K-Means)
- **Segments Identified**:
  - 🌟 High-Value Customers (972) - High spending, frequent purchases
  - 👥 Regular Customers (1,268) - Moderate spending, stable behavior
  - ⚠️ At-Risk Customers (1,271) - Low recent activity, churn candidates
  - 🆕 New Customers (389) - Limited purchase history

#### b. **Churn Prediction Model** (Random Forest)
- Predicts probability of customer churn (97.7% churn rate in current dataset)
- Provides targeted retention recommendations

#### c. **Lifetime Value (LTV) Model** (Random Forest Regressor)
- Predicts customer's future spending potential
- Average LTV: $59.76
- Range: $20 - $100

### 3. **New ML Prediction API Endpoints**

#### Get Customer Segment
```bash
GET /api/ml/predict/segment/<customer_id>
```
**Response**:
```json
{
  "segment": "High-Value Customers",
  "segment_id": 0,
  "description": "High spending, frequent purchases, low churn risk",
  "customer_data": {...}
}
```

#### Predict Churn Risk
```bash
GET /api/ml/predict/churn/<customer_id>
```
**Response**:
```json
{
  "churn_probability": 0.75,
  "churn_risk_level": "High",
  "recommendation": "Send personalized offer or loyalty reward"
}
```

#### Predict Lifetime Value
```bash
GET /api/ml/predict/ltv/<customer_id>
```
**Response**:
```json
{
  "current_ltv": 100.0,
  "predicted_ltv": 85.5,
  "potential_growth": -14.5,
  "confidence": "High"
}
```

#### Bulk Predictions
```bash
POST /api/ml/bulk-predict
{
  "limit": 50
}
```

## File Structure

```
crm-backend/
├── shopping_trends.csv           # Source dataset
├── load_shopping_trends.py       # Dataset loader script
├── train_models.py               # ML model training pipeline
├── requirements.txt              # Updated with pandas, scikit-learn
├── routes/
│   └── ml.py                     # ML prediction API endpoints
├── models/                       # Trained model artifacts
│   ├── segmentation_model.pkl
│   ├── churn_model.pkl
│   ├── ltv_model.pkl
│   └── model_metrics.json
└── app.py                        # Updated with ML blueprint
```

## How to Use

### 1. **Load the Dataset**
```bash
cd crm-backend
python3 load_shopping_trends.py
```

### 2. **Train Models**
```bash
python3 train_models.py
```

### 3. **Start the Backend**
```bash
python3 app.py
```

### 4. **Access ML Endpoints**
```bash
# Get a customer ID first
curl http://localhost:5002/api/customers?limit=1

# Predict segment
curl http://localhost:5002/api/ml/predict/segment/<customer_id>

# Predict churn
curl http://localhost:5002/api/ml/predict/churn/<customer_id>

# Predict LTV
curl http://localhost:5002/api/ml/predict/ltv/<customer_id>
```

## Key Features

### ✅ Database Integration
- ✅ All customer data persisted in MongoDB
- ✅ Segment information automatically added to customer records
- ✅ Works with local MongoDB fallback (automatically handles MongoDB Atlas SSL errors)

### ✅ Feature Engineering
Models use 9 customer features:
1. Age
2. Total Spend
3. Total Orders
4. Average Order Value
5. Days Since Last Order
6. Subscription Status
7. Gender
8. Review Rating
9. Purchase Frequency

### ✅ Predictions Available
- ✅ Real-time segmentation for any customer
- ✅ Churn probability with actionable recommendations
- ✅ Lifetime value forecasting
- ✅ Bulk prediction for campaign planning

### ✅ Fallback & Resilience
- ✅ Database fallback chain (MongoDB Atlas → Firebase → Local MongoDB → mongomock)
- ✅ Models gracefully handle missing data
- ✅ All endpoints have error handling

## Model Performance

| Model | Type | Training Samples | Accuracy Metric |
|-------|------|------------------|-----------------|
| Segmentation | K-Means | 3,900 | 4 segments identified |
| Churn | Random Forest | 3,900 | 97.7% churn rate detected |
| LTV | Random Forest | 3,900 | Average: $59.76, Range: $20-$100 |

## Dataset Mapping

### Customer CSV → Database
| CSV Column | Database Field | Usage |
|-----------|----------------|-------|
| Customer ID | Auto-generated _id | Document identifier |
| Age | age | Feature for ML models |
| Gender | gender | Feature for ML models |
| Location | city | Customer location |
| Subscription Status | subscription_status | Feature for segmentation |
| Review Rating | review_rating | Quality indicator |
| Frequency of Purchases | purchase_frequency | Purchase pattern |
| Previous Purchases | (incorporated in dates) | Customer history |

### Order CSV → Database
| CSV Column | Orders Field | Usage |
|-----------|--------------|-------|
| Customer ID | customer_id | Linking to customer |
| Purchase Amount (USD) | amount | Revenue tracking |
| Category | category | Product category |
| Item Purchased | item | Product name |
| Order Date | order_date | Timeline |
| Discount Applied | discount_applied | Promotion tracking |

## Analytics Available

### Dashboard Enhancements
- Customer segmentation breakdown
- Churn risk distribution
- LTV tier analysis
- Segment-specific metrics

### Bulk Operations
- Segment all customers at once
- Identify high-churn-risk cohorts
- Prioritize high-LTV customers for campaigns

### Campaign Optimization
- Target High-Value Customers with loyalty programs
- Create win-back campaigns for At-Risk segment
- Personalize offers based on LTV predictions

## Notes

- **Models are trained once**: Run `train_models.py` after loading new data
- **Real-time predictions**: Segmentation, churn, and LTV predictions are computed on-the-fly
- **Feature scaling**: All models use StandardScaler for feature normalization
- **Database persistence**: All predictions are consistent with MongoDB backend

## Next Steps

1. **Integrate ML predictions into the frontend** - Display customer segments and risk levels
2. **Create automated campaigns** - Based on churn risk and LTV predictions
3. **Set up model retraining** - Schedule periodic model updates as new data arrives
4. **Add A/B testing** - Validate model recommendations against actual customer behavior

## Troubleshooting

### Models not loading?
- Ensure `models/` directory exists
- Run `train_models.py` to generate model files
- Check `model_metrics.json` for training metadata

### Predictions returning errors?
- Verify customer exists: `curl http://localhost:5002/api/customers`
- Check backend logs: `tail -f /tmp/xeno-backend.log`
- Ensure models are trained: `ls -la models/`

### Database issues?
- System automatically falls back to local MongoDB
- Check database connection: `curl http://localhost:5002/api/health`

## Technology Stack

- **Data Processing**: Pandas 2.0.3
- **ML Models**: scikit-learn 1.3.2
- **Database**: MongoDB (local) + mongomock fallback
- **Framework**: Flask 3.0.2
- **API**: RESTful JSON endpoints
