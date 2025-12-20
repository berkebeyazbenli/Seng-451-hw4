#!/usr/bin/env python3
"""
PostgreSQL Blackboard Verilerini Görüntüleme Aracı
"""
import psycopg2
import json
from datetime import datetime
from tabulate import tabulate

DB_CONFIG = {
    "host": "database-1.c814i00i8t9k.us-east-1.rds.amazonaws.com",
    "database": "postgres",
    "user": "postgres",
    "password": "Bekobeko42",
    "connect_timeout": 5
}

def view_all_records():
    """Tüm kayıtları göster"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        cur.execute("""
            SELECT id, status, 
                   input_data->>'age' as age,
                   input_data->>'trestbps' as bp,
                   input_data->>'chol' as chol,
                   ml_analysis->>'result_text' as ml_result,
                   ml_analysis->>'probability' as ml_prob,
                   clinical_analysis->>'risk_score' as risk_score,
                   created_at
            FROM heart_blackboard
            ORDER BY id DESC
            LIMIT 20
        """)
        
        records = cur.fetchall()
        
        if records:
            headers = ["ID", "Status", "Yaş", "Kan Basıncı", "Kolesterol", 
                      "ML Sonuç", "ML Olasılık", "Risk Skoru", "Oluşturulma"]
            print("\n" + "="*100)
            print("📊 BLACKBOARD KAYITLARI (Son 20 Kayıt)")
            print("="*100)
            print(tabulate(records, headers=headers, tablefmt="grid"))
            print("="*100)
        else:
            print("❌ Kayıt bulunamadı!")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Hata: {e}")

def view_record_detail(record_id):
    """Belirli bir kaydın detaylarını göster"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        cur.execute("""
            SELECT id, input_data, ml_analysis, clinical_analysis, status, created_at
            FROM heart_blackboard
            WHERE id = %s
        """, (record_id,))
        
        record = cur.fetchone()
        
        if record:
            print("\n" + "="*80)
            print(f"📋 KAYIT DETAYI - ID: {record[0]}")
            print("="*80)
            print(f"Status: {record[4]}")
            print(f"Oluşturulma: {record[5]}")
            print("\n📥 INPUT DATA (Hasta Verisi):")
            print(json.dumps(json.loads(record[1]) if isinstance(record[1], str) else record[1], 
                           indent=2, ensure_ascii=False))
            
            if record[2]:
                print("\n🤖 ML ANALYSIS:")
                ml_data = json.loads(record[2]) if isinstance(record[2], str) else record[2]
                print(json.dumps(ml_data, indent=2, ensure_ascii=False))
            
            if record[3]:
                print("\n🏥 CLINICAL ANALYSIS:")
                clin_data = json.loads(record[3]) if isinstance(record[3], str) else record[3]
                print(json.dumps(clin_data, indent=2, ensure_ascii=False))
            
            print("="*80)
        else:
            print(f"❌ ID {record_id} için kayıt bulunamadı!")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Hata: {e}")

def view_statistics():
    """İstatistikleri göster"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        # Toplam kayıt sayısı
        cur.execute("SELECT COUNT(*) FROM heart_blackboard")
        total = cur.fetchone()[0]
        
        # Status dağılımı
        cur.execute("""
            SELECT status, COUNT(*) 
            FROM heart_blackboard 
            GROUP BY status
        """)
        status_dist = cur.fetchall()
        
        # ML sonuç dağılımı
        cur.execute("""
            SELECT ml_analysis->>'result_text' as result, COUNT(*) 
            FROM heart_blackboard 
            WHERE ml_analysis IS NOT NULL
            GROUP BY ml_analysis->>'result_text'
        """)
        ml_dist = cur.fetchall()
        
        print("\n" + "="*60)
        print("📈 İSTATİSTİKLER")
        print("="*60)
        print(f"Toplam Kayıt: {total}")
        print("\nStatus Dağılımı:")
        for status, count in status_dist:
            print(f"  {status}: {count}")
        print("\nML Sonuç Dağılımı:")
        for result, count in ml_dist:
            if result:
                print(f"  {result}: {count}")
        print("="*60)
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Hata: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "detail" and len(sys.argv) > 2:
            view_record_detail(int(sys.argv[2]))
        elif sys.argv[1] == "stats":
            view_statistics()
        else:
            print("Kullanım:")
            print("  python view_database.py              # Tüm kayıtları listele")
            print("  python view_database.py detail <id>  # Belirli kaydı göster")
            print("  python view_database.py stats        # İstatistikleri göster")
    else:
        view_all_records()

