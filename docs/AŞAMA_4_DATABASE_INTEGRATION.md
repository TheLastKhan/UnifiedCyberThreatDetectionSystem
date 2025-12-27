# AŞAMA 4: Database & Kaggle Data Integration

**Status**: IN PROGRESS  
**Date**: 2025-12-08  
**Estimated Duration**: 6-8 hours  
**Completed**: ~1.5 hours (Database schema migration)

---

## 📋 Overview

AŞAMA 4 iki kritik görev içerir:

1. **4.1 Database Schema Genişletme** ✅ (TAMAMLANDI)
   - Yeni alanlar ekle: severity, attack_type
   - Migration script oluştur
   - Existing data migration

2. **4.2 Kaggle Veri İntegrasyonu** ⏳ (DEVAM EDECEK)
   - Veri indir (4 dataset)
   - CSV parsing
   - Database'e import et

---

## ✅ TAMAMLANAN: Database Schema Migration

### Yapılan İşler:

#### 1. Migration Script Oluşturuldu
**Dosya**: `migrations/001_add_severity_and_attack_type.py` (350+ satır)

**Özellikleri**:
- ✅ Severity column ekleme (emails tablosuna)
- ✅ Attack_type column ekleme (web_logs tablosuna)
- ✅ Detection_method column (emails)
- ✅ ML_confidence column (web_logs)
- ✅ Index oluşturma
- ✅ Existing data update
- ✅ Rollback desteği

**Kullanım**:
```bash
# Migration'ı çalıştır
python run_migrations.py

# Migration'ı geri al
python run_migrations.py rollback

# Status kontrol et
python run_migrations.py status
```

#### 2. Database Models Güncellendi
**Dosya**: `src/database/models.py`

**Email Model Yeni Alanları**:
```python
severity: VARCHAR(20)  # phishing, malware, spam, suspicious, legitimate
detection_method: VARCHAR(50)  # tfidf, bert, fasttext, ensemble
```

**WebLog Model Yeni Alanları**:
```python
attack_type: VARCHAR(50)  # sql_injection, xss, ddos, brute_force, etc.
ml_confidence: FLOAT  # Anomaly detection confidence (0-1)
```

#### 3. Migration Runner Oluşturuldu
**Dosya**: `run_migrations.py` (260+ satır)

**Özellikler**:
- ✅ Database connection verification
- ✅ Prerequisites check
- ✅ Migration execution
- ✅ Rollback support
- ✅ Status reporting

---

## 📊 Enum Definitions

### Email Severity Levels
```python
SEVERITY_ENUM = [
    'phishing',      # Advanced phishing attempts
    'malware',       # Malware distribution
    'spam',          # Spam/UCE
    'suspicious',    # Suspicious but unconfirmed
    'legitimate'     # Clean email
]
```

### Web Attack Types
```python
ATTACK_TYPE_ENUM = [
    'sql_injection',         # SQL injection attempts
    'xss',                   # Cross-site scripting
    'ddos',                  # Distributed denial of service
    'brute_force',           # Authentication brute force
    'malware_distribution',  # Malware spreading
    'credential_theft',      # Credential harvesting
    'data_exfiltration',     # Data theft
    'command_injection',     # Remote command execution
    'path_traversal',        # Directory traversal
    'file_upload',           # Malicious file upload
    'authentication_bypass', # Authentication bypass
    'business_logic',        # Business logic attacks
    'unknown'                # Unknown attack type
]
```

---

## 🔄 Migration Details

### Changes Made

#### Table: `emails`

| Column | Type | Index | Default | Note |
|--------|------|-------|---------|------|
| severity | VARCHAR(20) | ✓ | 'legitimate' | **NEW** - Threat severity classification |
| detection_method | VARCHAR(50) | ✓ | 'tfidf' | **NEW** - Which model detected threat |

**Indexes Created**:
- `idx_email_severity` - For filtering by severity
- `idx_email_detection_method` - For model performance tracking

#### Table: `web_logs`

| Column | Type | Index | Default | Note |
|--------|------|-------|---------|------|
| attack_type | VARCHAR(50) | ✓ | 'unknown' | **NEW** - Type of attack detected |
| ml_confidence | FLOAT | - | 0.0 | **NEW** - ML model confidence score |

**Indexes Created**:
- `idx_web_log_attack_type` - For attack categorization

#### Table: `migrations` (NEW)

Tracks all database migrations

| Column | Type | Purpose |
|--------|------|---------|
| id | SERIAL | Primary key |
| version | VARCHAR(50) | Migration version (001, 002, etc.) |
| description | TEXT | Migration description |
| status | VARCHAR(20) | 'completed', 'pending', 'failed' |
| applied_at | TIMESTAMP | When migration was applied |

---

## 📈 Data Migration Strategy

### For Existing Emails

```sql
UPDATE emails 
SET severity = CASE 
    WHEN prediction = 1 AND risk_score >= 75 THEN 'phishing'
    WHEN prediction = 1 AND risk_score < 75 THEN 'suspicious'
    WHEN prediction = 0 THEN 'legitimate'
    ELSE 'suspicious'
END,
detection_method = 'tfidf'  -- Default to TF-IDF for old records
WHERE severity IS NULL
```

### For Existing Web Logs

```sql
UPDATE web_logs 
SET attack_type = CASE 
    WHEN indicators LIKE '%sql%' THEN 'sql_injection'
    WHEN indicators LIKE '%xss%' THEN 'xss'
    WHEN indicators LIKE '%ddos%' THEN 'ddos'
    WHEN is_anomaly = true THEN 'unknown'
    ELSE 'unknown'
END
WHERE attack_type IS NULL
```

---

## 🚀 Next Steps: Kaggle Data Integration

### AŞAMA 4.2: Kaggle Veri İntegrasyonu (⏳ SONRA)

**Tahmini Süre**: 3-4 saat

#### Step 1: Kaggle API Setup (15-20 dakika)
1. Kaggle account oluştur: https://www.kaggle.com/
2. API token indir: https://www.kaggle.com/settings/account
3. Token'ı yerleştir:
   - **Windows**: `C:\Users\YourUsername\.kaggle\kaggle.json`
   - **Linux/Mac**: `~/.kaggle/kaggle.json`
4. Permissions ayarla: `chmod 600 ~/.kaggle/kaggle.json` (Linux/Mac)

#### Step 2: Veri İndirme (1-2 saat)
```bash
python download_kaggle_datasets.py
```

**Datasets**:
1. Phishing Website Detection (~50MB)
2. Email Spam Classification (~20MB)
3. Malicious URL Detection (~80MB)
4. Web Attack Logs (~30MB)

#### Step 3: Data Import (30-45 dakika)
```bash
python import_kaggle_data.py
```

**Process**:
- CSV parsing
- Data cleaning
- Duplicate detection
- PostgreSQL batch insert
- Validation

---

## 📋 Current Status

### ✅ Completed
- [x] Migration script (001_add_severity_and_attack_type.py)
- [x] Migration runner (run_migrations.py)
- [x] Database models updated
- [x] Enum definitions created
- [x] Data migration strategy

### ⏳ Ready to Execute
- [ ] Run migration: `python run_migrations.py`
- [ ] Verify migration: `python run_migrations.py status`

### 🔴 Next Phase
- [ ] Setup Kaggle API
- [ ] Download datasets
- [ ] Import to database

---

## 💾 Files Created/Modified

### New Files
1. `migrations/001_add_severity_and_attack_type.py` (350+ lines)
2. `run_migrations.py` (260+ lines)

### Modified Files
1. `src/database/models.py` - Added 4 new columns + updated to_dict()

### Total Changes
- **Lines Added**: ~610
- **Files Changed**: 3
- **Database Impact**: High (schema changes)

---

## 🔐 Rollback Procedure

If something goes wrong:

```bash
# Rollback migration
python run_migrations.py rollback

# This will:
# - Remove severity column from emails
# - Remove attack_type column from web_logs
# - Remove detection_method column from emails
# - Remove ml_confidence column from web_logs
# - Keep existing data intact (columns removed only)
```

---

## 📊 Testing Checklist

After migration completes:

- [ ] Database connection works
- [ ] New columns exist in emails table
- [ ] New columns exist in web_logs table
- [ ] Indexes created successfully
- [ ] Migration tracking table populated
- [ ] Existing data migrated (severity/attack_type set)
- [ ] ORM models work with new columns
- [ ] to_dict() methods include new fields

---

## 📝 Next Execution Steps

### To Complete AŞAMA 4.2:

1. **Get Kaggle API Key**
   ```bash
   # Download from https://www.kaggle.com/settings/account
   # Place at ~/.kaggle/kaggle.json
   ```

2. **Download Datasets**
   ```bash
   python download_kaggle_datasets.py
   # Expected time: 1-2 hours
   ```

3. **Import to Database**
   ```bash
   python import_kaggle_data.py
   # Expected time: 30-45 minutes
   # Expected records: 50,000+ rows
   ```

4. **Verify Data**
   ```bash
   python -c "
   from src.database.connection import get_session
   from src.database.models import Email, WebLog
   session = get_session()
   print(f'Emails: {session.query(Email).count()}')
   print(f'Web Logs: {session.query(WebLog).count()}')
   session.close()
   "
   ```

---

## 🎯 Success Criteria

AŞAMA 4 başarıyla tamamlandığında:

✅ Database migration executed without errors
✅ 4 new columns added to tables
✅ 50,000+ records imported from Kaggle
✅ All data with proper severity/attack_type classification
✅ Indexes created for performance
✅ ORM models working with new fields
✅ Tests still passing (38/38)

---

## 📞 Troubleshooting

### Migration Fails
1. Check PostgreSQL is running
2. Verify DATABASE_URL in config
3. Check table 'emails' and 'web_logs' exist
4. Review logs for specific errors

### Kaggle API Issues
1. Verify kaggle.json exists
2. Check file permissions
3. Verify API key is valid
4. Check internet connection

### Data Import Issues
1. Check CSV file format
2. Verify column names match
3. Check for duplicate handling
4. Review import_kaggle_data.py logs

---

**Next Phase**: AŞAMA 5 (Security APIs - VirusTotal Integration)
