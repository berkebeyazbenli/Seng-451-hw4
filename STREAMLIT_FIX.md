# 🔧 Streamlit Cloud Deployment Hata Çözümü

## Sorun: Package Installation Error

Streamlit Cloud'da paket kurulumu sırasında hata alıyorsanız:

### Çözüm 1: Requirements.txt Güncellendi ✅

`requirements.txt` dosyası güncellendi ve daha esnek versiyonlar kullanılıyor.

### Çözüm 2: Model Dosyalarını Ekleme

**ÖNEMLİ**: `model.pkl` ve `scaler.pkl` dosyaları GitHub'da yok (`.gitignore`'da). 

#### Seçenek A: Git LFS ile Ekleme (Önerilen)

```bash
# Git LFS'i yükle ve aktif et
git lfs install

# .pkl dosyalarını track et
git lfs track "*.pkl"

# .gitattributes dosyasını ekle
git add .gitattributes

# Model dosyalarını ekle
git add model.pkl scaler.pkl

# Commit ve push
git commit -m "Add model files with Git LFS"
git push origin main
```

#### Seçenek B: Manuel Upload (Streamlit Cloud)

1. Streamlit Cloud dashboard'a gidin
2. App settings → "Files" sekmesi
3. Model dosyalarını manuel olarak upload edin

#### Seçenek C: External Storage (Büyük Dosyalar İçin)

Model dosyalarını AWS S3 veya başka bir storage'a yükleyip, runtime'da indirin:

```python
# experts.py'ye ekleyin
import boto3
import os

def download_models():
    if not os.path.exists('model.pkl'):
        s3 = boto3.client('s3')
        s3.download_file('your-bucket', 'model.pkl', 'model.pkl')
        s3.download_file('your-bucket', 'scaler.pkl', 'scaler.pkl')
```

### Çözüm 3: Paket Versiyonlarını Kontrol Etme

Eğer hala hata alıyorsanız, `packages.txt` dosyasını kullanın (versiyonsuz):

1. Streamlit Cloud'da app settings'e gidin
2. "Dependencies" bölümünde `packages.txt` dosyasını seçin
3. Veya `requirements.txt` yerine manuel olarak paketleri ekleyin

### Çözüm 4: Python Versiyonu

Streamlit Cloud genellikle Python 3.11 kullanır. Eğer sorun devam ederse:

1. App settings → "Python version" → 3.11 seçin
2. Veya `runtime.txt` dosyası oluşturun:

```
python-3.11.5
```

### Çözüm 5: Build Logs Kontrol

Streamlit Cloud'da:
1. App dashboard'a gidin
2. "Logs" sekmesine tıklayın
3. Hangi paketin hata verdiğini kontrol edin
4. O paketi `requirements.txt`'ten kaldırıp alternatifini deneyin

## Test

Deploy sonrası:
1. App URL'ine gidin
2. Console'da hata olup olmadığını kontrol edin
3. Model dosyalarının yüklendiğini kontrol edin

## Hala Çalışmıyorsa

1. Streamlit Cloud community forum'a sorun: https://discuss.streamlit.io
2. GitHub issues'da ara: https://github.com/streamlit/streamlit-cloud
3. Minimal bir test app oluşturup adım adım paket ekleyin

