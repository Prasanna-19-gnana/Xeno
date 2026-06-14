"""
ML Predictions Route
Uses trained models for customer segmentation and churn/LTV predictions
"""
from flask import Blueprint, request, jsonify
import pickle
import numpy as np
from datetime import datetime
from models import customers_col

ml_bp = Blueprint('ml', __name__)

def load_models():
    """Load trained models from disk"""
    try:
        with open('models/segmentation_model.pkl', 'rb') as f:
            seg_data = pickle.load(f)
        with open('models/churn_model.pkl', 'rb') as f:
            churn_data = pickle.load(f)
        with open('models/ltv_model.pkl', 'rb') as f:
            ltv_data = pickle.load(f)
        return seg_data, churn_data, ltv_data
    except Exception as e:
        print(f"❌ Error loading models: {e}")
        return None, None, None

def prepare_features(customer):
    """Prepare feature vector from customer data"""
    age = customer.get('age', 0)
    total_spend = customer.get('total_spend', 0)
    total_orders = customer.get('total_orders', 0)
    avg_order_value = total_spend / total_orders if total_orders > 0 else 0
    
    # Days since last order
    last_order = customer.get('last_order_date', '')
    if last_order:
        last_date = datetime.strptime(last_order, '%Y-%m-%d')
        days_since_order = (datetime.utcnow() - last_date).days
    else:
        days_since_order = 999
    
    # Subscription status (1 for yes, 0 for no)
    subscription = 1 if customer.get('subscription_status') == 'Yes' else 0
    
    # Gender encoding (Male=1, Female=0)
    gender = 1 if customer.get('gender') == 'Male' else 0
    
    # Review rating
    rating = float(customer.get('review_rating', 3.0))
    
    # Purchase frequency
    frequency_map = {
        'Weekly': 52, 'Fortnightly': 26, 'Bi-Weekly': 26, 
        'Monthly': 12, 'Quarterly': 4, 'Every 3 Months': 4, 'Annually': 1
    }
    freq_purchases = frequency_map.get(customer.get('purchase_frequency', 'Monthly'), 12)
    
    return np.array([[
        age, total_spend, total_orders, avg_order_value, 
        days_since_order, subscription, gender, rating, freq_purchases
    ]])

@ml_bp.route('/api/ml/predict/segment/<customer_id>', methods=['GET'])
def predict_customer_segment(customer_id):
    """Predict customer segment for a given customer"""
    try:
        seg_data, _, _ = load_models()
        if seg_data is None:
            return jsonify({"status": "error", "message": "Models not trained yet"}), 503
        
        customer = customers_col.find_one({'_id': customer_id})
        if not customer:
            return jsonify({"status": "error", "message": "Customer not found"}), 404
        
        X = prepare_features(customer)
        X_scaled = seg_data['scaler'].transform(X)
        segment_id = int(seg_data['kmeans'].predict(X_scaled)[0])
        
        segment_names = {
            0: 'High-Value Customers',
            1: 'Regular Customers',
            2: 'At-Risk Customers',
            3: 'New Customers'
        }
        
        segment_name = segment_names[segment_id]
        
        # Get segment characteristics
        segment_chars = {
            'High-Value Customers': 'High spending, frequent purchases, low churn risk',
            'Regular Customers': 'Moderate spending, regular purchases, stable',
            'At-Risk Customers': 'Low recent activity, potential churn candidates',
            'New Customers': 'New to platform, limited purchase history'
        }
        
        return jsonify({
            "status": "success",
            "customer_id": customer_id,
            "segment": segment_name,
            "segment_id": segment_id,
            "description": segment_chars.get(segment_name, ''),
            "customer_data": {
                "name": customer.get('name'),
                "spend": customer.get('total_spend'),
                "orders": customer.get('total_orders'),
                "age": customer.get('age')
            }
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@ml_bp.route('/api/ml/predict/churn/<customer_id>', methods=['GET'])
def predict_churn(customer_id):
    """Predict churn probability for a customer"""
    try:
        _, churn_data, _ = load_models()
        if churn_data is None:
            return jsonify({"status": "error", "message": "Models not trained yet"}), 503
        
        customer = customers_col.find_one({'_id': customer_id})
        if not customer:
            return jsonify({"status": "error", "message": "Customer not found"}), 404
        
        X = prepare_features(customer)
        X_scaled = churn_data['scaler'].transform(X)
        
        churn_pred = churn_data['model'].predict(X_scaled)[0]
        churn_prob = churn_data['model'].predict_proba(X_scaled)[0]
        
        churn_risk = float(max(churn_prob))
        
        # Recommend actions
        if churn_risk > 0.7:
            recommendation = "High priority: Send personalized offer or loyalty reward"
        elif churn_risk > 0.4:
            recommendation = "Medium priority: Engage with special campaign"
        else:
            recommendation = "Low risk: Maintain standard engagement"
        
        return jsonify({
            "status": "success",
            "customer_id": customer_id,
            "churn_probability": churn_risk,
            "churn_risk_level": "High" if churn_risk > 0.7 else "Medium" if churn_risk > 0.4 else "Low",
            "recommendation": recommendation
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@ml_bp.route('/api/ml/predict/ltv/<customer_id>', methods=['GET'])
def predict_ltv(customer_id):
    """Predict Lifetime Value for a customer"""
    try:
        _, _, ltv_data = load_models()
        if ltv_data is None:
            return jsonify({"status": "error", "message": "Models not trained yet"}), 503
        
        customer = customers_col.find_one({'_id': customer_id})
        if not customer:
            return jsonify({"status": "error", "message": "Customer not found"}), 404
        
        X = prepare_features(customer)
        X_scaled = ltv_data['scaler'].transform(X)
        
        predicted_ltv = float(ltv_data['model'].predict(X_scaled)[0])
        current_ltv = float(customer.get('total_spend', 0))
        
        return jsonify({
            "status": "success",
            "customer_id": customer_id,
            "current_ltv": current_ltv,
            "predicted_ltv": round(predicted_ltv, 2),
            "potential_growth": round(predicted_ltv - current_ltv, 2),
            "confidence": "High" if abs(predicted_ltv - current_ltv) < 20 else "Medium"
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@ml_bp.route('/api/ml/bulk-predict', methods=['POST'])
def bulk_predict():
    """Predict segments for multiple customers"""
    try:
        data = request.json
        limit = data.get('limit', 50)
        
        seg_data, _, _ = load_models()
        if seg_data is None:
            return jsonify({"status": "error", "message": "Models not trained yet"}), 503
        
        segment_names = {
            0: 'High-Value Customers',
            1: 'Regular Customers',
            2: 'At-Risk Customers',
            3: 'New Customers'
        }
        
        # Get customers and predict
        customers = list(customers_col.find().limit(limit))
        predictions = []
        
        for customer in customers:
            X = prepare_features(customer)
            X_scaled = seg_data['scaler'].transform(X)
            segment_id = int(seg_data['kmeans'].predict(X_scaled)[0])
            
            predictions.append({
                "customer_id": customer['_id'],
                "name": customer.get('name'),
                "segment": segment_names[segment_id],
                "spend": customer.get('total_spend')
            })
        
        return jsonify({
            "status": "success",
            "total": len(predictions),
            "predictions": predictions
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
