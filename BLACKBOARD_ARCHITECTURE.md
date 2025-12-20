# 🎯 Blackboard Mimari Mimarisi - Açıklama

## 📚 Blackboard Pattern Nedir?

Blackboard Pattern, birden fazla uzman sistemin (knowledge sources) ortak bir veri yapısı (blackboard) üzerinde çalışarak karmaşık problemleri çözdüğü bir yazılım mimarisidir. Gerçek hayattaki bir grup uzmanın bir tahta (blackboard) üzerinde çalışarak problemi çözmeye benzer.

## 🏗️ Bu Projedeki Uygulama

### 1. **Blackboard (Veritabanı)**
- **Konum**: PostgreSQL veritabanı (`heart_blackboard` tablosu)
- **Rol**: Tüm verilerin ve sonuçların merkezi depolandığı yer
- **Yapı**:
  ```sql
  heart_blackboard:
    - id: Kayıt ID'si
    - input_data: Ham hasta verisi (JSON)
    - ml_analysis: ML uzmanının sonuçları (JSON)
    - clinical_analysis: Klinik uzmanının sonuçları (JSON)
    - status: Durum (PENDING, COMPLETED, ERROR)
  ```

### 2. **Controller (Koordinatör)**
- **Fonksiyon**: `blackboard_controller()` (main.py)
- **Rol**: 
  - Blackboard'dan veri okur
  - Uzmanları tetikler
  - Sonuçları blackboard'a yazar
  - Süreci yönetir

### 3. **Knowledge Sources (Uzmanlar)**
İki farklı uzman modül:

#### 🤖 ML Expert Module
- **Konum**: `experts.py` → `ml_expert_module()`
- **Uzmanlık**: Makine öğrenmesi ile tahmin
- **Yöntem**: RandomForest modeli kullanarak hasta/sağlıklı tahmini
- **Çıktı**: 
  - Tahmin (0/1)
  - Olasılıklar
  - Güvenilirlik seviyesi
  - Önemli özellikler

#### 🏥 Clinical Expert Module
- **Konum**: `experts.py` → `clinical_expert_module()`
- **Uzmanlık**: Klinik kurallar ve risk faktörleri
- **Yöntem**: Tıbbi kurallara göre analiz
- **Çıktı**:
  - Risk skoru
  - Bulgular
  - Uyarılar
  - Risk faktörleri

## 🔄 İş Akışı (Workflow)

```
┌─────────────────────────────────────────────────────────────┐
│  1. Kullanıcı Veri Girişi (Frontend - app.py)              │
│     - Hasta bilgileri girilir                               │
│     - "Teşhis Koy" butonuna basılır                         │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  2. API İsteği (main.py - submit_patient)                  │
│     - POST /submit-patient                                  │
│     - Veri blackboard'a yazılır (status: PENDING)         │
│     - Background task başlatılır                           │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  3. Blackboard'a Yazma (PostgreSQL)                        │
│     INSERT INTO heart_blackboard                            │
│     VALUES (input_data, 'PENDING')                          │
│     RETURNING id                                            │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  4. Controller Tetiklenir (blackboard_controller)          │
│     - Background task olarak çalışır                       │
│     - Blackboard'dan veri okur                             │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  5. Uzmanlar Çalıştırılır (Knowledge Sources)              │
│                                                             │
│     ┌──────────────────┐    ┌──────────────────┐          │
│     │ ML Expert        │    │ Clinical Expert │          │
│     │ - Model tahmini  │    │ - Risk analizi   │          │
│     │ - Olasılıklar    │    │ - Bulgular       │          │
│     └────────┬─────────┘    └────────┬─────────┘          │
│              │                        │                    │
│              └──────────┬─────────────┘                    │
│                         │                                  │
└─────────────────────────┼──────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  6. Sonuçlar Blackboard'a Yazılır                          │
│     UPDATE heart_blackboard                                │
│     SET ml_analysis = {...},                               │
│         clinical_analysis = {...},                         │
│         status = 'COMPLETED'                               │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  7. Frontend Polling (app.py)                              │
│     - Status kontrol edilir                                │
│     - COMPLETED olana kadar beklenir                       │
│     - Sonuçlar gösterilir                                  │
└─────────────────────────────────────────────────────────────┘
```

## 🎯 Blackboard Pattern'in Avantajları

### ✅ Bu Projede Sağladığı Faydalar:

1. **Modülerlik**: 
   - Her uzman bağımsız çalışır
   - Yeni uzmanlar kolayca eklenebilir
   - Uzmanlar birbirini tanımaz

2. **Esneklik**:
   - Uzmanlar farklı zamanlarda çalışabilir
   - Paralel işleme mümkün
   - Uzmanlar sırayla veya aynı anda çalışabilir

3. **Genişletilebilirlik**:
   - Yeni uzman modül eklemek kolay
   - Mevcut kodu değiştirmeden yeni özellikler eklenebilir

4. **Merkezi Veri Yönetimi**:
   - Tüm veriler tek yerde (blackboard)
   - Veri tutarlılığı sağlanır
   - Durum takibi kolay

5. **Hata Yönetimi**:
   - Bir uzman hata verirse diğerleri etkilenmez
   - Hata durumu blackboard'a kaydedilir
   - Kullanıcı bilgilendirilir

## 📊 Veri Akışı Detayı

### Blackboard Durumları:
- **PENDING**: Veri eklendi, analiz bekleniyor
- **COMPLETED**: Tüm uzmanlar çalıştı, sonuçlar hazır
- **ERROR**: Analiz sırasında hata oluştu

### Örnek Blackboard Kaydı:
```json
{
  "id": 11,
  "input_data": {
    "age": 45,
    "sex": 1,
    "trestbps": 120,
    "chol": 210,
    "cp": 0,
    "thalach": 150,
    ...
  },
  "ml_analysis": {
    "prediction": 1,
    "probability": 0.74,
    "result_text": "Hasta",
    "confidence_level": "Yüksek",
    ...
  },
  "clinical_analysis": {
    "risk_score": "Normal",
    "details": [],
    "risk_factors": [...],
    ...
  },
  "status": "COMPLETED"
}
```

## 🔧 Kod Yapısı

### Controller (main.py)
```python
def blackboard_controller(record_id):
    # 1. Blackboard'dan oku
    # 2. Uzmanları çalıştır
    # 3. Sonuçları blackboard'a yaz
```

### Knowledge Sources (experts.py)
```python
class KnowledgeSources:
    @staticmethod
    def ml_expert_module(input_data):
        # ML analizi yap
        return {...}
    
    @staticmethod
    def clinical_expert_module(input_data):
        # Klinik analiz yap
        return {...}
```

## 🚀 Genişletme Örnekleri

Yeni bir uzman eklemek için:

1. `experts.py`'ye yeni bir metod ekle:
```python
@staticmethod
def radiology_expert_module(input_data):
    # Radyoloji analizi
    return {...}
```

2. `blackboard_controller`'da çağır:
```python
rad_res = KnowledgeSources.radiology_expert_module(patient_data)
```

3. Blackboard'a yaz:
```python
cur.execute("""
    UPDATE heart_blackboard 
    SET radiology_analysis = %s
    WHERE id = %s
""", (json.dumps(rad_res), record_id))
```

## 📝 Özet

Blackboard Pattern bu projede:
- **Veritabanı** = Blackboard (merkezi veri deposu)
- **Controller** = Koordinatör (uzmanları yönetir)
- **Knowledge Sources** = Uzmanlar (ML ve Klinik)
- **Status** = Durum takibi (PENDING → COMPLETED)

Bu mimari sayesinde sistem modüler, esnek ve genişletilebilir bir yapıya sahiptir! 🎯

