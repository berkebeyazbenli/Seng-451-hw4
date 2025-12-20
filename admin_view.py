import streamlit as st
import psycopg2
import json
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Blackboard Admin View", layout="wide")
st.title("📊 Blackboard Veritabanı Görüntüleme")

DB_CONFIG = {
    "host": "database-1.c814i00i8t9k.us-east-1.rds.amazonaws.com",
    "database": "postgres",
    "user": "postgres",
    "password": "Bekobeko42",
    "connect_timeout": 5
}

def get_all_records():
    """Tüm kayıtları getir"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        cur.execute("""
            SELECT id, status, 
                   input_data,
                   ml_analysis,
                   clinical_analysis,
                   created_at
            FROM heart_blackboard
            ORDER BY id DESC
        """)
        
        records = cur.fetchall()
        cur.close()
        conn.close()
        return records
    except Exception as e:
        st.error(f"Veritabanı hatası: {e}")
        return []

def get_statistics():
    """İstatistikleri getir"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        # Toplam kayıt
        cur.execute("SELECT COUNT(*) FROM heart_blackboard")
        total = cur.fetchone()[0]
        
        # Status dağılımı
        cur.execute("""
            SELECT status, COUNT(*) 
            FROM heart_blackboard 
            GROUP BY status
        """)
        status_dist = dict(cur.fetchall())
        
        # ML sonuç dağılımı
        cur.execute("""
            SELECT ml_analysis->>'result_text' as result, COUNT(*) 
            FROM heart_blackboard 
            WHERE ml_analysis IS NOT NULL
            GROUP BY ml_analysis->>'result_text'
        """)
        ml_dist = dict(cur.fetchall())
        
        cur.close()
        conn.close()
        
        return {
            "total": total,
            "status_dist": status_dist,
            "ml_dist": ml_dist
        }
    except Exception as e:
        st.error(f"İstatistik hatası: {e}")
        return None

# Sidebar - Filtreler
with st.sidebar:
    st.header("🔍 Filtreler")
    status_filter = st.selectbox(
        "Status Filtresi",
        ["Tümü", "PENDING", "COMPLETED", "ERROR"]
    )
    refresh = st.button("🔄 Yenile")

# İstatistikler
stats = get_statistics()
if stats:
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Toplam Kayıt", stats["total"])
    with col2:
        st.metric("Tamamlanan", stats["status_dist"].get("COMPLETED", 0))
    with col3:
        st.metric("Beklemede", stats["status_dist"].get("PENDING", 0))
    with col4:
        st.metric("Hata", stats["status_dist"].get("ERROR", 0))

# Kayıtları getir
records = get_all_records()

if records:
    # Filtreleme
    if status_filter != "Tümü":
        records = [r for r in records if r[1] == status_filter]
    
    st.subheader(f"📋 Kayıtlar ({len(records)} adet)")
    
    # Tablo görünümü
    if st.checkbox("📊 Tablo Görünümü", value=True):
        table_data = []
        for record in records:
            id_val, status, input_data, ml_analysis, clinical_analysis, created_at = record
            
            # Input data parse
            input_parsed = json.loads(input_data) if isinstance(input_data, str) else input_data
            
            # ML analysis parse
            ml_parsed = None
            if ml_analysis:
                ml_parsed = json.loads(ml_analysis) if isinstance(ml_analysis, str) else ml_analysis
            
            # Clinical analysis parse
            clin_parsed = None
            if clinical_analysis:
                clin_parsed = json.loads(clinical_analysis) if isinstance(clinical_analysis, str) else clinical_analysis
            
            table_data.append({
                "ID": id_val,
                "Status": status,
                "Yaş": input_parsed.get("age", "N/A"),
                "Kan Basıncı": input_parsed.get("trestbps", "N/A"),
                "Kolesterol": input_parsed.get("chol", "N/A"),
                "ML Sonuç": ml_parsed.get("result_text", "N/A") if ml_parsed else "N/A",
                "ML Olasılık": f"%{ml_parsed.get('probability', 0)*100:.1f}" if ml_parsed and ml_parsed.get('probability') else "N/A",
                "Risk Skoru": clin_parsed.get("risk_score", "N/A") if clin_parsed else "N/A",
                "Oluşturulma": created_at.strftime("%Y-%m-%d %H:%M:%S") if created_at else "N/A"
            })
        
        df = pd.DataFrame(table_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
    
    # Detaylı görünüm
    st.subheader("🔍 Detaylı Görünüm")
    selected_id = st.selectbox("Kayıt Seçin", [r[0] for r in records])
    
    if selected_id:
        selected_record = next((r for r in records if r[0] == selected_id), None)
        if selected_record:
            id_val, status, input_data, ml_analysis, clinical_analysis, created_at = selected_record
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 📥 Input Data (Hasta Verisi)")
                input_parsed = json.loads(input_data) if isinstance(input_data, str) else input_data
                st.json(input_parsed)
            
            with col2:
                st.markdown("### 📊 Status Bilgisi")
                st.info(f"**Status:** {status}")
                if created_at:
                    st.info(f"**Oluşturulma:** {created_at.strftime('%Y-%m-%d %H:%M:%S')}")
            
            if ml_analysis:
                st.markdown("### 🤖 ML Analysis")
                ml_parsed = json.loads(ml_analysis) if isinstance(ml_analysis, str) else ml_analysis
                st.json(ml_parsed)
            
            if clinical_analysis:
                st.markdown("### 🏥 Clinical Analysis")
                clin_parsed = json.loads(clinical_analysis) if isinstance(clinical_analysis, str) else clinical_analysis
                st.json(clin_parsed)
else:
    st.warning("📭 Henüz kayıt bulunmamaktadır.")

