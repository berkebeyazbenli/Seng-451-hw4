# 🌐 Streamlit Cloud Deployment Rehberi

## Streamlit Cloud'a Deploy Etme

### Adım 1: Streamlit Cloud'a Giriş
1. https://share.streamlit.io adresine gidin
2. GitHub hesabınızla giriş yapın

### Adım 2: Yeni App Oluştur
1. "New app" butonuna tıklayın
2. Repository seçin: `berkebeyazbenli/Seng-451-hw4`
3. Branch: `main`
4. Main file path: `app.py`

### Adım 3: Environment Variables Ekle
"Advanced settings" → "Secrets" bölümüne şunları ekleyin:

```toml
[secrets]
DB_HOST = "database-1.c814i00i8t9k.us-east-1.rds.amazonaws.com"
DB_NAME = "postgres"
DB_USER = "postgres"
DB_PASSWORD = "Bekobeko42"
BACKEND_URL = "https://your-backend-url.com"  # Backend URL'inizi buraya yazın
```

### Adım 4: Deploy
"Deploy" butonuna tıklayın. Streamlit Cloud otomatik olarak:
- `requirements.txt` dosyasını okuyacak
- Bağımlılıkları yükleyecek
- `app.py` dosyasını çalıştıracak

### ⚠️ Önemli Notlar

1. **Model Dosyaları**: `model.pkl` ve `scaler.pkl` dosyaları GitHub'da yok (`.gitignore`'da). 
   - Streamlit Cloud'a manuel olarak upload edin
   - Veya GitHub'a ekleyin (büyük dosyalar için Git LFS kullanın)

2. **Backend URL**: Backend'i de deploy etmeniz gerekiyor (Render, Railway, vb.)

3. **Database**: AWS RDS zaten canlıda, sadece bağlantı bilgilerini secrets'a ekleyin

## Model Dosyalarını Ekleme

### Yöntem 1: Git LFS (Önerilen)
```bash
git lfs install
git lfs track "*.pkl"
git add .gitattributes
git add model.pkl scaler.pkl
git commit -m "Add model files with Git LFS"
git push
```

### Yöntem 2: Streamlit Cloud Secrets
Model dosyalarını base64 encode edip secrets'a ekleyebilirsiniz (küçük dosyalar için).

### Yöntem 3: External Storage
Model dosyalarını AWS S3 veya başka bir storage'a yükleyip runtime'da indirin.

## Backend Deployment

Backend'i de deploy etmeniz gerekiyor. `DEPLOYMENT.md` dosyasına bakın.

## Test

Deploy sonrası Streamlit Cloud size bir URL verecek:
`https://your-app-name.streamlit.app`

Bu URL'den uygulamanıza erişebilirsiniz.

