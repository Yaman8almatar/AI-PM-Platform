import pytest
from app.models.plan_models import GeneratePlanRequest

def test_generate_plan_request_valid():
    # اختبار: إدخال وصف مشروع صحيح وطويل بما يكفي
    valid_text = "تطبيق لإدارة المطاعم يشمل تسجيل الطلبات ونظام محاسبة شامل"
    request = GeneratePlanRequest(text=valid_text)
    assert request.text == valid_text # يجب أن يمر الاختبار بنجاح

def test_generate_plan_request_empty():
    # اختبار: إدخال نص فارغ أو مسافات فقط
    with pytest.raises(ValueError, match="النص المدخل فارغ"):
        GeneratePlanRequest(text="   ")

def test_generate_plan_request_short():
    # اختبار: إدخال نص قصير جداً (أقل من 10 أحرف)
    with pytest.raises(ValueError, match="وصف المشروع قصير جدًا"):
        GeneratePlanRequest(text="قصير جدا")