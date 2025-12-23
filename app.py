import streamlit as st
import requests
import psycopg2
import time
import json
import pandas as pd
import os

# Streamlit Cloud secrets veya environment variables'dan oku
try:
    # Streamlit Cloud secrets
    DB_HOST = st.secrets.get("DB_HOST", os.getenv("DB_HOST", "database-1.c814i00i8t9k.us-east-1.rds.amazonaws.com"))
    DB_NAME = st.secrets.get("DB_NAME", os.getenv("DB_NAME", "postgres"))
    DB_USER = st.secrets.get("DB_USER", os.getenv("DB_USER", "postgres"))
    DB_PASSWORD = st.secrets.get("DB_PASSWORD", os.getenv("DB_PASSWORD", "Bekobeko42"))
    BACKEND_URL = st.secrets.get("BACKEND_URL", os.getenv("BACKEND_URL", "http://localhost:8000"))
except:
    # Fallback to environment variables
    DB_HOST = os.getenv("DB_HOST", "database-1.c814i00i8t9k.us-east-1.rds.amazonaws.com")
    DB_NAME = os.getenv("DB_NAME", "postgres")
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "Bekobeko42")
    BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

st.set_page_config(page_title="Grup-17 Blackboard Diagnosis", layout="wide")
st.title("🩺 Kalp Teşhis Destek Sistemi (Group-17)")

# Form Alanları
with st.sidebar:
    st.header("Hasta Veri Girişi")
    age = st.number_input("Yaş", 1, 100, 45)
    trestbps = st.number_input("Kan Basıncı", 80, 200, 120)
    chol = st.number_input("Kolesterol", 100, 500, 210)
    cp = st.selectbox("Göğüs Ağrısı Tipi", [0, 1, 2, 3])
    thalach = st.number_input("Maks. Kalp Atış Hızı", 60, 220, 150)
    # Diğerleri varsayılan
    patient_data = {"age": age, "trestbps": trestbps, "chol": chol, "cp": cp, "thalach": thalach, "sex": 1, "fbs": 0, "restecg": 0, "exang": 0, "oldpeak": 1.0, "slope": 1, "ca": 0, "thal": 2}

if st.sidebar.button("Teşhis Koy"):
    try:
        res = requests.post(f"{BACKEND_URL}/submit-patient", json=patient_data)
        if res.status_code == 200:
            record_id = res.json()["id"]
            st.success(f"✅ Hasta kaydı oluşturuldu (ID: {record_id})")
            
            # Polling: Status COMPLETED veya ERROR olana kadar bekle
            with st.spinner("Uzmanlar tahtayı güncelliyor..."):
                max_attempts = 30  # Maksimum 30 deneme (15 saniye)
                attempt = 0
                status = "PENDING"
                
                while status not in ["COMPLETED", "ERROR"] and attempt < max_attempts:
                    time.sleep(0.5)  # 0.5 saniye bekle
                    attempt += 1
                    
                    try:
                        conn = psycopg2.connect(
                            host=DB_HOST,
                            database=DB_NAME,
                            user=DB_USER,
                            password=DB_PASSWORD
                        )
                        cur = conn.cursor()
                        cur.execute(
                            "SELECT ml_analysis, clinical_analysis, status FROM heart_blackboard WHERE id = %s",
                            (record_id,)
                        )
                        row = cur.fetchone()
                        conn.close()
                        
                        if row:
                            status = row[2] if row[2] else "PENDING"
                            
                            # Hata durumu kontrolü
                            if status == "ERROR":
                                error_info = {}
                                if row[0]:
                                    try:
                                        error_info = json.loads(row[0]) if isinstance(row[0], str) else row[0]
                                    except:
                                        error_info = {"error": "Bilinmeyen hata"}
                                st.error(f"❌ Analiz sırasında hata oluştu: {error_info.get('error', 'Bilinmeyen hata')}")
                                break
                            
                            # Eğer tamamlandıysa sonuçları göster
                            if status == "COMPLETED" and row[0] and row[1]:
                                # JSON string'leri parse et
                                ml_analysis = json.loads(row[0]) if isinstance(row[0], str) else row[0]
                                clinical_analysis = json.loads(row[1]) if isinstance(row[1], str) else row[1]
                                
                                st.success("🎉 Analiz tamamlandı!")
                                
                                # Ana sonuçlar
                                c1, c2 = st.columns(2)
                                with c1:
                                    st.markdown("### 🤖 ML Analiz Sonuçları")
                                    result_color = "🔴" if ml_analysis['result_text'] == "Hasta" else "🟢"
                                    st.markdown(f"**Sonuç:** {result_color} {ml_analysis['result_text']}")
                                    
                                    # Olasılık bilgileri
                                    prob_patient = ml_analysis.get('probability_patient', ml_analysis.get('probability', 0))
                                    prob_healthy = ml_analysis.get('probability_healthy', 1 - prob_patient)
                                    
                                    st.progress(prob_patient)
                                    st.caption(f"**Hasta Olasılığı:** %{prob_patient*100:.2f}")
                                    st.caption(f"**Sağlıklı Olasılığı:** %{prob_healthy*100:.2f}")
                                    
                                    # Güvenilirlik seviyesi
                                    confidence = ml_analysis.get('confidence_level', 'Orta')
                                    confidence_icon = "🟢" if confidence == "Yüksek" else "🟡" if confidence == "Orta" else "🔴"
                                    st.info(f"**Güvenilirlik:** {confidence_icon} {confidence}")
                                    
                                    # En önemli özellikler
                                    if ml_analysis.get('top_features'):
                                        st.markdown("**En Önemli Özellikler:**")
                                        for feat in ml_analysis['top_features']:
                                            st.caption(f"• {feat['feature']}: {feat['importance']*100:.2f}%")
                                
                                with c2:
                                    st.markdown("### 🏥 Klinik Analiz Sonuçları")
                                    risk_score = clinical_analysis.get('risk_score', 'Normal')
                                    risk_score_numeric = clinical_analysis.get('risk_score_numeric', 0)
                                    risk_score_percentage = clinical_analysis.get('risk_score_percentage', 0)
                                    
                                    risk_icon = "🔴" if "Yüksek" in risk_score else "🟡" if "Orta" in risk_score else "🟢"
                                    st.markdown(f"**Risk Seviyesi:** {risk_icon} {risk_score}")
                                    
                                    # Risk skoru progress bar (ML'deki gibi)
                                    st.progress(risk_score_numeric / 100)
                                    st.caption(f"**Risk Skoru:** {risk_score_percentage}/100")
                                    
                                    # Güvenilirlik seviyesi (ML'deki gibi)
                                    confidence = clinical_analysis.get('risk_level_confidence', 'Orta')
                                    confidence_icon = "🟢" if confidence == "Yüksek" else "🟡" if confidence == "Orta" else "🔴"
                                    st.info(f"**Güvenilirlik:** {confidence_icon} {confidence}")
                                    
                                    # Risk faktörleri sayıları
                                    high_risks = clinical_analysis.get('high_risk_factors_count', 0)
                                    medium_risks = clinical_analysis.get('medium_risk_factors_count', 0)
                                    st.caption(f"**Yüksek Risk Faktörü:** {high_risks} | **Orta Risk Faktörü:** {medium_risks}")
                                    
                                    # En önemli risk faktörleri (ML'deki top_features gibi)
                                    if clinical_analysis.get('top_risk_factors'):
                                        st.markdown("**En Önemli Risk Faktörleri:**")
                                        for rf in clinical_analysis['top_risk_factors']:
                                            st.caption(f"• {rf['factor']}: {rf['contribution']:.2f} puan (ağırlık: {rf['weight']*100:.0f}%)")
                                    
                                    # Bulgular
                                    if clinical_analysis.get('details'):
                                        st.markdown("**Bulgular:**")
                                        for detail in clinical_analysis['details']:
                                            st.warning(f"⚠️ {detail}")
                                    
                                    # Uyarılar
                                    if clinical_analysis.get('warnings'):
                                        st.markdown("**Uyarılar:**")
                                        for warning in clinical_analysis['warnings']:
                                            st.info(f"ℹ️ {warning}")
                                
                                # Detaylı bilgiler için expander
                                with st.expander("📊 Detaylı Analiz Bilgileri", expanded=False):
                                    col1, col2 = st.columns(2)
                                    
                                    with col1:
                                        st.markdown("#### ML Model Detayları")
                                        st.json({
                                            "Model Tipi": ml_analysis.get('model_type', 'N/A'),
                                            "Tahmin": ml_analysis.get('prediction', 'N/A'),
                                            "Sonuç": ml_analysis.get('result_text', 'N/A'),
                                            "Hasta Olasılığı": f"%{prob_patient*100:.4f}",
                                            "Sağlıklı Olasılığı": f"%{prob_healthy*100:.4f}",
                                            "Güvenilirlik": ml_analysis.get('confidence_level', 'N/A')
                                        })
                                    
                                    with col2:
                                        st.markdown("#### Klinik Veri Özeti")
                                        patient_summary = clinical_analysis.get('patient_data_summary', {})
                                        st.json(patient_summary)
                                
                                # Risk faktörleri tablosu (detaylı)
                                if clinical_analysis.get('risk_factors'):
                                    st.markdown("### 📋 Risk Faktörleri Analizi")
                                    risk_df_data = []
                                    for rf in clinical_analysis['risk_factors']:
                                        risk_df_data.append({
                                            "Faktör": rf.get('factor', 'N/A'),
                                            "Değer": rf.get('value', 'N/A'),
                                            "Durum": rf.get('status', 'N/A'),
                                            "Risk Skoru": f"{rf.get('score', 0):.0f}/100",
                                            "Ağırlık": f"%{rf.get('weight', 0)*100:.0f}",
                                            "Katkı": f"{rf.get('score', 0) * rf.get('weight', 0):.2f}",
                                            "Eşik Değer": rf.get('threshold', 'N/A')
                                        })
                                    if risk_df_data:
                                        # Arrow/pyarrow serialization can fail when a column mixes types
                                        # (e.g. "Değer" being both numbers and strings like "Yok").
                                        risk_df = pd.DataFrame(risk_df_data).astype(str)
                                        st.dataframe(risk_df, width="stretch", hide_index=True)
                                
                                # Risk skorları detayı (ML'deki gibi)
                                if clinical_analysis.get('risk_scores'):
                                    with st.expander("📈 Risk Skorları Detayı", expanded=False):
                                        st.markdown("#### Her Faktörün Risk Skoru (0-100)")
                                        risk_scores_data = clinical_analysis.get('risk_scores', {})
                                        for factor, score in risk_scores_data.items():
                                            factor_name = {
                                                'cholesterol': 'Kolesterol',
                                                'blood_pressure': 'Kan Basıncı',
                                                'age': 'Yaş',
                                                'chest_pain': 'Göğüs Ağrısı',
                                                'exercise_angina': 'Egzersiz Anjinası',
                                                'st_depression': 'ST Depresyonu',
                                                'heart_rate': 'Kalp Atış Hızı',
                                                'fbs': 'Açlık Kan Şekeri'
                                            }.get(factor, factor)
                                            st.progress(score / 100)
                                            st.caption(f"**{factor_name}:** {score:.0f}/100")
                                
                                break
                    except Exception as db_error:
                        st.error(f"Veritabanı hatası: {db_error}")
                        break
                
                if status == "PENDING":
                    st.warning("⏳ Analiz henüz tamamlanmadı. Lütfen birkaç saniye sonra tekrar deneyin.")
        else:
            st.error(f"❌ Hata: {res.status_code} - {res.text}")
    except requests.exceptions.ConnectionError:
        st.error("❌ Backend servisine bağlanılamadı. Lütfen FastAPI sunucusunun çalıştığından emin olun.")
    except Exception as e:
        st.error(f"❌ Beklenmeyen hata: {str(e)}")