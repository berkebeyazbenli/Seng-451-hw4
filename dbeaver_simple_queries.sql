-- ============================================
-- DBeaver için Basit ve Çalışan Sorgular
-- Her sorguyu TEK TEK çalıştırın (Ctrl+Enter)
-- ============================================

-- SORGU 1: Tamamlanan kayıtları basit görünümle göster
SELECT 
    id,
    status,
    input_data->>'age' as age,
    input_data->>'trestbps' as blood_pressure,
    input_data->>'chol' as cholesterol,
    ml_analysis->>'result_text' as ml_result,
    ml_analysis->>'probability' as ml_probability,
    clinical_analysis->>'risk_score' as risk_score,
    updated_at
FROM heart_blackboard
WHERE status = 'COMPLETED'
ORDER BY id DESC;

-- SORGU 2: JSONB sütunlarını text olarak göster (DBeaver için)
SELECT 
    id,
    status,
    input_data::text as input_data,
    ml_analysis::text as ml_analysis,
    clinical_analysis::text as clinical_analysis,
    updated_at
FROM heart_blackboard
WHERE status = 'COMPLETED'
ORDER BY id DESC;

-- SORGU 3: Formatlanmış JSON göster (jsonb_pretty ile)
SELECT 
    id,
    status,
    jsonb_pretty(input_data) as input_data,
    jsonb_pretty(ml_analysis) as ml_analysis,
    jsonb_pretty(clinical_analysis) as clinical_analysis,
    updated_at
FROM heart_blackboard
WHERE status = 'COMPLETED'
ORDER BY id DESC;

-- SORGU 4: Son 5 tamamlanan kayıt (en basit)
SELECT 
    id,
    status,
    input_data->>'age' as age,
    ml_analysis->>'result_text' as ml_result,
    clinical_analysis->>'risk_score' as risk_score
FROM heart_blackboard
WHERE status = 'COMPLETED'
ORDER BY id DESC
LIMIT 5;

-- SORGU 5: Tüm kayıtların status dağılımı
SELECT 
    status,
    COUNT(*) as count
FROM heart_blackboard
GROUP BY status
ORDER BY count DESC;

-- SORGU 6: Belirli bir ID'yi göster (ID'yi değiştirin)
SELECT 
    id,
    status,
    input_data::text as input_data,
    ml_analysis::text as ml_analysis,
    clinical_analysis::text as clinical_analysis
FROM heart_blackboard
WHERE id = 16;

-- SORGU 7: Tüm kayıtları listele (basit)
SELECT 
    id,
    status,
    input_data->>'age' as age,
    updated_at
FROM heart_blackboard
ORDER BY id DESC;

