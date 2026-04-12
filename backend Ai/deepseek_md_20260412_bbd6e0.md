# Project Planning API

## التشغيل

```bash
# 1. إنشاء بيئة افتراضية
python -m venv venv
source venv/bin/activate  # أو .\venv\Scripts\activate

# 2. تثبيت المتطلبات
pip install -r requirements.txt

# 3. نسخ ملف البيئة
cp .env.example .env

# 4. تشغيل الخادم
python run.py
# أو
uvicorn app.main:app --reload