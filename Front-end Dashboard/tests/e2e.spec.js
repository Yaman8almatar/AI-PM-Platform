import { test, expect } from '@playwright/test';

test('يجب أن يقوم المستخدم بتوليد خطة مشروع بنجاح مع تمرير استعراضي بطيء', async ({ page }) => {
  // 1. زيادة وقت الاختبار الكلي ليتسع للانتظار والتمرير (80 ثانية)
  test.setTimeout(80000);

  await page.goto('/');

  // 2. تعبئة البيانات والضغط على الزر
  const inputField = page.getByPlaceholder('اكتب هنا كل ما يخطر ببالك... الأهداف، المنصات المستهدفة، الميزات المطلوبة...');
  await inputField.fill('تطبيق متكامل لإدارة الصيدليات يشمل تتبع المخزون، تنبيهات انتهاء الصلاحية، ونظام مبيعات ذكي');
  
  const generateButton = page.locator('button', { hasText: 'توليد المخططات والمخاطر ⚡' });
  await generateButton.click();

  // 3. انتظار ظهور شاشة النتائج (ننتظر ظهور بطاقة الإحصائيات)
  // الروبوت سينتظر هنا حتى ينتهي الذكاء الاصطناعي من عمله تماماً
  await expect(page.locator('text=إجمالي المهام المجدولة')).toBeVisible({ timeout: 50000 });

  // 4. ثبات لمدة ثانيتين للاستمتاع بمنظر النتائج الأولى
  await page.waitForTimeout(2000);

  // 5. 🚀 منطق التمرير البطيء لمدة 10 ثوانٍ 🚀
  // سنقوم بالنزول 250 بكسل كل ثانية لمدة 10 مرات
  for (let i = 0; i < 10; i++) {
    await page.evaluate(() => {
      window.scrollBy({
        top: 250,           // المسافة التي سينزلها في كل خطوة
        behavior: 'smooth'  // تجعل الحركة ناعمة وانسيابية
      });
    });
    
    // الانتظار لمدة ثانية واحدة بين كل تمريرة
    await page.waitForTimeout(1000); 
  }

  // انتظار أخير لرؤية مخطط غانت في أسفل الصفحة
  await page.waitForTimeout(2000);
});