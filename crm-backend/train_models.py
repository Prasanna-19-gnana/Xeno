"""
Machine Learning Model Training
Trains ML models on shopping trends dataset for segmentation and prediction
"""
import pickle
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from models import customers_col, orders_col
import json

# Model storage paths
MODELS_DIR = './models'
import os
os.makedirs(MODELS_DIR, exist_ok=True)

def load_training_data():
    """Load customer and order data from database"""
    print("📊 Loading training data from database...")
    
    customers = list(customers_col.find())
    orders = list(orders_col.find())
    
    print(f"✅ Loaded {len(customers)} customers and {len(orders)} orders")
    
    # Create feature matrix
    features = []
    customer_ids = []
    
    for cust in customers:
        # Calculate features
        age = cust.get('age', 0)
        total_spend = cust.get('total_spend', 0)
        total_orders = cust.get('total_orders', 0)
        avg_order_value = total_spend / total_orders if total_orders > 0 else 0
        
        # Days since last order
        last_order = cust.get('last_order_date', '')
        if last_order:
            last_date = datetime.strptime(last_order, '%Y-%m-%d')
            days_since_order = (datetime.utcnow() - last_date).days
        else:
            days_since_order = 999
        
        # Subscription status (1 for yes, 0 for no)
        subscription = 1 if cust.get('subscription_status') == 'Yes' else 0
        
        # Gender encoding (Male=1, Female=0)
        gender = 1 if cust.get('gender') == 'Male' else 0
        
        # Review rating
        rating = float(cust.get('review_rating', 3.0))
        
        # Purchase frequency (convert to numeric)
        frequency_map = {
            'Weekly': 52, 'Fortnightly': 26, 'Bi-Weekly': 26, 
            'Monthly': 12, 'Quarterly': 4, 'Every 3 Months': 4, 'Annually': 1
        }
        freq_purchases = frequency_map.get(cust.get('purchase_frequency', 'Monthly'), 12)
        
        feature_vector = [
            age,
            total_spend,
            total_orders,
            avg_order_value,
            days_since_order,
            subscription,
            gender,
            rating,
            freq_purchases
        ]
        
        features.append(feature_vector)
        customer_ids.append(cust['_id'])
    
    X = np.array(features)
    return X, customer_ids, customers

def train_segmentation_model(X, customer_ids, customers):
    """Train customer segmentation model using K-means"""
    print("\n🎯 Training Customer Segmentation Model...")
    
    # Normalize features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Train K-means (4 segments: High-Value, Regular, At-Risk, New)
    kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
    segments = kmeans.fit_predict(X_scaled)
    
    # Save model
    with open(f'{MODELS_DIR}/segmentation_model.pkl', 'wb') as f:
        pickle.dump({'kmeans': kmeans, 'scaler': scaler}, f)
    
    # Map segments to names
    segment_names = {
        0: 'High-Value Customers',
        1: 'Regular Customers',
        2: 'At-Risk Customers',
        3: 'New Customers'
    }
    
    # Update database with segments
    segment_counts = {}
    for cust_id, segment in zip(customer_ids, segments):
        segment_name = segment_names[int(segment)]
        segment_counts[segment_name] = segment_counts.get(segment_name, 0) + 1
        
        customers_col.update_one(
            {'_id': cust_id},
            {'$set': {'segment': segment_name, 'segment_id': int(segment)}}
        )
    
    print("✅ Customer Segmentation Model trained successfully")
    for seg_name, count in segment_counts.items():
        print(f"   - {seg_name}: {count} customers")
    
    return kmeans, scaler, segment_names

def train_churn_model(X, customers):
    """Train customer churn prediction model"""
    print("\n🚨 Training Churn Prediction Model...")
    
    # Create target variable (1 if no order in 90 days, 0 otherwise)
    y_churn = []
    for cust in customers:
        last_order = cust.get('last_order_date', '')
        if last_order:
            last_date = datetime.strptime(last_order, '%Y-%m-%d')
            days_since = (datetime(2026, 6, 10) - last_date).days
            y_churn.append(1 if days_since > 90 else 0)
        else:
            y_churn.append(1)
    
    y_churn = np.array(y_churn)
    
    # Normalize features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Train Random Forest
    rf_churn = RandomForestClassifier(n_estimators=50, random_state=42)
    rf_churn.fit(X_scaled, y_churn)
    
    # Save model
    with open(f'{MODELS_DIR}/churn_model.pkl', 'wb') as f:
        pickle.dump({'model': rf_churn, 'scaler': scaler}, f)
    
    print("✅ Churn Prediction Model trained successfully")
    print(f"   - Churn rate: {np.mean(y_churn)*100:.1f}%")
    
    return rf_churn, scaler

def train_ltv_model(X, customers):
    """Train Lifetime Value prediction model"""
    print("\n💰 Training Lifetime Value (LTV) Model...")
    
    # Create target variable (total spend)
    y_ltv = np.array([c.get('total_spend', 0) for c in customers])
    
    # Normalize features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Train Random Forest Regressor
    rf_ltv = RandomForestRegressor(n_estimators=50, random_state=42)
    rf_ltv.fit(X_scaled, y_ltv)
    
    # Save model
    with open(f'{MODELS_DIR}/ltv_model.pkl', 'wb') as f:
        pickle.dump({'model': rf_ltv, 'scaler': scaler}, f)
    
    print("✅ Lifetime Value Model trained successfully")
    print(f"   - Average LTV: ${np.mean(y_ltv):,.2f}")
    print(f"   - Max LTV: ${np.max(y_ltv):,.2f}")
    
    return rf_ltv, scaler

def save_model_metrics(X, customer_ids, customers):
    """Save model metrics and stats"""
    print("\n📈 Computing Model Metrics...")
    
    metrics = {
        'trained_at': datetime.now().isoformat(),
        'total_customers': len(customers),
        'total_features': X.shape[1],
        'average_spend': float(np.mean([c.get('total_spend', 0) for c in customers])),
        'average_orders': float(np.mean([c.get('total_orders', 0) for c in customers])),
        'age_range': {
            'min': int(np.min(X[:, 0])),
            'max': int(np.max(X[:, 0])),
            'mean': float(np.mean(X[:, 0]))
        },
        'spend_range': {
            'min': int(np.min(X[:, 1])),
            'max': int(np.max(X[:, 1])),
            'mean': float(np.mean(X[:, 1]))
        }
    }
    
    with open(f'{MODELS_DIR}/model_metrics.json', 'w') as f:
        json.dump(metrics, f, indent=2)
    
    print("✅ Metrics saved")
    return metrics

def train_all_models():
    """Train all ML models on shopping trends dataset"""
    print("""
╔════════════════════════════════════════╗
║  🤖 ML Model Training Pipeline        ║
║  Shopping Trends Dataset              ║
╚════════════════════════════════════════╝
    """)
    
    # Load data
    X, customer_ids, customers = load_training_data()
    
    # Train models
    train_segmentation_model(X, customer_ids, customers)
    train_churn_model(X, customers)
    train_ltv_model(X, customers)
    
    # Save metrics
    metrics = save_model_metrics(X, customer_ids, customers)
    
    print(f"""
✅ All Models Trained Successfully!
   📊 Models saved to {MODELS_DIR}/
   📈 Metrics: {metrics}
    """)

if __name__ == "__main__":
    train_all_models()
