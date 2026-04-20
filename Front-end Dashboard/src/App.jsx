import React, { useState, useRef } from 'react';
import Tree from 'react-d3-tree';
import { Gantt, ViewMode } from 'gantt-task-react';
import "gantt-task-react/dist/index.css";
import { toPng } from 'html-to-image';

// --- CSS متقدم مدمج للحركات والتأثيرات الخارقة ---
const masterUI = `
  * { box-sizing: border-box; font-family: 'Cairo', sans-serif; }
  .dashboard-bg { background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%); min-height: 100vh; }
  
  .premium-card { 
    background: #ffffff; 
    border-radius: 24px; 
    box-shadow: 0 10px 40px -10px rgba(0,0,0,0.08); 
    border: 1px solid rgba(255,255,255,0.8);
    transition: transform 0.3s ease, box-shadow 0.3s ease;
  }
  
  .textarea-mega { 
    width: 100%; min-height: 200px; padding: 25px; border-radius: 20px; 
    border: 2px solid #cbd5e1; font-size: 18px; color: #0f172a; 
    background: #f8fafc; transition: all 0.3s; resize: vertical; line-height: 1.8;
  }
  .textarea-mega:focus { border-color: #4f46e5; background: #fff; box-shadow: 0 0 0 5px rgba(79, 70, 229, 0.15); outline: none; }
  
  .btn-magic { 
    background: linear-gradient(135deg, #4f46e5 0%, #3b82f6 100%); 
    color: white; border: none; padding: 18px 45px; border-radius: 16px; 
    font-size: 20px; font-weight: 800; cursor: pointer; transition: all 0.3s;
    box-shadow: 0 10px 25px rgba(79, 70, 229, 0.3); display: inline-flex; align-items: center; gap: 12px;
  }
  .btn-magic:hover { transform: translateY(-3px) scale(1.02); box-shadow: 0 15px 35px rgba(79, 70, 229, 0.4); }
  
  .loader-core { width: 70px; height: 70px; border: 6px solid #e2e8f0; border-top-color: #4f46e5; border-radius: 50%; animation: spin 1s cubic-bezier(0.68, -0.55, 0.265, 1.55) infinite; }
  @keyframes spin { to { transform: rotate(360deg); } }
  
  .fade-in-up { animation: fadeInUp 0.8s ease forwards; opacity: 0; transform: translateY(20px); }
  @keyframes fadeInUp { to { opacity: 1; transform: translateY(0); } }

  .risk-badge { padding: 6px 12px; border-radius: 12px; font-size: 12px; font-weight: 800; display: inline-flex; align-items: center; gap: 5px; }

  /* شريط تمرير (Scrollbar) مخصص وأنيق لسجل المخاطر */
  .custom-scroll { overflow-y: auto; padding-right: 5px; }
  .custom-scroll::-webkit-scrollbar { width: 6px; }
  .custom-scroll::-webkit-scrollbar-track { background: #f1f5f9; border-radius: 10px; }
  .custom-scroll::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 10px; }
  .custom-scroll::-webkit-scrollbar-thumb:hover { background: #94a3b8; }
`;

function App() {
  const [projectName, setProjectName] = useState("");
  const [loading, setLoading] = useState(false);
  const [isGenerated, setIsGenerated] = useState(false);
  const treeContainerRef = useRef(null);

  const [treeData, setTreeData] = useState({});
  const [tasks, setTasks] = useState([]);
  const [riskLogData, setRiskLogData] = useState([]);
  
  const [stats, setStats] = useState({ tasks: 0, days: 0, criticalRisks: 0 });

  const renderRectSvgNode = ({ nodeDatum, toggleNode }) => {
    const isRoot = !nodeDatum.__rd3t || nodeDatum.__rd3t.depth === 0;
    return (
      <g>
        <defs>
          <filter id="nodeShadow" x="-20%" y="-20%" width="140%" height="140%">
            <feDropShadow dx="0" dy="6" stdDeviation="6" floodOpacity="0.15" />
          </filter>
        </defs>
        <rect 
          width="280" height="90" x="-140" y="-45" rx="16"
          fill={isRoot ? "#0f172a" : (nodeDatum.children ? "#4f46e5" : "#0ea5e9")} 
          filter="url(#nodeShadow)" onClick={toggleNode} style={{ cursor: 'pointer' }}
        />
        <foreignObject x="-130" y="-35" width="260" height="70">
          <div style={{ color: '#fff', fontSize: isRoot ? '16px' : '14px', fontWeight: '800', textAlign: 'center', display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%', wordWrap: 'break-word', lineHeight: '1.5' }}>
            {nodeDatum.name}
          </div>
        </foreignObject>
      </g>
    );
  };

  const handleGenerate = async () => {
    if (projectName.trim().length < 10) { alert("⚠️ يرجى كتابة وصف مفصل للمشروع لا يقل عن 10 أحرف."); return; }
    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/generate-plan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: projectName })
      });
      if (!response.ok) throw new Error("السيرفر لا يستجيب");
      
      const result = await response.json();
      
      setTreeData({
        name: result.project_name || "الخطة الرئيسية",
        children: result.wbs.map(p => ({ name: p.phase, children: p.tasks.map(t => ({ name: t })) }))
      });
      setRiskLogData(result.risk_log || []);

      let totalDays = 0;
      let currentDate = new Date();
      const formattedTasks = result.gantt_data.map((t, i) => {
        const start = new Date(currentDate);
        const end = new Date(currentDate);
        end.setDate(end.getDate() + Math.max(1, t.duration_days));
        currentDate = new Date(end);
        totalDays += t.duration_days;
        return { 
          start, end, name: t.task_name, id: `T_${i}`, type: 'task', progress: 100, 
          styles: { progressColor: i % 2 === 0 ? '#4f46e5' : '#0ea5e9', progressSelectedColor: '#312e81' } 
        };
      });
      
      setTasks(formattedTasks);
      setStats({ 
        tasks: formattedTasks.length, 
        days: totalDays, 
        criticalRisks: (result.risk_log || []).filter(r => r.impact === 'High').length 
      });
      setIsGenerated(true);
    } catch (e) {
      alert("❌ تأكد من تشغيل الباك إند.");
    } finally {
      setLoading(false);
    }
  };

  const downloadImage = () => {
    if (!treeContainerRef.current) return;
    const btn = treeContainerRef.current.querySelector('button');
    if (btn) btn.style.display = 'none';
    toPng(treeContainerRef.current, { backgroundColor: '#f8fafc', pixelRatio: 2 })
      .then(url => { const a = document.createElement('a'); a.download = 'WBS_Premium.png'; a.href = url; a.click(); })
      .finally(() => { if (btn) btn.style.display = 'block'; });
  };

  const getRiskStyle = (level) => {
    if (level === 'High') return { bg: '#fee2e2', text: '#b91c1c', border: '#fca5a5', icon: '🔴' };
    if (level === 'Medium') return { bg: '#fef3c7', text: '#b45309', border: '#fcd34d', icon: '🟠' };
    return { bg: '#d1fae5', text: '#047857', border: '#6ee7b7', icon: '🟢' };
  };

  return (
    <div className="dashboard-bg">
      <style>{masterUI}</style>

      {/* Navbar */}
      <nav style={{ padding: '20px 50px', background: 'rgba(255,255,255,0.9)', backdropFilter: 'blur(10px)', borderBottom: '1px solid #e2e8f0', position: 'sticky', top: 0, zIndex: 100, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '15px' }}>
          <div style={{ background: 'linear-gradient(135deg, #4f46e5, #0ea5e9)', color: 'white', padding: '10px', borderRadius: '12px', fontSize: '24px', boxShadow: '0 4px 15px rgba(79, 70, 229, 0.4)' }}>🚀</div>
          <h1 style={{ margin: 0, color: '#0f172a', fontSize: '26px', fontWeight: '900', letterSpacing: '-0.5px' }}>AI PM Architect</h1>
        </div>
        {isGenerated && <button onClick={() => setIsGenerated(false)} style={{ padding: '10px 25px', background: '#f1f5f9', color: '#0f172a', border: 'none', borderRadius: '12px', fontWeight: '800', cursor: 'pointer', fontSize: '16px', transition: '0.3s' }}>+ مشروع جديد</button>}
      </nav>

      {/* Loading Overlay */}
      {loading && (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(248, 250, 252, 0.95)', zIndex: 200, display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', backdropFilter: 'blur(8px)' }}>
          <div className="loader-core"></div>
          <h2 style={{ marginTop: '30px', color: '#0f172a', fontSize: '28px', fontWeight: '800' }}>جاري المعالجة والتحليل...</h2>
          <p style={{ color: '#64748b', fontSize: '18px' }}>نستخدم أحدث نماذج الذكاء الاصطناعي لرسم خطة مشروعك 🧠</p>
        </div>
      )}

      {/* شاشة الإدخال العملاقة */}
      {!isGenerated && !loading && (
        <div className="fade-in-up" style={{ maxWidth: '1000px', margin: '80px auto', padding: '0 20px', textAlign: 'center' }}>
          <h1 style={{ fontSize: '52px', color: '#0f172a', marginBottom: '20px', fontWeight: '900', lineHeight: '1.2' }}>هندس مشروعك بضغطة زر.</h1>
          <p style={{ color: '#475569', fontSize: '22px', marginBottom: '50px', fontWeight: '500' }}>أدخل تفاصيل ونطاق المشروع بدقة، ودع الباقي على ذكائنا الاصطناعي.</p>
          
          <div className="premium-card" style={{ padding: '40px', textAlign: 'right', background: '#fff' }}>
            <label style={{ display: 'block', marginBottom: '15px', color: '#0f172a', fontSize: '20px', fontWeight: '800' }}>📝 صف نطاق العمل (Project Scope):</label>
            <textarea 
              className="textarea-mega"
              value={projectName}
              onChange={(e) => setProjectName(e.target.value)}
              placeholder="اكتب هنا كل ما يخطر ببالك... الأهداف، المنصات المستهدفة، الميزات المطلوبة..."
            />
            <div style={{ display: 'flex', justifyContent: 'center', marginTop: '35px' }}>
              <button className="btn-magic" onClick={handleGenerate}>توليد المخططات والمخاطر ⚡</button>
            </div>
          </div>
        </div>
      )}

      {/* لوحة التحكم (بعد التوليد) */}
      {isGenerated && !loading && (
        <div className="fade-in-up" style={{ padding: '40px 60px', display: 'flex', flexDirection: 'column', gap: '35px' }}>
          
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '30px' }}>
            {[
              { title: "إجمالي المهام المجدولة", value: stats.tasks, icon: "📋", color: "#4f46e5", bg: "#e0e7ff" },
              { title: "المدة الزمنية (بالأيام)", value: stats.days, icon: "⏳", color: "#0ea5e9", bg: "#e0f2fe" },
              { title: "عدد المخاطر الحرجة", value: stats.criticalRisks, icon: "⚠️", color: "#e11d48", bg: "#ffe4e6" }
            ].map((kpi, idx) => (
              <div key={idx} className="premium-card" style={{ padding: '30px', display: 'flex', alignItems: 'center', gap: '25px' }}>
                <div style={{ background: kpi.bg, color: kpi.color, width: '70px', height: '70px', borderRadius: '20px', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '32px' }}>{kpi.icon}</div>
                <div>
                  <p style={{ margin: '0 0 8px 0', color: '#64748b', fontSize: '16px', fontWeight: '700' }}>{kpi.title}</p>
                  <h2 style={{ margin: 0, color: '#0f172a', fontSize: '38px', fontWeight: '900' }}>{kpi.value}</h2>
                </div>
              </div>
            ))}
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1.6fr 1.4fr', gap: '35px', height: '650px' }}>
            {/* WBS Tree */}
            <div className="premium-card" ref={treeContainerRef} style={{ position: 'relative', overflow: 'hidden' }}>
               <div style={{ padding: '25px 30px', borderBottom: '1px solid #f1f5f9', display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: '#fff', position: 'relative', zIndex: 10 }}>
                 <h3 style={{ margin: 0, color: '#0f172a', fontSize: '22px', fontWeight: '900' }}>🌳 هيكل تجزئة العمل (WBS)</h3>
                 <button onClick={downloadImage} style={{ background: '#f1f5f9', color: '#0f172a', border: 'none', padding: '10px 20px', borderRadius: '10px', fontWeight: '800', cursor: 'pointer' }}>حفظ الصورة 📸</button>
               </div>
               <div style={{ width: '100%', height: 'calc(100% - 85px)', background: '#fafaf9' }}>
                 <Tree 
                    data={treeData} orientation="vertical" translate={{ x: 450, y: 50 }} 
                    renderCustomNodeElement={renderRectSvgNode} pathFunc="step"
                    nodeSize={{ x: 350, y: 220 }} separation={{ siblings: 1.5, nonSiblings: 2 }} zoom={0.65}
                 />
               </div>
            </div>

            {/* سجل المخاطر - مع السكرول */}
            <div className="premium-card" style={{ display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
              <div style={{ padding: '25px 30px', borderBottom: '1px solid #f1f5f9', background: '#fff', zIndex: 10 }}>
                <h3 style={{ margin: 0, color: '#0f172a', fontSize: '22px', fontWeight: '900' }}>🛡️ لوحة تحليل المخاطر</h3>
              </div>
              {/* تمت إضافة السكرول هنا 👇 مع تحديد أقصى ارتفاع مسموح */}
              <div className="custom-scroll" style={{ padding: '25px', background: '#fafaf9', display: 'flex', flexDirection: 'column', gap: '20px', height: 'calc(100% - 85px)' }}>
                {riskLogData.map((r, i) => {
                  const probStyle = getRiskStyle(r.probability);
                  const impStyle = getRiskStyle(r.impact);
                  return (
                    <div key={i} style={{ background: '#fff', borderRadius: '20px', padding: '25px', border: `1px solid #e2e8f0`, boxShadow: '0 4px 15px rgba(0,0,0,0.02)' }}>
                      <h4 style={{ margin: '0 0 20px 0', color: '#0f172a', fontSize: '18px', fontWeight: '800', lineHeight: '1.5' }}>{r.risk}</h4>
                      
                      <div style={{ display: 'flex', gap: '15px', marginBottom: '20px' }}>
                        <div style={{ flex: 1, background: '#f8fafc', padding: '15px', borderRadius: '16px', border: '1px solid #f1f5f9' }}>
                          <p style={{ margin: '0 0 10px 0', fontSize: '13px', color: '#64748b', fontWeight: '700' }}>إمكانية الحدوث (Probability)</p>
                          <span className="risk-badge" style={{ background: probStyle.bg, color: probStyle.text, border: `1px solid ${probStyle.border}` }}>
                            {probStyle.icon} {r.probability}
                          </span>
                        </div>
                        <div style={{ flex: 1, background: '#f8fafc', padding: '15px', borderRadius: '16px', border: '1px solid #f1f5f9' }}>
                          <p style={{ margin: '0 0 10px 0', fontSize: '13px', color: '#64748b', fontWeight: '700' }}>مدى الخطورة (Impact)</p>
                          <span className="risk-badge" style={{ background: impStyle.bg, color: impStyle.text, border: `1px solid ${impStyle.border}` }}>
                            {impStyle.icon} {r.impact}
                          </span>
                        </div>
                      </div>

                      <div style={{ background: '#f0fdf4', padding: '15px 20px', borderRadius: '16px', border: '1px solid #bbf7d0' }}>
                        <strong style={{ color: '#166534', fontSize: '14px', display: 'block', marginBottom: '5px' }}>💡 استراتيجية التخفيف:</strong>
                        <span style={{ color: '#15803d', fontSize: '15px', lineHeight: '1.6' }}>{r.mitigation}</span>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>

          {/* مخطط غانت - بمساحة عملاقة */}
          <div className="premium-card" style={{ padding: '35px', direction: 'ltr', background: '#fff', display: 'flex', flexDirection: 'column' }}>
            <h3 style={{ marginTop: 0, marginBottom: '25px', textAlign: 'right', direction: 'rtl', color: '#0f172a', fontSize: '22px', fontWeight: '900' }}>📅 المخطط الزمني للمشروع (Gantt)</h3>
            {/* إجبار مخطط غانت على أخذ مساحة ضخمة ليظهر بوضوح 👇 */}
            <div style={{ minHeight: '550px', overflowX: 'auto', width: '100%' }}>
              <Gantt 
                tasks={tasks} viewMode={ViewMode.Day} 
                listCellWidth="350px" columnWidth={110} rowHeight={65} fontSize={15} barCornerRadius={10} barFill={80}
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;