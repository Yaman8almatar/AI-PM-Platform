import React, { useState,useRef } from 'react';
import Tree from 'react-d3-tree';
import ReactMarkdown from 'react-markdown';
import { Gantt, ViewMode } from 'gantt-task-react';
import "gantt-task-react/dist/index.css";
import { toPng } from 'html-to-image';

function App() {
  const [projectName, setProjectName] = useState("");
  const [loading, setLoading] = useState(false);
  const treeContainerRef = React.useRef(null);
  const [treeData, setTreeData] = useState({ 
    name: "ادخل اسم المشروع لبدء التوليد",  
    children: [{ name: "في انتظار البيانات..." }]
  }
  
);
  
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

  const [riskLogMd, setRiskLogMd] = useState("سيظهر سجل المخاطر هنا بعد التوليد...");

  // دالة مخصصة لرسم العقد (Nodes) لحل مشكلة التداخل ودعم العربية
  const renderRectSvgNode = ({ nodeDatum, toggleNode }) => (
    <g>
      <rect 
        width="140" 
        height="40" 
        x="-70" 
        y="-20" 
        rx="10"
        fill={nodeDatum.children ? "#1a73e8" : "#34a853"} 
        onClick={toggleNode}
      />
      <text 
        fill="white" 
        strokeWidth="0.5" 
        x="0" 
        y="5" 
        textAnchor="middle" 
        style={{ fontSize: '12px', fontWeight: 'bold', fontFamily: 'Arial' }}
      >
        {nodeDatum.name}
      </text>
    </g>
  );
// دالة تحميل الصورة المعدلة يدوياً لإخفاء الزر
const downloadImage = () => {
  if (treeContainerRef.current === null) return;
  
  // 1. أوجد زر التحميل داخل هذا المرجع وأخفِه
  // نستخدم الـ querySelector للبحث عن وسم button
  const buttonToRemove = treeContainerRef.current.querySelector('button');
  if (buttonToRemove) {
    buttonToRemove.style.opacity = '0'; // اجعله شفافاً تماماً
  }

  // 2. خذ الصورة الآن (بدون الزر)
  // تأكد من إضافة backgroundColor لضمان خلفية بيضاء نقية
  toPng(treeContainerRef.current, { cacheBust: true, backgroundColor: '#ffffff' })
    .then((dataUrl) => {
      const link = document.createElement('a');
      link.download = `WBS-${projectName || 'project'}.png`;
      link.href = dataUrl;
      link.click();
    })
    .catch((err) => {
      console.error(err);
      alert("حدث خطأ أثناء تحميل الصورة.");
    })
    .finally(() => {
      // 3. أعد إظهار الزر فوراً بعد انتهاء العملية (في كل الأحوال)
      if (buttonToRemove) {
        buttonToRemove.style.opacity = '1'; // اجعله مرئياً مجدداً
      }
    });
};
  const handleGenerate = async () => {
    if (!projectName.trim()) return;
    setLoading(true);
    
    try {
      const response = await fetch('http://localhost:8000/api/generate-plan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: projectName })
      });
      
      if (!response.ok) throw new Error("خطأ في الاتصال بالسيرفر");
      const result = await response.json();
      
      const formattedTree = {
        name: result.project_name || projectName,
        children: result.wbs.map(phase => ({
          name: phase.phase,
          children: phase.tasks.map(task => ({ name: task }))
        }))
      };
      setTreeData(formattedTree);

      let mdTable = `### ⚠️ سجل المخاطر (Risk Log)\n\n| الخطر | الاحتمالية | التأثير | خطة التخفيف |\n|---|---|---|---|\n`;
      result.risk_log.forEach(r => {
       mdTable +=` | ${r.risk} | **${r.probability}** | **${r.impact}** | ${r.mitigation} |\n`;
      });
      setRiskLogMd(mdTable);

      let currentDate = new Date();
      const formattedTasks = result.gantt_data.map((task, index) => {
        const start = new Date(currentDate);
        const end = new Date(currentDate);
        end.setDate(end.getDate() + Math.max(1, task.duration_days));
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
      alert("حدث خطأ أثناء الاتصال بالسيرفر.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ width: '100%', height: '100vh', display: 'flex', flexDirection: 'column', padding: '15px', direction: 'rtl', backgroundColor: '#f4f7f6', overflow: 'hidden' }}>
      
      <div style={{ background: '#fff', padding: '10px 20px', borderRadius: '10px', marginBottom: '15px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', boxShadow: '0 2px 5px rgba(0,0,0,0.05)' }}>
        <h3 style={{ margin: 0, color: '#1a73e8' }}>🚀 AI PM Dashboard - Sprint 1</h3>
        <div style={{ display: 'flex', gap: '8px' }}>
          <input 
            value={projectName}
            onChange={(e) => setProjectName(e.target.value)} 
            placeholder="أدخل وصف المشروع..." 
            style={{ padding: '8px', width: '300px', borderRadius: '5px', border: '1px solid #ddd' }}
          />
          <button onClick={handleGenerate} disabled={loading} style={{ padding: '8px 20px', backgroundColor: loading ? '#ccc' : '#34a853', color: '#fff', border: 'none', borderRadius: '5px', cursor: 'pointer' }}>
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
            <div ref={treeContainerRef} style={{ background: '#fff', borderRadius: '10px', border: '1px solid #eee', position: 'relative', overflow: 'hidden' }}>
              <button 
  onClick={downloadImage}
  style={{ 
    position: 'absolute', 
    top: '10px', 
    right: '10px', 
    zIndex: 10, 
    padding: '8px 15px', 
    backgroundColor: '#1a73e8', 
    color: '#fff', 
    border: 'none', 
    borderRadius: '5px', 
    cursor: 'pointer',
    fontSize: '12px',
    fontWeight: 'bold',
    boxShadow: '0 2px 4px rgba(0,0,0,0.2)'
  }}
>
  تحميل كصورة 📥
</button>
                <Tree 
                  data={treeData} 
                  orientation="vertical" 
                  translate={{ x: 400, y: 50 }} 
                  renderCustomNodeElement={renderRectSvgNode}
                  pathFunc="step"
                  collapsible={true}
                  zoom={0.8}
                  scaleExtent={{ min: 0.4, max: 2 }}
                />
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