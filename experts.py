import pickle
import pandas as pd
import numpy as np

# Modelleri yükle
ml_model = None
scaler = None
try:
    with open('model.pkl', 'rb') as f:
        ml_model = pickle.load(f)
    with open('scaler.pkl', 'rb') as f:
        scaler = pickle.load(f)
except Exception as e:
    print(f"Model yükleme hatası: {e}")

class KnowledgeSources:
    @staticmethod
    def ml_expert_module(input_data):
        """Uzman Modül 1: ML Analizi"""
        if ml_model is None or scaler is None:
            raise ValueError("Model veya scaler yüklenmemiş!")
        
        feature_order = ['age', 'sex', 'cp', 'trestbps', 'chol', 'fbs', 'restecg', 
                         'thalach', 'exang', 'oldpeak', 'slope', 'ca', 'thal']
        
        ordered_data = {key: input_data.get(key, 0) for key in feature_order}
        df = pd.DataFrame([ordered_data], columns=feature_order)
        
        scaled_data = scaler.transform(df)
        prediction = ml_model.predict(scaled_data)[0]
        probabilities = ml_model.predict_proba(scaled_data)[0]
        
        # IMPORTANT: In this dataset/model setup, 1=Healthy and 0=Patient
        result_text = "Healthy" if prediction == 1 else "Patient"
        prob_patient = round(float(probabilities[0]), 4)  # class 0 probability (Patient)
        prob_healthy = round(float(probabilities[1]), 4)  # class 1 probability (Healthy)
        
        feature_importance = ml_model.feature_importances_
        top_features = sorted(zip(feature_order, feature_importance), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            "prediction": int(prediction),
            "probability": prob_patient,
            "probability_patient": prob_patient,
            "probability_healthy": prob_healthy,
            "result_text": result_text,
            "confidence_level": (
                "High"
                if max(probabilities) > 0.7
                else "Medium"
                if max(probabilities) > 0.6
                else "Low"
            ),
            "model_type": "RandomForest",
            "top_features": [{"feature": feat, "importance": round(float(imp), 4)} for feat, imp in top_features]
        }

    @staticmethod
    def clinical_expert_module(input_data):
        """Expert Module 2: Enhanced clinical analysis (rule-based)"""
        findings, risk_factors = [], []
        risk_scores = {}
        
        # Verileri al
        age = input_data.get('age', 0)
        sex = input_data.get('sex', 1)
        chol = input_data.get('chol', 0)
        trestbps = input_data.get('trestbps', 0)
        thalach = input_data.get('thalach', 0)
        cp = input_data.get('cp', 0)
        exang = input_data.get('exang', 0)
        oldpeak = input_data.get('oldpeak', 0)
        ca = input_data.get('ca', 0)
        thal = input_data.get('thal', 2)

        # 1) Coronary vessel blockage (CA) analysis (Weight: 25% - most critical)
        ca_score = 10 if ca == 0 else (60 if ca == 1 else 95)
        if ca > 0:
            findings.append(f"Angiography suggests {ca} blocked vessel(s) / calcification")
        risk_factors.append({"factor": "Blocked vessels (CA)", "score": ca_score, "weight": 0.25})

        # 2) Thalassemia / blood flow (THAL) analysis (Weight: 15%)
        # In this dataset: 3 (reversible defect) is high risk, 2 is normal.
        thal_score = 90 if thal == 3 else 15
        if thal == 3:
            findings.append("Thal test: reversible defect (high risk)")
        risk_factors.append({"factor": "Thalassemia (THAL)", "score": thal_score, "weight": 0.15})

        # 3) Chest pain type (CP) (Weight: 15%)
        cp_score = 5 if cp == 3 else (80 if cp == 0 else 40)
        risk_factors.append({"factor": "Chest pain type (CP)", "score": cp_score, "weight": 0.15})

        # 4) ST depression (OLDPEAK) (Weight: 15%)
        st_score = 95 if oldpeak > 2.0 else (50 if oldpeak > 1.0 else 10)
        risk_factors.append({"factor": "ST depression (oldpeak)", "score": st_score, "weight": 0.15})

        # 5) Other (age, blood pressure, cholesterol) (Weight: 30%)
        other_score = (chol > 240 or trestbps > 140 or age > 60) * 70 or 20
        risk_factors.append({"factor": "Lifestyle / demographics", "score": other_score, "weight": 0.30})

        # Total score
        total_risk = sum(rf['score'] * rf['weight'] for rf in risk_factors)
        risk_level = "High risk" if total_risk > 65 else ("Medium risk" if total_risk > 35 else "Low risk")
        
        return {
            "risk_score": risk_level,
            "risk_score_numeric": round(total_risk, 2),
            "details": findings,
            "top_risk_factors": [
                {
                    **rf,
                    "contribution": round(float(rf.get("score", 0)) * float(rf.get("weight", 0)), 4),
                }
                for rf in sorted(risk_factors, key=lambda x: x["score"] * x["weight"], reverse=True)[:3]
            ],
            "patient_data_summary": input_data
        }