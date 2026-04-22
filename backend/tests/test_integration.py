import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pytest
from fastapi.testclient import TestClient
from app.main import app  

# إنشاء عميل وهمي يحاكي الواجهة الأمامية (React)
client = TestClient(app)

def test_health_check_endpoint():
    # 1. اختبار نقطة فحص السيرفر (Health Check)
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"

def test_api_generate_plan_validation():
    # 2. اختبار تكامل طبقة الـ API مع طبقة التحقق (Models)
    # نرسل طلباً يحتوي على وصف مشروع قصير جداً لنرى كيف سيتصرف السيرفر ككل
    payload = {"text": "قصير جدا"}
    response = client.post("/api/generate-plan", json=payload)
    
    # يجب أن يتدخل السيرفر ويرفض الطلب ويرجع كود 422 (Unprocessable Entity)
    assert response.status_code == 422 
    
    # نتأكد أن رسالة الخطأ تفصيلية وتوضح أن المشكلة في حقل 'text'
    error_detail = response.json()["detail"][0]
    assert error_detail["loc"] == ["body", "text"]