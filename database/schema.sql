-- VitalGuard 資料庫架構
-- 在 Supabase SQL Editor 中執行此腳本

-- ============================================
-- 1. Profiles 表 (使用者個人檔案)
-- ============================================
CREATE TABLE IF NOT EXISTS profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL UNIQUE REFERENCES auth.users(id) ON DELETE CASCADE,
    sharing_code VARCHAR(8) UNIQUE NOT NULL,
    age INTEGER CHECK (age >= 0 AND age <= 120),
    height DECIMAL(5,2) CHECK (height > 0),
    weight DECIMAL(5,2) CHECK (weight > 0),
    bmi DECIMAL(5,2) CHECK (bmi >= 0),
    chronic_disease TEXT,
    gender VARCHAR(20),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 自動更新 updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_profiles_updated_at
    BEFORE UPDATE ON profiles
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Profiles 索引
CREATE INDEX idx_profiles_user_id ON profiles(user_id);
CREATE INDEX idx_profiles_sharing_code ON profiles(sharing_code);

-- ============================================
-- 2. Health Measurements 表 (健康測量記錄)
-- ============================================
CREATE TABLE IF NOT EXISTS health_measurements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    systolic_bp INTEGER NOT NULL CHECK (systolic_bp BETWEEN 50 AND 250),
    diastolic_bp INTEGER NOT NULL CHECK (diastolic_bp BETWEEN 30 AND 150),
    pulse INTEGER CHECK (pulse BETWEEN 30 AND 200),
    bp_category VARCHAR(20) NOT NULL,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    deleted_at TIMESTAMP WITH TIME ZONE
);

-- Health Measurements 索引
CREATE INDEX idx_health_measurements_user_id ON health_measurements(user_id);
CREATE INDEX idx_health_measurements_created_at ON health_measurements(created_at DESC);
CREATE INDEX idx_health_measurements_deleted_at ON health_measurements(deleted_at);

-- ============================================
-- 3. Caregiver Patient Links 表 (監看者綁定)
-- ============================================
CREATE TABLE IF NOT EXISTS caregiver_patient_links (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    caregiver_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    patient_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(caregiver_id, patient_id)
);

-- Caregiver Links 索引
CREATE INDEX idx_caregiver_links_caregiver_id ON caregiver_patient_links(caregiver_id);
CREATE INDEX idx_caregiver_links_patient_id ON caregiver_patient_links(patient_id);
CREATE INDEX idx_caregiver_links_status ON caregiver_patient_links(status);

-- ============================================
-- 4. Dietary Knowledge Base 表 (臨床飲食數據)
-- ============================================
CREATE TABLE IF NOT EXISTS dietary_knowledge_base (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id VARCHAR(50),
    age INTEGER,
    gender VARCHAR(20),
    height_cm DECIMAL(5,2),
    weight_kg DECIMAL(5,2),
    bmi DECIMAL(5,2),
    chronic_disease TEXT,
    blood_pressure_systolic INTEGER,
    blood_pressure_diastolic INTEGER,
    cholesterol_level INTEGER,
    blood_sugar_level INTEGER,
    genetic_risk_factor VARCHAR(10),
    allergies TEXT,
    daily_steps INTEGER,
    exercise_frequency INTEGER,
    sleep_hours DECIMAL(3,1),
    alcohol_consumption VARCHAR(10),
    smoking_habit VARCHAR(10),
    dietary_habits VARCHAR(50),
    caloric_intake INTEGER,
    protein_intake INTEGER,
    carbohydrate_intake INTEGER,
    fat_intake INTEGER,
    preferred_cuisine VARCHAR(50),
    food_aversions TEXT,
    recommended_calories INTEGER,
    recommended_protein INTEGER,
    recommended_carbs INTEGER,
    recommended_fats INTEGER,
    recommended_meal_plan VARCHAR(100),
    bp_category VARCHAR(20),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Dietary Knowledge Base 索引 (優化 KNN 查詢)
CREATE INDEX idx_dietary_kb_age ON dietary_knowledge_base(age);
CREATE INDEX idx_dietary_kb_bmi ON dietary_knowledge_base(bmi);
CREATE INDEX idx_dietary_kb_bp_category ON dietary_knowledge_base(bp_category);
CREATE INDEX idx_dietary_kb_composite ON dietary_knowledge_base(age, bmi, bp_category);

-- ============================================
-- 5. RLS (Row Level Security) 安全政策
-- ============================================

-- 啟用 RLS
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE health_measurements ENABLE ROW LEVEL SECURITY;
ALTER TABLE caregiver_patient_links ENABLE ROW LEVEL SECURITY;
ALTER TABLE dietary_knowledge_base ENABLE ROW LEVEL SECURITY;

-- Profiles RLS: 使用者可讀寫自己的檔案
CREATE POLICY "Users can view own profile" ON profiles
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own profile" ON profiles
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own profile" ON profiles
    FOR UPDATE USING (auth.uid() = user_id);

-- Health Measurements RLS: 使用者可 CRUD 自己的記錄
CREATE POLICY "Users can view own measurements" ON health_measurements
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own measurements" ON health_measurements
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own measurements" ON health_measurements
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own measurements" ON health_measurements
    FOR DELETE USING (auth.uid() = user_id);

-- Caregiver Links RLS: 參與者可查看
CREATE POLICY "Caregivers can view their links" ON caregiver_patient_links
    FOR SELECT USING (auth.uid() = caregiver_id OR auth.uid() = patient_id);

CREATE POLICY "Caregivers can create links" ON caregiver_patient_links
    FOR INSERT WITH CHECK (auth.uid() = caregiver_id);

-- Dietary Knowledge Base RLS: 所有登入者唯讀
CREATE POLICY "Authenticated users can view dietary data" ON dietary_knowledge_base
    FOR SELECT USING (auth.role() = 'authenticated');

-- ============================================
-- 6. 輔助函數
-- ============================================

-- 函數: 根據 Sharing Code 查找使用者
CREATE OR REPLACE FUNCTION get_user_by_sharing_code(code VARCHAR(8))
RETURNS TABLE (user_id UUID, sharing_code VARCHAR(8)) AS $$
BEGIN
    RETURN QUERY
    SELECT p.user_id, p.sharing_code
    FROM profiles p
    WHERE p.sharing_code = code;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ============================================
-- 說明
-- ============================================
-- 執行此腳本後，請執行:
-- 1. 在 Supabase Dashboard 啟用 Email Auth
-- 2. 執行 scripts/import_clinical_data.py 匯入臨床數據
-- 3. 測試 API 端點
