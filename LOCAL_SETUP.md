# 💻 Local Development Setup

## Backend'i Local'de Çalıştırma

### 1. Gereksinimler

```bash
pip install -r requirements.txt
```

### 2. Model Dosyalarını Kontrol Edin

`model.pkl` ve `scaler.pkl` dosyalarının proje dizininde olduğundan emin olun.

### 3. Backend'i Başlatın

```bash
# Terminal 1: Backend
uvicorn main:app --reload --port 8000
```

Backend şu adreste çalışacak: `http://localhost:8000`

### 4. Frontend'i Başlatın

```bash
# Terminal 2: Frontend
streamlit run app.py
```

Frontend şu adreste çalışacak: `http://localhost:8501`

### 5. Test

1. Frontend'i açın: http://localhost:8501
2. Hasta verilerini girin
3. "Teşhis Koy" butonuna basın
4. Backend loglarını kontrol edin (Terminal 1)

## Backend Endpoints

- **Health Check**: http://localhost:8000/health
- **Root**: http://localhost:8000/
- **API Docs**: http://localhost:8000/docs (Swagger UI)
- **Submit Patient**: POST http://localhost:8000/submit-patient

## Environment Variables (Local)

Local'de environment variables kullanmak isterseniz:

```bash
# Linux/Mac
export DB_HOST="database-1.c814i00i8t9k.us-east-1.rds.amazonaws.com"
export DB_NAME="postgres"
export DB_USER="postgres"
export DB_PASSWORD="Bekobeko42"

# Windows
set DB_HOST=database-1.c814i00i8t9k.us-east-1.rds.amazonaws.com
set DB_NAME=postgres
set DB_USER=postgres
set DB_PASSWORD=Bekobeko42
```

Veya `.env` dosyası kullanın (python-dotenv ile).

## Sorun Giderme

### Backend başlamıyor
- Port 8000 kullanımda mı? `lsof -i :8000` (Mac/Linux)
- Model dosyaları var mı?
- Veritabanı bağlantısı çalışıyor mu?

### Frontend backend'e bağlanamıyor
- Backend çalışıyor mu? http://localhost:8000/health
- `BACKEND_URL` doğru mu? (Local'de `http://localhost:8000`)

### Model dosyaları bulunamıyor
- `model.pkl` ve `scaler.pkl` proje dizininde mi?
- Dosya yolları doğru mu?

