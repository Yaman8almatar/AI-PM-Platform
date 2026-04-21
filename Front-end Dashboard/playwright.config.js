import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './tests', // المجلد الذي سنضع فيه الاختبارات
  use: {
    baseURL: 'http://localhost:5173', // رابط تشغيل الواجهة (Vite)
    headless: false, // نجعلها false لكي نرى المتصفح وهو يتحرك أمامنا!
    viewport: { width: 1280, height: 720 },
  },
});