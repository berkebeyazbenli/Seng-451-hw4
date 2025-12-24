# ✅ Backend Deploy Durumunu Kontrol Etme

## 🔍 Backend Deploy Edildi Mi?

### Yöntem 1: Script ile Kontrol (Hızlı)

```bash
python3 check_backend.py
```

Bu script backend'in çalışıp çalışmadığını kontrol eder.

### Yöntem 2: Tarayıcı ile Kontrol

1. **Health Check**: https://seng-451-hw4.onrender.com/health
   - Çalışıyorsa: `{"status": "healthy", "service": "heart-diagnosis-backend"}` görürsünüz
   - Çalışmıyorsa: Hata sayfası veya timeout

2. **API Docs**: https://seng-451-hw4.onrender.com/docs
   - Çalışıyorsa: Swagger UI görürsünüz
   - Çalışmıyorsa: Hata sayfası

3. **Root Endpoint**: https://seng-451-hw4.onrender.com/
   - Çalışıyorsa: `{"status": "ok", "message": "Backend is running"}` görürsünüz

### Yöntem 3: Render.com Dashboard

1. Render.com dashboard'a gidin
2. Backend servisinize tıklayın (`Seng-451-hw4`)
3. **"Logs"** sekmesine bakın:
   - ✅ "Deployed successfully" görürseniz → Çalışıyor
   - ⏳ "Building..." görürseniz → Hala deploy ediliyor
   - ❌ Hata mesajları varsa → Sorun var

4. **"Events"** sekmesine bakın:
   - Son deploy'un durumunu gösterir
   - Başarılı/başarısız olduğunu gösterir

## 🎯 Deploy Durumları

### ✅ Başarılı Deploy
- Health check çalışıyor
- API docs erişilebilir
- Logs'ta "Deployed successfully" var
- Events'te yeşil tick var

### ⏳ Deploy Ediliyor
- Logs'ta "Building..." görünüyor
- Health check timeout veriyor
- Birkaç dakika bekleyin

### ❌ Deploy Başarısız
- Logs'ta hata mesajları var
- Health check bağlanamıyor
- Events'te kırmızı X var
- Ayarları kontrol edin (Python 3, build command, vb.)

### 💤 Uyku Modunda (Free Tier)
- 15 dakika kullanılmazsa uyku moduna geçer
- İlk istek 50 saniye gecikebilir
- Sonra normal çalışır

## 🚀 Hızlı Test

Terminal'de:

```bash
# Health check
curl https://seng-451-hw4.onrender.com/health

# Root endpoint
curl https://seng-451-hw4.onrender.com/
```

Başarılı yanıt:
```json
{"status": "healthy", "service": "heart-diagnosis-backend"}
```

## 📝 Notlar

- **Free Tier**: İlk istek 50 saniye gecikebilir (uyku modu)
- **Deploy Süresi**: İlk deploy 2-5 dakika sürebilir
- **Otomatik Deploy**: GitHub'a push ettiğinizde otomatik deploy edilir

## 🆘 Sorun Giderme

### Backend çalışmıyor
1. Render.com dashboard → Logs kontrol edin
2. Settings → Environment "Python 3" mü?
3. Build Command doğru mu?
4. Start Command doğru mu?
5. Environment Variables ekli mi?

### Timeout alıyorum
- Free tier'da uyku modunda olabilir
- Birkaç saniye bekleyip tekrar deneyin
- İlk istek yavaş olabilir (50 saniye)

