import React, { useState } from 'react';
import Tree from 'react-d3-tree';
import ReactMarkdown from 'react-markdown';
import { Gantt, ViewMode } from 'gantt-task-react';
import "gantt-task-react/dist/index.css";

function App() {
  const [projectName, setProjectName] = useState("");
  const [loading, setLoading] = useState(false); // حالة التحميل
  
  // بيانات افتراضية فارغة لحين وصول رد السيرفر
  const [data, setData] = useState({ name: "ادخل اسم المشروع لبدء التوليد",  children: [{ name: "المرحلة الأولى" }, { name: "المرحلة الثانية"});
  const [tasks, setTasks] = useState([{
      start: new Date(),
      end: new Date(new Date().getTime() + 24 * 60 * 60 * 1000),
      name: 'في انتظار البيانات...',
      id: 'Task 0',
      type: 'task',
      progress: 0,
      isDisabled: true,
      styles: { progressColor: '#eeeeee', progressSelectedColor: '#dddddd' },
    }]);
  const [srs, setSrs] = useState("سيظهر محتوى الـ SRS هنا بعد التوليد...");

  // دالة الربط مع Backend (مهمة عبد العزيز)
  const handleGenerate = async () => {
    if (!projectName.trim()) return;
    setLoading(true);
    
    try {
      // محاولة الاتصال بعبد العزيز
      const response = await fetch('http://localhost:8000/api/generate-plan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ scope: projectName })
      });
      const result = await response.json();
      
      // إذا نجح الاتصال، نحدث البيانات
      setData(result.wbs);
      setSrs(result.srs);
      setTasks(result.gantt.map(t => ({ ...t, start: new Date(t.start), end: new Date(t.end) })));

    } catch (error) {
      console.warn("السيرفر غير جاهز بعد، سأعرض بيانات تجريبية...");
      
      // بيانات وهمية تظهر فوراً لتجربة الواجهة
      setData({
        name: projectName,
        children: [{ name: "تحليل النظام" }, { name: "بناء القاعدة" }]
      });
      setTasks([
        { start: new Date(), end: new Date(new Date().getTime() + 10**8), name: 'مهمة تجريبية 1', id: 'T1', type: 'task', progress: 50 },
        { start: new Date(), end: new Date(new Date().getTime() + 2*10**8), name: 'مهمة تجريبية 2', id: 'T2', type: 'task', progress: 10 }
      ]);
      setSrs("### وثيقة تجريبية\nتم التوليد بنجاح (وضع الاختبار)");
      
    } finally {
      setTimeout(() => setLoading(false), 1500); // تأخير بسيط لمحاكاة تفكير الـ AI
    }
  };

  return (
    <div style={{ width: '100%', height: '100vh', display: 'flex', flexDirection: 'column', padding: '15px', direction: 'rtl', backgroundColor: '#f4f7f6', overflow: 'hidden' }}>
      
      {/* الهيدر مع زر التوليد */}
      <div style={{ background: '#fff', padding: '10px 20px', borderRadius: '10px', marginBottom: '15px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', boxShadow: '0 2px 5px rgba(0,0,0,0.05)' }}>
        <h3 style={{ margin: 0, color: '#1a73e8' }}>🚀 AI PM Dashboard</h3>
        <div style={{ display: 'flex', gap: '8px' }}>
          <input 
            value={projectName} 
            onChange={(e) => setProjectName(e.target.value)} 
            placeholder="أدخل وصف أو اسم المشروع..." 
            style={{ padding: '8px', width: '300px', borderRadius: '5px', border: '1px solid #ddd' }}
          />
          <button 
            onClick={handleGenerate} 
            disabled={loading}
            style={{ padding: '8px 20px', backgroundColor: loading ? '#ccc' : '#34a853', color: '#fff', border: 'none', borderRadius: '5px', cursor: 'pointer' }}
          >
            {loading ? "جاري التوليد..." : "توليد الخطة ✨"}
          </button>
        </div>
      </div>

      {loading ? (
        <div style={{ flex: 1, display: 'flex', justifyContent: 'center', alignItems: 'center', flexDirection: 'column' }}>
           <div className="spinner" style={{ border: '4px solid #f3f3f3', borderTop: '4px solid #3498db', borderRadius: '50%', width: '40px', height: '40px', animation: 'spin 2s linear infinite' }}></div>
           <p style={{ marginTop: '10px' }}>جاري تحليل البيانات عبر الذكاء الاصطناعي...</p>
           <style>{@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }}</style>
        </div>
      ) : (
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '15px', overflow: 'hidden' }}>
          {/* هنا تضع كود الـ Grid (الشجرة و SRS و Gantt) كما فعلنا سابقاً */}
          {/* سيعمل الكود تلقائياً فور وصول البيانات إلى الحالة (State) */}
          <div style={{ display: 'grid', gridTemplateColumns: '1.5fr 1fr', gap: '15px', height: '55%' }}>

<div style={{ background: '#fff', borderRadius: '10px', border: '1px solid #eee', position: 'relative' }}>
                <Tree data={data} orientation="vertical" translate={{ x: 200, y: 30 }} />
             </div>
             <div style={{ background: '#fff', borderRadius: '10px', border: '1px solid #eee', padding: '15px', overflowY: 'auto' }}>
                <ReactMarkdown>{srs}</ReactMarkdown>
             </div>
          </div>
          <div style={{ flex: 1, background: '#fff', borderRadius: '10px', border: '1px solid #eee', padding: '10px', direction: 'ltr', overflow: 'auto' }}>
            {tasks.length > 0 && <Gantt tasks={tasks} viewMode={ViewMode.Day} locale="ara" />}
          </div>
        </div>
      )}
    </div>
  );
}

export default App;