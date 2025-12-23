# 🚀 Deployment Rehberi

## Deployment Seçenekleri

### 1. Render.com (Önerilen - Kolay)

#### Backend (FastAPI) Deploy:
1. Render.com'a giriş yapın
2. "New +" → "Web Service" seçin
3. GitHub repository'nizi bağlayın
4. Ayarlar:
   - **Name**: `heart-diagnosis-backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Environment Variables**:
     ```
     DB_HOST=database-1.c814i00i8t9k.us-east-1.rds.amazonaws.com
     DB_NAME=postgres
     DB_USER=postgres
     DB_PASSWORD=Bekobeko42
     ```

#### Frontend (Streamlit) Deploy:
1. Render.com'da "New +" → "Web Service"
2. Ayarlar:
   - **Name**: `heart-diagnosis-frontend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `streamlit run app.py --server.port $PORT --server.address 0.0.0.0`
   - **Environment Variables**: Backend URL'ini ekleyin

### 2. Railway.app

1. Railway.app'e giriş yapın
2. "New Project" → GitHub repo seçin
3. Otomatik olarak detect eder ve deploy eder
4. Environment variables ekleyin

### 3. AWS EC2

```bash
# EC2 instance'a bağlan
ssh -i your-key.pem ubuntu@your-ec2-ip

# Gerekli paketleri yükle
sudo apt update
sudo apt install python3-pip python3-venv postgresql-client -y

# Projeyi klonla
git clone https://github.com/berkebeyazbenli/Seng-451-hw4.git
cd Seng-451-hw4

# Virtual environment oluştur
python3 -m venv venv
source venv/bin/activate

# Bağımlılıkları yükle
pip install -r requirements.txt

# Backend'i başlat (screen veya systemd ile)
screen -S backend
uvicorn main:app --host 0.0.0.0 --port 8000

# Frontend'i başlat (yeni screen'de)
screen -S frontend
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
```

### 4. Docker ile Deploy

```bash
# Docker image oluştur
docker build -t heart-diagnosis .

# Backend container
docker run -d -p 8000:8000 \
  -e DB_HOST=database-1.c814i00i8t9k.us-east-1.rds.amazonaws.com \
  -e DB_NAME=postgres \
  -e DB_USER=postgres \
  -e DB_PASSWORD=Bekobeko42 \
  --name backend \
  heart-diagnosis uvicorn main:app --host 0.0.0.0 --port 8000

# Frontend container
docker run -d -p 8501:8501 \
  -e BACKEND_URL=http://your-backend-url:8000 \
  --name frontend \
  heart-diagnosis streamlit run app.py --server.port 8501 --server.address 0.0.0.0
```

## 🔧 Environment Variables

Production'da şunları kullanın:

```bash
DB_HOST=database-1.c814i00i8t9k.us-east-1.rds.amazonaws.com
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=Bekobeko42
BACKEND_URL=https://your-backend-url.com
```

## ⚠️ Önemli Notlar

1. **Güvenlik**: Production'da şifreleri environment variables olarak kullanın
2. **CORS**: Frontend ve backend farklı domain'lerdeyse CORS ayarları gerekebilir
3. **Model Dosyaları**: `model.pkl` ve `scaler.pkl` dosyalarını deployment'a eklemeyi unutmayın
4. **Port**: Render/Railway gibi servisler PORT environment variable kullanır

## 📝 Model Dosyalarını Ekleme

Model dosyaları `.gitignore`'da olduğu için GitHub'a push edilmez. Deployment'a eklemek için:

1. **Render/Railway**: Model dosyalarını manuel olarak upload edin
2. **Docker**: Dockerfile'a `COPY model.pkl scaler.pkl ./` ekleyin
3. **EC2**: `scp` ile dosyaları kopyalayın

