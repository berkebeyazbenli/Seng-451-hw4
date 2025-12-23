import streamlit as st
import requests
import psycopg2
import time
import json
import pandas as pd
import os

# Read from Streamlit Cloud secrets or environment variables
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

st.set_page_config(page_title="Group-17 Blackboard Diagnosis", layout="wide")
st.title("🩺 Heart Disease Decision Support (Group-17)")

# Sidebar form
with st.sidebar:
    st.header("📋 Patient Input")
    age = st.number_input(
        "Age",
        min_value=18,
        max_value=100,
        value=45,
        help="Adult age range is typically used in clinical screening (18–100).",
    )
    sex = st.selectbox(
        "Sex",
        [0, 1],
        format_func=lambda x: "Male" if x == 1 else "Female",
        help="0: Female, 1: Male (dataset encoding).",
    )
    trestbps = st.number_input(
        "Resting blood pressure (mmHg)",
        min_value=40,
        max_value=250,
        value=120,
        help="Systolic blood pressure. Wide but realistic range (40–250).",
    )
    chol = st.number_input(
        "Serum cholesterol (mg/dL)",
        min_value=80,
        max_value=600,
        value=210,
        help="Total cholesterol. Wide but realistic range (80–600).",
    )
    cp = st.selectbox(
        "Chest pain type (CP)",
        [0, 1, 2, 3],
        help="0: Asymptomatic, 1: Typical angina, 2: Atypical angina, 3: Non-anginal pain.",
    )
    thalach = st.number_input(
        "Max heart rate achieved (bpm)",
        min_value=40,
        max_value=220,
        value=170,
        help="Peak heart rate during exercise test. Realistic range (40–220).",
    )
    exang = st.selectbox(
        "Exercise-induced angina (EXANG)",
        [0, 1],
        format_func=lambda x: "Yes" if x == 1 else "No",
        help="Whether angina occurs during exercise. 0: No, 1: Yes.",
    )
    oldpeak = st.number_input(
        "Oldpeak (ST depression)",
        min_value=0.0,
        max_value=6.0,
        value=0.0,
        step=0.1,
        help="ST depression induced by exercise relative to rest (typically 0.0–6.0).",
    )
    
    with st.expander("🛠️ Advanced settings (optional)"):
        st.caption("If you are unsure, keep the defaults.")
        slope = st.selectbox(
            "ST segment slope (SLOPE)",
            [0, 1, 2],
            index=2,
            help="Slope of the peak exercise ST segment (dataset encoding: 0/1/2).",
        )
        ca = st.selectbox(
            "Number of major vessels (CA)",
            [0, 1, 2, 3, 4],
            index=0,
            help="Number of major vessels colored by fluoroscopy (0–4).",
        )
        thal = st.selectbox(
            "Thalassemia (THAL)",
            [0, 1, 2, 3],
            index=2,
            help="Thalassemia test result (dataset encoding: 0/1/2/3).",
        )
        fbs = st.selectbox(
            "Fasting blood sugar > 120 mg/dL (FBS)",
            [0, 1],
            index=0,
            help="0: No, 1: Yes.",
        )
        restecg = st.selectbox(
            "Resting ECG (RESTECG)",
            [0, 1, 2],
            index=0,
            help="Resting electrocardiographic results (dataset encoding: 0/1/2).",
        )

    patient_data = {
        "age": age, "sex": sex, "cp": cp, "trestbps": trestbps, "chol": chol, 
        "fbs": fbs, "restecg": restecg, "thalach": thalach, "exang": exang, 
        "oldpeak": oldpeak, "slope": slope, "ca": ca, "thal": thal
    }

if st.sidebar.button("Run diagnosis"):
    try:
        res = requests.post(f"{BACKEND_URL}/submit-patient", json=patient_data)
        if res.status_code == 200:
            record_id = res.json()["id"]
            st.success(f"✅ Patient record created (ID: {record_id})")
            
            # Polling: Status COMPLETED veya ERROR olana kadar bekle
            with st.spinner("Experts are updating the blackboard..."):
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
                                        error_info = {"error": "Unknown error"}
                                st.error(f"❌ Analysis failed: {error_info.get('error', 'Unknown error')}")
                                break
                            
                            # Eğer tamamlandıysa sonuçları göster
                            if status == "COMPLETED" and row[0] and row[1]:
                                # JSON string'leri parse et
                                ml_analysis = json.loads(row[0]) if isinstance(row[0], str) else row[0]
                                clinical_analysis = json.loads(row[1]) if isinstance(row[1], str) else row[1]
                                
                                st.success("🎉 Analysis completed!")
                                
                                # Ana sonuçlar
                                c1, c2 = st.columns(2)
                                with c1:
                                    st.markdown("### 🤖 ML results")
                                    result_text = ml_analysis.get("result_text", "N/A")
                                    result_color = "🔴" if result_text == "Patient" else "🟢"
                                    st.markdown(f"**Result:** {result_color} {result_text}")
                                    
                                    # Olasılık bilgileri
                                    prob_patient = ml_analysis.get('probability_patient', ml_analysis.get('probability', 0))
                                    prob_healthy = ml_analysis.get('probability_healthy', 1 - prob_patient)
                                    
                                    st.progress(prob_patient)
                                    st.caption(f"**Patient probability:** {prob_patient*100:.2f}%")
                                    st.caption(f"**Healthy probability:** {prob_healthy*100:.2f}%")
                                    
                                    # Güvenilirlik seviyesi
                                    confidence = ml_analysis.get('confidence_level', 'Medium')
                                    confidence_icon = "🟢" if confidence == "High" else "🟡" if confidence == "Medium" else "🔴"
                                    st.info(f"**Confidence:** {confidence_icon} {confidence}")
                                    
                                    # En önemli özellikler
                                    if ml_analysis.get('top_features'):
                                        st.markdown("**Top features:**")
                                        for feat in ml_analysis['top_features']:
                                            st.caption(f"• {feat['feature']}: {feat['importance']*100:.2f}%")
                                
                                with c2:
                                    st.markdown("### 🏥 Clinical results")
                                    risk_score = clinical_analysis.get('risk_score', 'Normal')
                                    risk_score_numeric = clinical_analysis.get('risk_score_numeric', 0)
                                    risk_score_percentage = clinical_analysis.get('risk_score_percentage', 0)
                                    
                                    risk_icon = "🔴" if "High" in risk_score else "🟡" if "Medium" in risk_score else "🟢"
                                    st.markdown(f"**Risk level:** {risk_icon} {risk_score}")
                                    
                                    # Risk skoru progress bar (ML'deki gibi)
                                    st.progress(risk_score_numeric / 100)
                                    st.caption(f"**Risk score:** {risk_score_numeric:.1f}/100")
                                    
                                    # Güvenilirlik seviyesi (ML'deki gibi)
                                    confidence = clinical_analysis.get('risk_level_confidence', 'Medium')
                                    confidence_icon = "🟢" if confidence == "High" else "🟡" if confidence == "Medium" else "🔴"
                                    st.info(f"**Confidence:** {confidence_icon} {confidence}")
                                    
                                    # Risk faktörleri sayıları
                                    high_risks = clinical_analysis.get('high_risk_factors_count', 0)
                                    medium_risks = clinical_analysis.get('medium_risk_factors_count', 0)
                                    st.caption(f"**High-risk factors:** {high_risks} | **Medium-risk factors:** {medium_risks}")
                                    
                                    # En önemli risk faktörleri (ML'deki top_features gibi)
                                    if clinical_analysis.get('top_risk_factors'):
                                        st.markdown("**Top risk factors:**")
                                        for rf in clinical_analysis['top_risk_factors']:
                                            # Backward-compatible: older saved rows may not have `contribution`
                                            factor = rf.get("factor", "N/A")
                                            contribution = rf.get("contribution")
                                            weight = rf.get("weight")
                                            score = rf.get("score")

                                            # Compute contribution when missing (score * weight)
                                            if contribution is None:
                                                try:
                                                    if score is not None and weight is not None:
                                                        contribution = float(score) * float(weight)
                                                except Exception:
                                                    contribution = None

                                            try:
                                                weight_pct = f"{float(weight) * 100:.0f}%" if weight is not None else "N/A"
                                            except Exception:
                                                weight_pct = "N/A"

                                            if contribution is None:
                                                st.caption(f"• {factor} (weight: {weight_pct})")
                                            else:
                                                st.caption(f"• {factor}: {float(contribution):.2f} points (weight: {weight_pct})")
                                    
                                    # Bulgular
                                    if clinical_analysis.get('details'):
                                        st.markdown("**Findings:**")
                                        for detail in clinical_analysis['details']:
                                            st.warning(f"⚠️ {detail}")
                                    
                                    # Uyarılar
                                    if clinical_analysis.get('warnings'):
                                        st.markdown("**Warnings:**")
                                        for warning in clinical_analysis['warnings']:
                                            st.info(f"ℹ️ {warning}")
                                
                                # Detaylı bilgiler için expander
                                with st.expander("📊 Detailed analysis", expanded=False):
                                    col1, col2 = st.columns(2)
                                    
                                    with col1:
                                        st.markdown("#### ML model details")
                                        st.json({
                                            "Model type": ml_analysis.get('model_type', 'N/A'),
                                            "Prediction": ml_analysis.get('prediction', 'N/A'),
                                            "Result": ml_analysis.get('result_text', 'N/A'),
                                            "Patient probability": f"{prob_patient*100:.4f}%",
                                            "Healthy probability": f"{prob_healthy*100:.4f}%",
                                            "Confidence": ml_analysis.get('confidence_level', 'N/A')
                                        })
                                    
                                    with col2:
                                        st.markdown("#### Patient summary")
                                        patient_summary = clinical_analysis.get('patient_data_summary', {})
                                        st.json(patient_summary)
                                
                                # Risk faktörleri tablosu (detaylı)
                                if clinical_analysis.get('risk_factors'):
                                    st.markdown("### 📋 Risk factor breakdown")
                                    risk_df_data = []
                                    for rf in clinical_analysis['risk_factors']:
                                        score_val = rf.get("score", 0)
                                        weight_val = rf.get("weight", 0)
                                        risk_df_data.append({
                                            "Factor": rf.get('factor', 'N/A'),
                                            "Score (0-100)": f"{score_val:.0f}",
                                            "Weight": f"{weight_val*100:.0f}%",
                                            "Contribution": f"{score_val * weight_val:.2f}",
                                        })
                                    if risk_df_data:
                                        # Arrow/pyarrow serialization can fail when a column mixes types
                                        # (e.g. "Değer" being both numbers and strings like "Yok").
                                        risk_df = pd.DataFrame(risk_df_data).astype(str)
                                        st.dataframe(risk_df, width="stretch", hide_index=True)
                                
                                # Risk skorları detayı (ML'deki gibi)
                                if clinical_analysis.get('risk_scores'):
                                    with st.expander("📈 Risk score details", expanded=False):
                                        st.markdown("#### Risk score per factor (0–100)")
                                        risk_scores_data = clinical_analysis.get('risk_scores', {})
                                        for factor, score in risk_scores_data.items():
                                            factor_name = {
                                                'cholesterol': 'Cholesterol',
                                                'blood_pressure': 'Blood pressure',
                                                'age': 'Age',
                                                'chest_pain': 'Chest pain',
                                                'exercise_angina': 'Exercise angina',
                                                'st_depression': 'ST depression',
                                                'heart_rate': 'Heart rate',
                                                'fbs': 'Fasting blood sugar'
                                            }.get(factor, factor)
                                            st.progress(score / 100)
                                            st.caption(f"**{factor_name}:** {score:.0f}/100")
                                
                                break
                    except Exception as db_error:
                        st.error(f"Database error: {db_error}")
                        break
                
                if status == "PENDING":
                    st.warning("⏳ Analysis is not finished yet. Please try again in a few seconds.")
        else:
            st.error(f"❌ Request failed: {res.status_code} - {res.text}")
    except requests.exceptions.ConnectionError:
        st.error("❌ Could not reach the backend. Make sure the FastAPI server is running.")
    except Exception as e:
        st.error(f"❌ Unexpected error: {str(e)}")