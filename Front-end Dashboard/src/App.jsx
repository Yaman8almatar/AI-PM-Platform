import React, { useState } from 'react';
import Tree from 'react-d3-tree';
import ReactMarkdown from 'react-markdown';
import { Gantt, ViewMode } from 'gantt-task-react';
import "gantt-task-react/dist/index.css";

function App() {
  const [projectName, setProjectName] = useState("");
  const [loading, setLoading] = useState(false);
  
  // 1. حالة الـ WBS
  const [treeData, setTreeData] = useState({ 
    name: "ادخل اسم المشروع لبدء التوليد",  
    children: [{ name: "في انتظار البيانات..." }] 
  });
  
  // 2. حالة مخطط غانت
  const [tasks, setTasks] = useState([{
      start: new Date(),
      end: new Date(new Date().getTime() + 24 * 60 * 60 * 1000),
      name: 'في انتظار البيانات...',
      id: 'Task_0',
      type: 'task',
      progress: 0,
      isDisabled: true,
      styles: { progressColor: '#eeeeee', progressSelectedColor: '#dddddd' },
  }]);

  // 3. حالة سجل المخاطر (بديل الـ SRS)
  const [riskLogMd, setRiskLogMd] = useState("سيظهر سجل المخاطر هنا بعد التوليد...");

  const handleGenerate = async () => {
    if (!projectName.trim()) return;
    setLoading(true);
    
    try {
      // إرسال 'text' بدلاً من 'scope' لمطابقة الـ API Contract
      const response = await fetch('http://localhost:8000/api/generate-plan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: projectName })
      });
      
      if (!response.ok) throw new Error("خطأ في الاتصال بالسيرفر");
      const result = await response.json();
      
      // ==========================================
      // تحويل البيانات (Data Transformation)
      // ==========================================

      // A. تحويل WBS ليتناسب مع مكتبة react-d3-tree
      const formattedTree = {
        name: result.project_name || projectName,
        children: result.wbs.map(phase => ({
          name: phase.phase,
          children: phase.tasks.map(task => ({ name: task }))
        }))
      };
      setTreeData(formattedTree);

      // B. تحويل سجل المخاطر إلى Markdown Table
      let mdTable = `### ⚠️ سجل المخاطر (Risk Log)\n\n| الخطر | الاحتمالية | التأثير | خطة التخفيف |\n|---|---|---|---|\n`;
      result.risk_log.forEach(r => {
       mdTable += `| ${r.risk} | **${r.probability}** | **${r.impact}** | ${r.mitigation} | \n`;
      });
      setRiskLogMd(mdTable);

      // C. تحويل duration_days إلى تواريخ حقيقية لمكتبة Gantt
      let currentDate = new Date(); // يبدأ المشروع من اليوم
      const formattedTasks = result.gantt_data.map((task, index) => {
        const start = new Date(currentDate);
        const end = new Date(currentDate);
        end.setDate(end.getDate() + Math.max(1, task.duration_days)); // إضافة الأيام
        
        // تحديث التاريخ للمهمة التالية (تسلسل شلالي مبسط)
        currentDate = new Date(end);

        return {
          start: start,
          end: end,
          name: task.task_name,
          id: `Task_${index}`,
          type: 'task',
          progress: 0,
        };
      });
      setTasks(formattedTasks);

    } catch (error) {
      console.error(error);
      alert("حدث خطأ أثناء الاتصال بالسيرفر. تأكد من أن الباك إند يعمل على البورت 8000.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ width: '100%', height: '100vh', display: 'flex', flexDirection: 'column', padding: '15px', direction: 'rtl', backgroundColor: '#f4f7f6', overflow: 'hidden' }}>
      
      {/* الهيدر */}
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
           <style>{`@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }`}</style>
        </div>
      ) : (
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '15px', overflow: 'hidden' }}>
          <div style={{ display: 'grid', gridTemplateColumns: '1.5fr 1fr', gap: '15px', height: '55%' }}>
             <div style={{ background: '#fff', borderRadius: '10px', border: '1px solid #eee', position: 'relative' }}>
                <Tree data={treeData} orientation="vertical" translate={{ x: 200, y: 30 }} />
             </div>
             <div style={{ background: '#fff', borderRadius: '10px', border: '1px solid #eee', padding: '15px', overflowY: 'auto' }}>
                <ReactMarkdown>{riskLogMd}</ReactMarkdown>
             </div>
          </div>
          <div style={{ flex: 1, background: '#fff', borderRadius: '10px', border: '1px solid #eee', padding: '10px', direction: 'ltr', overflow: 'auto' }}>
            {tasks.length > 0 && <Gantt tasks={tasks} viewMode={ViewMode.Day} />}
          </div>
        </div>
      )}
    </div>
  );
}

export default App;