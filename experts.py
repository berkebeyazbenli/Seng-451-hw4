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
    print("✅ Model ve scaler başarıyla yüklendi.")
except FileNotFoundError as e:
    print(f"❌ Hata: model.pkl veya scaler.pkl dosyası bulunamadı! {e}")
except Exception as e:
    print(f"❌ Model yükleme hatası: {e}")

class KnowledgeSources:
    @staticmethod
    def ml_expert_module(input_data):
        """Uzman Modül 1: ML Analizi"""
        if ml_model is None or scaler is None:
            raise ValueError("Model veya scaler yüklenmemiş!")
        
        try:
            # Modelin beklediği sütun sırası (standart kalp hastalığı veri seti sırası)
            feature_order = ['age', 'sex', 'cp', 'trestbps', 'chol', 'fbs', 'restecg', 
                           'thalach', 'exang', 'oldpeak', 'slope', 'ca', 'thal']
            
            # Veriyi doğru sırayla DataFrame'e çevir
            ordered_data = {key: input_data.get(key, 0) for key in feature_order}
            df = pd.DataFrame([ordered_data], columns=feature_order)
            
            # Ölçeklendir ve tahmin yap
            scaled_data = scaler.transform(df)
            prediction = ml_model.predict(scaled_data)[0]
            probabilities = ml_model.predict_proba(scaled_data)[0]
            
            # Her iki sınıf için olasılıklar
            prob_healthy = round(float(probabilities[0]), 4)
            prob_patient = round(float(probabilities[1]), 4)
            
            # Feature importance bilgisi (en önemli 5 özellik)
            feature_importance = ml_model.feature_importances_
            feature_names = feature_order
            top_features = sorted(zip(feature_names, feature_importance), 
                                key=lambda x: x[1], reverse=True)[:5]
            
            # Güvenilirlik seviyesi
            confidence_level = "Yüksek" if max(probabilities) > 0.7 else "Orta" if max(probabilities) > 0.6 else "Düşük"
            
            return {
                "prediction": int(prediction),
                "probability": prob_patient,
                "probability_healthy": prob_healthy,
                "probability_patient": prob_patient,
                "result_text": "Hasta" if prediction == 1 else "Sağlıklı",
                "confidence_level": confidence_level,
                "top_features": [{"feature": feat, "importance": round(float(imp), 4)} 
                                for feat, imp in top_features],
                "model_type": "RandomForest",
                "n_estimators": ml_model.n_estimators if hasattr(ml_model, 'n_estimators') else None
            }
        except Exception as e:
            print(f"ML Expert Module Hatası: {e}")
            raise

    @staticmethod
    def clinical_expert_module(input_data):
        """Uzman Modül 2: Klinik Kurallar - Detaylı Risk Analizi (ML benzeri)"""
        findings = []
        risk_factors = []
        warnings = []
        risk_scores = {}  # Her faktör için risk skoru (0-100)
        
        age = input_data.get('age', 0)
        chol = input_data.get('chol', 0)
        trestbps = input_data.get('trestbps', 0)
        thalach = input_data.get('thalach', 0)
        cp = input_data.get('cp', 0)
        exang = input_data.get('exang', 0)
        oldpeak = input_data.get('oldpeak', 0)
        fbs = input_data.get('fbs', 0)
        restecg = input_data.get('restecg', 0)
        slope = input_data.get('slope', 1)
        ca = input_data.get('ca', 0)
        thal = input_data.get('thal', 2)
        
        cp_types = {0: "Asemptomatik", 1: "Tipik anjina", 2: "Atipik anjina", 3: "Non-anginal ağrı"}
        max_hr_expected = 220 - age if age > 0 else 150
        
        # ========== 1. KOLESTEROL ANALİZİ (Ağırlık: 15%) ==========
        chol_score = 0
        if chol > 240:
            chol_score = 90
            findings.append("Yüksek Kolesterol (>240 mg/dL)")
            risk_factors.append({"factor": "Kolesterol", "value": chol, "status": "Yüksek", "threshold": 240, "weight": 0.15, "score": chol_score})
        elif chol > 200:
            chol_score = 50
            warnings.append(f"Kolesterol sınırda ({chol} mg/dL)")
            risk_factors.append({"factor": "Kolesterol", "value": chol, "status": "Sınırda", "threshold": 200, "weight": 0.15, "score": chol_score})
        else:
            chol_score = 10
            risk_factors.append({"factor": "Kolesterol", "value": chol, "status": "Normal", "threshold": 200, "weight": 0.15, "score": chol_score})
        risk_scores['cholesterol'] = chol_score
        
        # ========== 2. KAN BASINCI ANALİZİ (Ağırlık: 15%) ==========
        bp_score = 0
        if trestbps > 140:
            bp_score = 90
            findings.append("Yüksek Kan Basıncı (>140 mmHg)")
            risk_factors.append({"factor": "Kan Basıncı", "value": trestbps, "status": "Yüksek", "threshold": 140, "weight": 0.15, "score": bp_score})
        elif trestbps > 120:
            bp_score = 50
            warnings.append(f"Kan basıncı sınırda ({trestbps} mmHg)")
            risk_factors.append({"factor": "Kan Basıncı", "value": trestbps, "status": "Sınırda", "threshold": 120, "weight": 0.15, "score": bp_score})
        else:
            bp_score = 10
            risk_factors.append({"factor": "Kan Basıncı", "value": trestbps, "status": "Normal", "threshold": 120, "weight": 0.15, "score": bp_score})
        risk_scores['blood_pressure'] = bp_score
        
        # ========== 3. YAŞ RİSK ANALİZİ (Ağırlık: 10%) ==========
        age_score = 0
        if age > 65:
            age_score = 80
            risk_factors.append({"factor": "Yaş", "value": age, "status": "Yüksek Risk", "threshold": 65, "weight": 0.10, "score": age_score})
        elif age > 45:
            age_score = 40
            risk_factors.append({"factor": "Yaş", "value": age, "status": "Orta Risk", "threshold": 45, "weight": 0.10, "score": age_score})
        else:
            age_score = 10
            risk_factors.append({"factor": "Yaş", "value": age, "status": "Düşük Risk", "threshold": 45, "weight": 0.10, "score": age_score})
        risk_scores['age'] = age_score
        
        # ========== 4. GÖĞÜS AĞRISI ANALİZİ (Ağırlık: 20%) ==========
        cp_score = 0
        if cp == 0:
            cp_score = 5
        elif cp == 1:  # Tipik anjina - en yüksek risk
            cp_score = 95
            findings.append(f"Göğüs ağrısı: {cp_types.get(cp)}")
            risk_factors.append({"factor": "Göğüs Ağrısı", "value": cp_types.get(cp), "status": "Yüksek Risk", "threshold": "Yok", "weight": 0.20, "score": cp_score})
        elif cp == 2:  # Atipik anjina
            cp_score = 70
            findings.append(f"Göğüs ağrısı: {cp_types.get(cp)}")
            risk_factors.append({"factor": "Göğüs Ağrısı", "value": cp_types.get(cp), "status": "Orta-Yüksek Risk", "threshold": "Yok", "weight": 0.20, "score": cp_score})
        elif cp == 3:  # Non-anginal
            cp_score = 40
            findings.append(f"Göğüs ağrısı: {cp_types.get(cp)}")
            risk_factors.append({"factor": "Göğüs Ağrısı", "value": cp_types.get(cp), "status": "Orta Risk", "threshold": "Yok", "weight": 0.20, "score": cp_score})
        risk_scores['chest_pain'] = cp_score
        
        # ========== 5. EGZERSİZ ANJİNASI (Ağırlık: 15%) ==========
        exang_score = 0
        if exang == 1:
            exang_score = 85
            findings.append("Egzersiz anjinası mevcut")
            risk_factors.append({"factor": "Egzersiz Anjinası", "value": "Var", "status": "Yüksek Risk", "threshold": "Yok", "weight": 0.15, "score": exang_score})
        else:
            exang_score = 10
            risk_factors.append({"factor": "Egzersiz Anjinası", "value": "Yok", "status": "Normal", "threshold": "Yok", "weight": 0.15, "score": exang_score})
        risk_scores['exercise_angina'] = exang_score
        
        # ========== 6. ST DEPRESYONU (Ağırlık: 15%) ==========
        st_score = 0
        if oldpeak > 2:
            st_score = 90
            findings.append(f"Ciddi ST depresyonu ({oldpeak} mm)")
            risk_factors.append({"factor": "ST Depresyonu", "value": oldpeak, "status": "Yüksek Risk", "threshold": 2, "weight": 0.15, "score": st_score})
        elif oldpeak > 1:
            st_score = 60
            warnings.append(f"ST depresyonu mevcut ({oldpeak} mm)")
            risk_factors.append({"factor": "ST Depresyonu", "value": oldpeak, "status": "Orta Risk", "threshold": 1, "weight": 0.15, "score": st_score})
        else:
            st_score = 10
            risk_factors.append({"factor": "ST Depresyonu", "value": oldpeak, "status": "Normal", "threshold": 1, "weight": 0.15, "score": st_score})
        risk_scores['st_depression'] = st_score
        
        # ========== 7. MAKSİMUM KALP ATIŞ HIZI (Ağırlık: 5%) ==========
        hr_score = 0
        if thalach < max_hr_expected * 0.5:
            hr_score = 70
            warnings.append(f"Düşük maksimum kalp atış hızı ({thalach} bpm, beklenen: ~{max_hr_expected} bpm)")
            risk_factors.append({"factor": "Maks. Kalp Atış Hızı", "value": thalach, "status": "Düşük", "threshold": max_hr_expected * 0.5, "weight": 0.05, "score": hr_score})
        elif thalach < max_hr_expected * 0.7:
            hr_score = 30
            risk_factors.append({"factor": "Maks. Kalp Atış Hızı", "value": thalach, "status": "Sınırda", "threshold": max_hr_expected * 0.7, "weight": 0.05, "score": hr_score})
        else:
            hr_score = 10
            risk_factors.append({"factor": "Maks. Kalp Atış Hızı", "value": thalach, "status": "Normal", "threshold": max_hr_expected * 0.7, "weight": 0.05, "score": hr_score})
        risk_scores['heart_rate'] = hr_score
        
        # ========== 8. DİYABET (FBS) (Ağırlık: 5%) ==========
        fbs_score = 0
        if fbs == 1:
            fbs_score = 60
            findings.append("Açlık kan şekeri yüksek (>120 mg/dL)")
            risk_factors.append({"factor": "Açlık Kan Şekeri", "value": "Yüksek", "status": "Risk Faktörü", "threshold": "Normal", "weight": 0.05, "score": fbs_score})
        else:
            fbs_score = 10
            risk_factors.append({"factor": "Açlık Kan Şekeri", "value": "Normal", "status": "Normal", "threshold": "Normal", "weight": 0.05, "score": fbs_score})
        risk_scores['fbs'] = fbs_score
        
        # ========== TOPLAM RİSK SKORU HESAPLAMA ==========
        # Ağırlıklı ortalama ile toplam risk skoru (0-100)
        total_risk_score = (
            chol_score * 0.15 +
            bp_score * 0.15 +
            age_score * 0.10 +
            cp_score * 0.20 +
            exang_score * 0.15 +
            st_score * 0.15 +
            hr_score * 0.05 +
            fbs_score * 0.05
        )
        
        # Risk seviyesi belirleme (ML benzeri)
        if total_risk_score >= 70:
            risk_level = "Yüksek Risk"
            risk_level_confidence = "Yüksek"
        elif total_risk_score >= 40:
            risk_level = "Orta Risk"
            risk_level_confidence = "Orta"
        else:
            risk_level = "Düşük Risk"
            risk_level_confidence = "Yüksek"
        
        # Risk faktörü sayısı
        high_risk_count = len([rf for rf in risk_factors if rf.get('score', 0) >= 70])
        medium_risk_count = len([rf for rf in risk_factors if 40 <= rf.get('score', 0) < 70])
        
        # En önemli risk faktörleri (ML'deki top_features gibi)
        top_risk_factors = sorted(
            [{"factor": rf['factor'], "score": rf['score'], "weight": rf['weight'], "contribution": round(rf['score'] * rf['weight'], 2)} 
             for rf in risk_factors],
            key=lambda x: x['contribution'],
            reverse=True
        )[:5]
        
        return {
            "risk_score": risk_level,
            "risk_score_numeric": round(total_risk_score, 2),  # 0-100 arası sayısal skor
            "risk_score_percentage": round(total_risk_score, 1),  # Yüzde olarak
            "risk_level_confidence": risk_level_confidence,  # ML'deki confidence_level gibi
            "details": findings,
            "warnings": warnings,
            "risk_factors": risk_factors,
            "risk_scores": risk_scores,  # Her faktörün skoru
            "total_risk_factors": len([f for f in findings if "Yüksek" in f or "Ciddi" in f]),
            "high_risk_factors_count": high_risk_count,
            "medium_risk_factors_count": medium_risk_count,
            "top_risk_factors": top_risk_factors,  # ML'deki top_features gibi
            "patient_age": age,
            "patient_data_summary": {
                "age": age,
                "blood_pressure": trestbps,
                "cholesterol": chol,
                "max_heart_rate": thalach,
                "chest_pain_type": cp_types.get(cp, "Bilinmeyen"),
                "exercise_angina": "Var" if exang == 1 else "Yok",
                "st_depression": oldpeak,
                "fasting_blood_sugar": "Yüksek" if fbs == 1 else "Normal"
            }
        }