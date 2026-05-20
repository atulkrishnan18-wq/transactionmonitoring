import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Shield, User, MapPin, Activity, FileText, CheckCircle, AlertTriangle, ArrowLeft } from 'lucide-react';

const CaseDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('breakdown');
  
  // Form State
  const [form, setForm] = useState({
    client_rp: '',
    worldcheck_id: '',
    internal_summary: '',
    reviewer_rationale: '',
    disposition: 'PENDING',
    stage: 'PENDING_ASSESSMENT',
    p1_id: '', p1_src: '',
    p2_id: '', p2_src: '',
    p3_id: '', p3_src: ''
  });

  useEffect(() => {
    const fetchDetail = async () => {
      try {
        const response = await fetch(`http://localhost:5000/api/alerts/${id}`);
        const result = await response.json();
        setData(result);
        if (result.alert) {
          setForm({
            client_rp: result.alert.client_rp || '',
            worldcheck_id: result.alert.worldcheck_id || '',
            internal_summary: result.alert.internal_summary || '',
            reviewer_rationale: result.alert.reviewer_rationale || '',
            disposition: result.alert.disposition || 'PENDING',
            stage: result.alert.stage || 'PENDING_ASSESSMENT',
            p1_id: result.alert.point_1_identifier || '',
            p1_src: result.alert.point_1_source || '',
            p2_id: result.alert.point_2_identifier || '',
            p2_src: result.alert.point_2_source || '',
            p3_id: result.alert.point_3_identifier || '',
            p3_src: result.alert.point_3_source || ''
          });
        }
      } catch (error) {
        console.error("Failed to fetch case detail:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchDetail();
  }, [id]);

  const handleUpdate = async (newStage) => {
    // Validation for 3-point standard if resolving
    if (newStage === 'RESOLVED' || form.disposition === 'FALSE_POSITIVE') {
      const { p1_id, p1_src, p2_id, p2_src, p3_id, p3_src } = form;
      if (!p1_id || !p1_src || !p2_id || !p2_src || !p3_id || !p3_src) {
        alert("CRITICAL ERROR: Three-point standard not met. All 6 identifier/source fields are required for this disposition.");
        return;
      }
    }

    try {
      const response = await fetch(`http://localhost:5000/api/alerts/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...form,
          stage: newStage || form.stage,
          point_1_identifier: form.p1_id,
          point_1_source: form.p1_src,
          point_2_identifier: form.p2_id,
          point_2_source: form.p2_src,
          point_3_identifier: form.p3_id,
          point_3_source: form.p3_src,
          reviewer_id: 'ANALYST_01' // Mock reviewer ID
        })
      });
      if (response.ok) {
        alert("Case updated successfully.");
        navigate('/');
      } else {
        const error = await response.json();
        alert(`Failed to update: ${error.message}`);
      }
    } catch (error) {
      console.error("Update failed:", error);
    }
  };

  if (loading) return <div style={{padding: '40px'}}>Loading Case...</div>;
  if (!data) return <div style={{padding: '40px'}}>Case Not Found.</div>;

  const { alert, transaction } = data;

  const styles = {
    container: { padding: '24px', backgroundColor: '#f0f2f5', minHeight: '100vh', fontFamily: 'Segoe UI, Roboto, sans-serif' },
    card: { backgroundColor: '#fff', padding: '24px', borderRadius: '12px', border: '1px solid #e8e8e8', boxShadow: '0 2px 8px rgba(0,0,0,0.05)' },
    header: { display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', borderBottom: '1px solid #f0f0f0', paddingBottom: '20px', marginBottom: '20px' },
    backBtn: { background: 'none', border: 'none', color: '#1890ff', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' },
    title: { margin: 0, fontSize: '22px', fontWeight: 600 },
    
    badge: (stage) => ({
      padding: '4px 12px', borderRadius: '16px', fontSize: '12px', fontWeight: 600,
      backgroundColor: stage === 'RESOLVED' ? '#f6ffed' : '#fff7e6',
      color: stage === 'RESOLVED' ? '#52c41a' : '#fa8c16',
      border: `1px solid ${stage === 'RESOLVED' ? '#b7eb8f' : '#ffd591'}`
    }),
    
    tabRow: { display: 'flex', gap: '24px', marginBottom: '24px', borderBottom: '1px solid #f0f0f0' },
    tab: (active) => ({
      padding: '12px 4px', background: 'none', border: 'none', cursor: 'pointer',
      color: active ? '#1890ff' : '#595959',
      borderBottom: active ? '2px solid #1890ff' : 'none',
      fontWeight: active ? 600 : 400
    }),
    
    section: { marginBottom: '32px' },
    sectionTitle: { fontSize: '16px', fontWeight: 600, marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' },
    
    grid: { display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' },
    field: { marginBottom: '16px' },
    label: { fontSize: '13px', color: '#8c8c8c', marginBottom: '6px', display: 'block' },
    input: { width: '100%', padding: '10px', borderRadius: '6px', border: '1px solid #d9d9d9', fontSize: '14px' },
    textarea: { width: '100%', padding: '10px', borderRadius: '6px', border: '1px solid #d9d9d9', fontSize: '14px', height: '100px' },
    
    auditBox: { backgroundColor: '#f9f9f9', padding: '20px', borderRadius: '8px', border: '1px solid #e8e8e8' },
    auditGrid: { display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', marginBottom: '12px' },
    
    actionRow: { display: 'flex', gap: '12px', marginTop: '32px', borderTop: '1px solid #f0f0f0', paddingTop: '24px' },
    btn: (primary) => ({
      padding: '10px 24px', borderRadius: '6px', fontWeight: 600, cursor: 'pointer',
      backgroundColor: primary ? '#1890ff' : '#fff',
      color: primary ? '#fff' : '#595959',
      border: primary ? 'none' : '1px solid #d9d9d9'
    })
  };

  return (
    <div style={styles.container}>
      <button onClick={() => navigate('/')} style={styles.backBtn}><ArrowLeft size={16}/> Back to Queue</button>
      
      <div style={styles.card}>
        <div style={styles.header}>
          <div>
            <h1 style={styles.title}>Case Investigation: {alert.alert_id}</h1>
            <div style={{color: '#8c8c8c', fontSize: '14px', marginTop: '4px'}}>
              <User size={14} style={{verticalAlign: 'middle', marginRight: '4px'}}/>
              {alert.customer_name} (ID: {alert.customer_id})
            </div>
          </div>
          <span style={styles.badge(alert.stage)}>{alert.stage}</span>
        </div>

        <div style={styles.tabRow}>
          <button style={styles.tab(activeTab === 'breakdown')} onClick={() => setActiveTab('breakdown')}>Score Breakdown</button>
          <button style={styles.tab(activeTab === 'audit')} onClick={() => setActiveTab('audit')}>AML Audit (3-Point)</button>
          <button style={styles.tab(activeTab === 'rationale')} onClick={() => setActiveTab('rationale')}>Analyst Rationale</button>
        </div>

        {activeTab === 'breakdown' && (
          <div style={styles.section}>
            <div style={styles.grid}>
              <div>
                <h3 style={styles.sectionTitle}><Activity size={18}/> Risk Dimension Analysis</h3>
                <ProgressBar label="Customer Risk" value={transaction.modules.customer} styles={styles} />
                <ProgressBar label="Structuring Detection" value={transaction.modules.structuring} styles={styles} />
                <ProgressBar label="Geography Risk" value={transaction.modules.geo} styles={styles} />
                <ProgressBar label="Transaction Type" value={transaction.modules.transaction} styles={styles} />
                {transaction.mcs && (
                  <div style={{marginTop: '12px', padding: '12px', backgroundColor: '#f9f0ff', borderRadius: '8px', border: '1px solid #d3adf7'}}>
                    <ProgressBar label="Mule Cluster Score (MCS)" value={transaction.mcs} styles={styles} />
                    <div style={{fontSize: '11px', color: '#722ed1', fontWeight: 600}}>NETWORK RISK DETECTED</div>
                  </div>
                )}
                <div style={{marginTop: '20px', padding: '16px', backgroundColor: '#fff2f0', borderRadius: '8px', border: '1px solid #ffccc7'}}>
                  <div style={{display: 'flex', justifyContent: 'space-between', fontWeight: 700}}>
                    <span>Composite Risk Score (CRS):</span>
                    <span style={{color: '#cf1322'}}>{transaction.crs}</span>
                  </div>
                </div>
              </div>
              <div>
                <h3 style={styles.sectionTitle}><FileText size={18}/> Rules Fired</h3>
                <div style={{display: 'flex', flexDirection: 'column', gap: '8px'}}>
                  {transaction.rules_fired.map((rule, idx) => (
                    <div key={idx} style={{padding: '8px 12px', backgroundColor: '#f5f5f5', borderRadius: '4px', fontSize: '13px', borderLeft: '4px solid #1890ff'}}>
                      <strong>{rule}</strong>: Rule trigger detected by ScoreSentinel engine.
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'audit' && (
          <div style={styles.section}>
            <h3 style={styles.sectionTitle}><Shield size={18}/> Three-Point Identifier Audit</h3>
            <p style={{fontSize: '13px', color: '#8c8c8c', marginBottom: '20px'}}>
              Standard operational requirement per AUDIT_REQUIREMENTS.md. All fields must be verified against source documentation.
            </p>
            
            <div style={styles.grid}>
              <div style={styles.field}>
                <label style={styles.label}>Client RP (Relevant Person)</label>
                <input style={styles.input} value={form.client_rp} onChange={e => setForm({...form, client_rp: e.target.value})} placeholder="Full name of RP" />
              </div>
              <div style={styles.field}>
                <label style={styles.label}>World-Check ID</label>
                <input style={styles.input} value={form.worldcheck_id} onChange={e => setForm({...form, worldcheck_id: e.target.value})} placeholder="W-C Reference Number" />
              </div>
            </div>

            <div style={styles.auditBox}>
              <div style={styles.auditGrid}>
                <div style={styles.field}>
                  <label style={styles.label}>Point 1: Identifier</label>
                  <input style={styles.input} value={form.p1_id} onChange={e => setForm({...form, p1_id: e.target.value})} placeholder="e.g. Passport Number" />
                </div>
                <div style={styles.field}>
                  <label style={styles.label}>Point 1: Source</label>
                  <input style={styles.input} value={form.p1_src} onChange={e => setForm({...form, p1_src: e.target.value})} placeholder="e.g. Gov Database" />
                </div>
              </div>
              <div style={styles.auditGrid}>
                <div style={styles.field}>
                  <label style={styles.label}>Point 2: Identifier</label>
                  <input style={styles.input} value={form.p2_id} onChange={e => setForm({...form, p2_id: e.target.value})} placeholder="e.g. Address Proof" />
                </div>
                <div style={styles.field}>
                  <label style={styles.label}>Point 2: Source</label>
                  <input style={styles.input} value={form.p2_src} onChange={e => setForm({...form, p2_src: e.target.value})} placeholder="e.g. Utility Bill" />
                </div>
              </div>
              <div style={styles.auditGrid}>
                <div style={styles.field}>
                  <label style={styles.label}>Point 3: Identifier</label>
                  <input style={styles.input} value={form.p3_id} onChange={e => setForm({...form, p3_id: e.target.value})} placeholder="e.g. DOB" />
                </div>
                <div style={styles.field}>
                  <label style={styles.label}>Point 3: Source</label>
                  <input style={styles.input} value={form.p3_src} onChange={e => setForm({...form, p3_src: e.target.value})} placeholder="e.g. Entity Registry" />
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'rationale' && (
          <div style={styles.section}>
            <h3 style={styles.sectionTitle}><CheckCircle size={18}/> Analyst Decision</h3>
            <div style={styles.field}>
              <label style={styles.label}>Internal Summary</label>
              <textarea style={styles.textarea} value={form.internal_summary} onChange={e => setForm({...form, internal_summary: e.target.value})} placeholder="Executive summary of investigation findings..." />
            </div>
            <div style={styles.field}>
              <label style={styles.label}>Reviewer Rationale</label>
              <textarea style={styles.textarea} value={form.reviewer_rationale} onChange={e => setForm({...form, reviewer_rationale: e.target.value})} placeholder="Step-by-step reasoning for the disposition..." />
            </div>
            <div style={styles.field}>
              <label style={styles.label}>Disposition</label>
              <select style={styles.input} value={form.disposition} onChange={e => setForm({...form, disposition: e.target.value})}>
                <option value="PENDING">Select Disposition...</option>
                <option value="FALSE_POSITIVE">False Positive</option>
                <option value="MATCH_CONFIRMED">Match Confirmed</option>
                <option value="CLEARED">Cleared / Low Risk</option>
                <option value="ESCALATED">Escalated to MLRO</option>
              </select>
            </div>
          </div>
        )}

        <div style={styles.actionRow}>
          <button style={styles.btn(false)} onClick={() => handleUpdate('PENDING_ACTION')}>Send for Action</button>
          <button style={styles.btn(false)} onClick={() => handleUpdate('SENT_FOR_REVIEW')}>Send for Review</button>
          <button style={styles.btn(true)} onClick={() => handleUpdate('RESOLVED')}>Resolve & Close Case</button>
        </div>
      </div>
    </div>
  );
};

const ProgressBar = ({ label, value, styles }) => (
  <div style={{marginBottom: '16px'}}>
    <div style={{display: 'flex', justifyContent: 'space-between', fontSize: '13px', marginBottom: '6px'}}>
      <span style={{color: '#595959'}}>{label}</span>
      <span style={{fontWeight: 600}}>{value}%</span>
    </div>
    <div style={{width: '100%', height: '8px', backgroundColor: '#f0f0f0', borderRadius: '4px', overflow: 'hidden'}}>
      <div style={{width: `${value}%`, height: '100%', backgroundColor: '#1890ff', borderRadius: '4px'}}></div>
    </div>
  </div>
);

export default CaseDetail;
