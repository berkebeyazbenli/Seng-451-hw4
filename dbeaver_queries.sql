-- ============================================
-- DBeaver için PostgreSQL RDS Sorguları
-- ============================================

-- 1. Tüm tabloları listele
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public'
ORDER BY table_name;

-- 2. heart_blackboard tablosu yapısını göster
SELECT 
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_name = 'heart_blackboard'
ORDER BY ordinal_position;

-- 3. Tüm kayıtları göster (basit görünüm - DBeaver için önerilen)
SELECT 
    id,
    status,
    input_data->>'age' as age,
    input_data->>'trestbps' as blood_pressure,
    input_data->>'chol' as cholesterol,
    ml_analysis->>'result_text' as ml_result,
    ROUND((ml_analysis->>'probability')::numeric * 100, 2) as ml_probability_percent,
    clinical_analysis->>'risk_score' as risk_score,
    updated_at
FROM heart_blackboard
ORDER BY id DESC;

-- 3a. JSONB sütunlarını okunabilir JSON string olarak göster
SELECT 
    id,
    status,
    input_data::text as input_data_json,
    ml_analysis::text as ml_analysis_json,
    clinical_analysis::text as clinical_analysis_json,
    updated_at
FROM heart_blackboard
WHERE status = 'COMPLETED'
ORDER BY id DESC;

-- 4. Tüm kayıtları detaylı göster (JSON formatında - DBeaver için)
-- JSONB'yi text'e çevirerek görüntüle
SELECT 
    id,
    status,
    input_data::text as input_data,
    ml_analysis::text as ml_analysis,
    clinical_analysis::text as clinical_analysis,
    updated_at
FROM heart_blackboard
ORDER BY id DESC;

-- 4a. Sadece tamamlanan kayıtları detaylı göster
SELECT 
    id,
    status,
    jsonb_pretty(input_data) as input_data_formatted,
    jsonb_pretty(ml_analysis) as ml_analysis_formatted,
    jsonb_pretty(clinical_analysis) as clinical_analysis_formatted,
    updated_at
FROM heart_blackboard
WHERE status = 'COMPLETED'
ORDER BY id DESC;

-- 5. Status dağılımı
SELECT 
    status,
    COUNT(*) as count
FROM heart_blackboard
GROUP BY status
ORDER BY count DESC;

-- 6. Son 10 kayıt
SELECT 
    id,
    status,
    input_data->>'age' as age,
    ml_analysis->>'result_text' as ml_result,
    clinical_analysis->>'risk_score' as risk_score,
    updated_at
FROM heart_blackboard
ORDER BY id DESC
LIMIT 10;

-- 7. Belirli bir kayıt (ID ile) - DBeaver için formatlanmış
-- ID'yi değiştirin: WHERE id = 11
SELECT 
    id,
    status,
    jsonb_pretty(input_data) as input_data,
    jsonb_pretty(ml_analysis) as ml_analysis,
    jsonb_pretty(clinical_analysis) as clinical_analysis,
    updated_at
FROM heart_blackboard
WHERE id = 11;

-- 7a. Belirli bir kayıt - basit görünüm
SELECT 
    id,
    status,
    input_data->>'age' as age,
    input_data->>'trestbps' as blood_pressure,
    input_data->>'chol' as cholesterol,
    ml_analysis->>'result_text' as ml_result,
    ml_analysis->>'probability' as ml_probability,
    ml_analysis->>'confidence_level' as confidence,
    clinical_analysis->>'risk_score' as risk_score,
    clinical_analysis->>'total_risk_factors' as risk_factors_count,
    updated_at
FROM heart_blackboard
WHERE id = 11;

-- 8. Sadece tamamlanan kayıtlar
SELECT 
    id,
    input_data->>'age' as age,
    ml_analysis->>'result_text' as ml_result,
    ml_analysis->>'probability' as ml_probability,
    clinical_analysis->>'risk_score' as risk_score
FROM heart_blackboard
WHERE status = 'COMPLETED'
ORDER BY id DESC;

-- 9. Hata olan kayıtlar
SELECT 
    id,
    status,
    ml_analysis->>'error' as error_message,
    updated_at
FROM heart_blackboard
WHERE status = 'ERROR'
ORDER BY id DESC;

-- 10. Tablo istatistikleri
SELECT 
    COUNT(*) as total_records,
    COUNT(CASE WHEN status = 'COMPLETED' THEN 1 END) as completed,
    COUNT(CASE WHEN status = 'PENDING' THEN 1 END) as pending,
    COUNT(CASE WHEN status = 'ERROR' THEN 1 END) as errors
FROM heart_blackboard;

-- ============================================
-- DBeaver'da JSONB Görüntüleme İpuçları
-- ============================================
-- 
-- 1. JSONB sütunlarını görmek için:
--    - jsonb_pretty() kullanın (formatlanmış JSON)
--    - ::text kullanın (düz metin)
--    - -> veya ->> operatörleri ile belirli alanları çıkarın
--
-- 2. DBeaver'da JSONB sütununa çift tıklayınca
--    JSON viewer açılır (eğer yüklüyse)
--
-- 3. Tablo görünümünde JSONB sütunları NULL görünüyorsa:
--    - SQL Editor'de yukarıdaki sorguları kullanın
--    - jsonb_pretty() veya ::text kullanın
--
-- 4. En son tamamlanan kayıtları görmek için:
--    SELECT * FROM heart_blackboard WHERE status = 'COMPLETED' ORDER BY id DESC;

