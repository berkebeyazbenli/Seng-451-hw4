# 🩺 Kalp Teşhis Destek Sistemi - Blackboard Architecture

Bu proje, **Blackboard Pattern** mimarisini kullanarak kalp hastalığı teşhisi yapan bir uzman sistem uygulamasıdır.

## 📋 Proje Hakkında

Sistem, birden fazla uzman modülün (Knowledge Sources) ortak bir veri yapısı (Blackboard) üzerinde çalışarak hasta verilerini analiz eder ve teşhis önerisi sunar.

## 🏗️ Mimari

### Blackboard Pattern Bileşenleri

1. **Blackboard (Veritabanı)**: PostgreSQL RDS - Tüm verilerin merkezi deposu
2. **Controller**: Uzmanları koordine eden merkezi kontrol mekanizması
3. **Knowledge Sources (Uzmanlar)**:
   - **ML Expert**: Makine öğrenmesi tabanlı tahmin
   - **Clinical Expert**: Klinik kurallar ve risk faktörleri analizi

## 🚀 Kurulum

### Gereksinimler

```bash
pip install streamlit fastapi uvicorn psycopg2 pandas numpy scikit-learn requests
```

### Veritabanı Kurulumu

PostgreSQL veritabanında `heart_blackboard` tablosunu oluşturun:

```sql
CREATE TABLE heart_blackboard (
    id SERIAL PRIMARY KEY,
    input_data JSONB,
    ml_analysis JSONB,
    clinical_analysis JSONB,
    status VARCHAR(20),
    final_diagnosis TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Model Dosyaları

`model.pkl` ve `scaler.pkl` dosyalarını proje dizinine ekleyin (GitHub'a push edilmez, .gitignore'da).

## 📁 Dosya Yapısı

```
SoftwareArchitecture/
├── app.py                      # Streamlit frontend
├── main.py                     # FastAPI backend
├── experts.py                  # Uzman modüller (ML + Clinical)
├── model.pkl                    # ML modeli (gitignore'da)
├── scaler.pkl                  # Scaler (gitignore'da)
├── admin_view.py               # Admin görüntüleme sayfası
├── view_database.py            # Veritabanı görüntüleme scripti
├── dbeaver_queries.sql         # DBeaver SQL sorguları
├── BLACKBOARD_ARCHITECTURE.md  # Mimari dokümantasyonu
└── README.md                   # Bu dosya
```

## 🎯 Kullanım

### Backend'i Başlatma

```bash
uvicorn main:app --reload --port 8000
```

### Frontend'i Başlatma

```bash
streamlit run app.py
```

### Admin Görüntüleme

```bash
streamlit run admin_view.py
```

## 🔄 İş Akışı

1. Kullanıcı hasta verilerini frontend'ten girer
2. Veri blackboard'a (PostgreSQL) yazılır (status: PENDING)
3. Controller arka planda çalışır
4. Uzmanlar (ML + Clinical) analiz yapar
5. Sonuçlar blackboard'a yazılır (status: COMPLETED)
6. Frontend polling ile sonuçları okur ve gösterir

## 📊 Özellikler

### ML Expert Modülü
- RandomForest modeli ile tahmin
- Olasılık skorları
- Güvenilirlik seviyesi
- En önemli özellikler analizi

### Clinical Expert Modülü
- Detaylı risk faktörleri analizi
- 0-100 arası risk skoru
- Ağırlıklı risk hesaplama
- En önemli risk faktörleri
- Güvenilirlik seviyesi

## 🛠️ Teknolojiler

- **Frontend**: Streamlit
- **Backend**: FastAPI
- **Database**: PostgreSQL (AWS RDS)
- **ML**: scikit-learn (RandomForest)
- **Architecture**: Blackboard Pattern

## 📚 Dokümantasyon

Detaylı mimari açıklaması için `BLACKBOARD_ARCHITECTURE.md` dosyasına bakın.

## 👥 Grup

Group-17

## 📝 Lisans

Bu proje eğitim amaçlıdır.

