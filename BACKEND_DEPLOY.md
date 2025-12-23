# 🚀 Backend Deployment Rehberi (FastAPI)

Backend'i deploy etmeden Streamlit frontend çalışmaz!

## 🎯 Backend'in Rolü

1. **API Endpoint**: `/submit-patient` - Hasta verilerini alır
2. **Blackboard Controller**: Uzmanları tetikler ve sonuçları blackboard'a yazar
3. **Background Tasks**: Analiz işlemlerini arka planda yürütür

## 🚀 Deployment Seçenekleri

### Seçenek 1: Render.com (Önerilen - Otomatik Deploy ✅)

Render.com **otomatik deploy** yapar! GitHub'a push ettiğinizde otomatik olarak deploy edilir.

#### Adımlar:

1. **Render.com'a giriş yapın**
   - https://render.com
   - GitHub hesabınızla giriş yapın

2. **Yeni Web Service Oluşturun**
   - "New +" → "Web Service"
   - GitHub repository'nizi bağlayın: `berkebeyazbenli/Seng-451-hw4`
   - Branch: `main`
   - ✅ **"Auto-Deploy"** seçeneği aktif olacak (otomatik deploy)

3. **Ayarları Yapın**
   - **Name**: `heart-diagnosis-backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: Free (veya istediğiniz plan)

4. **Environment Variables Ekleyin**
   ```
   DB_HOST=database-1.c814i00i8t9k.us-east-1.rds.amazonaws.com
   DB_NAME=postgres
   DB_USER=postgres
   DB_PASSWORD=Bekobeko42
   ```

5. **İlk Deploy**
   - "Create Web Service" butonuna tıklayın
   - 2-3 dakika bekleyin
   - Backend URL'inizi kopyalayın (örn: `https://heart-diagnosis-backend.onrender.com`)

6. **Otomatik Deploy Aktif! 🎉**
   - Artık `main.py`, `experts.py` veya `requirements.txt` değiştiğinde
   - GitHub'a push ettiğinizde
   - Render.com **otomatik olarak yeniden deploy edecek**

7. **Streamlit Cloud Secrets'ı Güncelleyin**
   - Streamlit Cloud → App Settings → Secrets
   - `BACKEND_URL` değerini backend URL'inizle güncelleyin:
   ```toml
   BACKEND_URL = "https://heart-diagnosis-backend.onrender.com"
   ```

### Seçenek 2: Railway.app

1. Railway.app'e giriş yapın
2. "New Project" → GitHub repo seçin
3. Otomatik detect eder
4. Environment variables ekleyin
5. Deploy edin

### Seçenek 3: Fly.io

1. Fly.io CLI yükleyin
2. `fly launch` komutuyla deploy edin
3. Environment variables ekleyin

### Seçenek 4: AWS EC2 / Heroku / DigitalOcean

Detaylar için `DEPLOYMENT.md` dosyasına bakın.

## ⚠️ Önemli Notlar

### Model Dosyaları

Backend'de `model.pkl` ve `scaler.pkl` dosyalarına ihtiyaç var:

**Render.com için:**
1. Model dosyalarını GitHub'a ekleyin (Git LFS ile)
2. Veya Render'da "Environment" → "Secret Files" ile upload edin

**Git LFS ile ekleme:**
```bash
git lfs install
git lfs track "*.pkl"
git add .gitattributes model.pkl scaler.pkl
git commit -m "Add model files"
git push
```

### CORS Ayarları (Gerekirse)

Eğer frontend ve backend farklı domain'lerdeyse, `main.py`'ye CORS ekleyin:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Production'da spesifik domain kullanın
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Health Check Endpoint

Backend'in çalıştığını kontrol etmek için `main.py`'ye ekleyin:

```python
@app.get("/")
async def root():
    return {"status": "ok", "message": "Backend is running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}
```

## ✅ Test

Backend deploy edildikten sonra:

1. **Health Check**: `https://your-backend-url.com/health`
2. **API Test**: Postman veya curl ile test edin
3. **Frontend**: Streamlit Cloud'dan backend'e bağlanabildiğini kontrol edin

## 🔗 Frontend-Backend Bağlantısı

Streamlit Cloud'da `BACKEND_URL` secret'ını backend URL'inizle güncelleyin:

```toml
BACKEND_URL = "https://your-backend-url.com"
```

## 📊 Deployment Sonrası

1. ✅ Backend çalışıyor mu? (`/health` endpoint'i)
2. ✅ Frontend backend'e bağlanabiliyor mu?
3. ✅ Model dosyaları backend'de var mı?
4. ✅ Veritabanı bağlantısı çalışıyor mu?

## 🆘 Sorun Giderme

### Backend çalışmıyor
- Logs'u kontrol edin
- Environment variables doğru mu?
- Model dosyaları var mı?

### Frontend backend'e bağlanamıyor
- `BACKEND_URL` doğru mu?
- CORS ayarları yapıldı mı?
- Backend çalışıyor mu?

### Model dosyaları bulunamıyor
- Git LFS ile eklediniz mi?
- Dosya yolu doğru mu?
- Render'da secret files kullandınız mı?

