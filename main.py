from fastapi import FastAPI, BackgroundTasks
import psycopg2
from psycopg2.extras import RealDictCursor
from experts import KnowledgeSources
import json
import os

app = FastAPI()

# Environment variables'dan oku, yoksa default değerleri kullan
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "database-1.c814i00i8t9k.us-east-1.rds.amazonaws.com"),
    "database": os.getenv("DB_NAME", "postgres"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "Bekobeko42"),
    "connect_timeout": 5
}

def blackboard_controller(record_id):
    """Mimarinin beyni: Uzmanları tetikler ve tahtayı günceller"""
    conn = None
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # 1. Blackboard'dan ham veriyi oku
        cur.execute("SELECT input_data FROM heart_blackboard WHERE id = %s", (record_id,))
        record = cur.fetchone()
        if not record:
            print(f"ID {record_id} için kayıt bulunamadı!")
            return
        
        # JSON string'i parse et
        patient_data = json.loads(record['input_data']) if isinstance(record['input_data'], str) else record['input_data']
        
        # 2. Uzmanları çalıştır
        try:
            ml_res = KnowledgeSources.ml_expert_module(patient_data)
            clin_res = KnowledgeSources.clinical_expert_module(patient_data)
            
            # 3. Sonuçları tahtaya (RDS) geri yaz
            cur.execute("""
                UPDATE heart_blackboard 
                SET ml_analysis = %s, clinical_analysis = %s, status = 'COMPLETED'
                WHERE id = %s
            """, (json.dumps(ml_res), json.dumps(clin_res), record_id))
            
            conn.commit()
            print(f"✅ ID {record_id} için analiz başarıyla Blackboard'a işlendi.")
        except Exception as expert_error:
            # Hata durumunda status'ü ERROR olarak güncelle
            error_msg = str(expert_error)
            cur.execute("""
                UPDATE heart_blackboard 
                SET status = 'ERROR', ml_analysis = %s
                WHERE id = %s
            """, (json.dumps({"error": error_msg}), record_id))
            conn.commit()
            print(f"❌ ID {record_id} için uzman modül hatası: {error_msg}")
        
        cur.close()
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Controller Hatası (ID {record_id}): {error_msg}")
        # Hata durumunda status'ü güncellemeyi dene
        try:
            if conn:
                cur = conn.cursor()
                cur.execute("""
                    UPDATE heart_blackboard 
                    SET status = 'ERROR', ml_analysis = %s
                    WHERE id = %s
                """, (json.dumps({"error": error_msg}), record_id))
                conn.commit()
                cur.close()
        except:
            pass
    finally:
        if conn:
            conn.close()

@app.post("/submit-patient")
async def submit_patient(data: dict, background_tasks: BackgroundTasks):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute("INSERT INTO heart_blackboard (input_data, status) VALUES (%s, 'PENDING') RETURNING id", (json.dumps(data),))
        new_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        
        # Analizi arka planda başlat
        background_tasks.add_task(blackboard_controller, new_id)
        return {"id": new_id, "status": "Success"}
    except Exception as e:
        return {"status": "Error", "message": str(e)}