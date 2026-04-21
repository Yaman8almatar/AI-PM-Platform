from locust import HttpUser, task, between

class AIProjectUser(HttpUser):
    # المستخدم الوهمي سينتظر من 1 إلى 5 ثوانٍ بين كل ضغطة وأخرى (ليحاكي المستخدم البشري)
    wait_time = between(1, 5)

    @task(3) 
    def check_health(self):
        # مهمة خفيفة (بوزن 3): 3 أضعاف المستخدمين سيتصفحون الموقع فقط ويتأكدون أنه يعمل
        self.client.get("/health")

    @task(1)
    def generate_plan(self):
        # مهمة ثقيلة (بوزن 1): مستخدم يطلب من الذكاء الاصطناعي توليد خطة كاملة
        payload = {"text": "تطبيق متكامل لإدارة العيادات الطبية وحجز المواعيد إلكترونياً"}
        
        # نضع اسم المهمة (name) لكي تظهر بشكل مرتب في تقرير الأداء
        self.client.post("/api/generate-plan", json=payload, name="Generate AI Plan")