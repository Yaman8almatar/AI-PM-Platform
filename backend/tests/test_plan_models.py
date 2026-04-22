import pytest
from pydantic import ValidationError
from app.models.plan_models import GeneratePlanRequest

def test_generate_plan_request_valid():
    valid_text = "تطبيق لإدارة المطاعم يشمل تسجيل الطلبات ونظام محاسبة شامل"
    request = GeneratePlanRequest(text=valid_text)
    assert request.text == valid_text 

def test_generate_plan_request_empty():
    # الآن نتوقع أن يطلق الكود خطأ ValidationError عند تمرير نص فارغ
    with pytest.raises(ValidationError):
        GeneratePlanRequest(text="   ")

def test_generate_plan_request_short():
    # نتوقع خطأ ValidationError عند تمرير نص قصير
    with pytest.raises(ValidationError):
        GeneratePlanRequest(text="قصير جدا")