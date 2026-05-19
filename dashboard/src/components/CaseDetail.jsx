import React, { useState } from 'react';

const CaseDetail = ({ alertData, onBack }) => {
  const [activeTab, setActiveTab] = useState('breakdown');

  // Mock data representing a high-risk Mule alert (used if no alertData passed)
  const data = alertData || {
    id: "ALT-20260514-0002",
    customer: "Global Shell Ltd",
    customer_id: "CUST-002",
    crs: 62.70,
    mcs: 85.00,
    rules: ["MUL-001", "MUL-002", "GEO-1C"],
    modules: {
      customer: 71,
      structuring: 40,
      geo: 100,
      transaction: 82,
      mule: 85
    }
  };

  const styles = {
    container: { padding: '24px', backgroundColor: '#fff', borderRadius: '8px', border: '1px solid #e8e8e8', margin: '24px', fontFamily: 'Segoe UI, Roboto, sans-serif' },
    header: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid #f0f0f0', paddingBottom: '16px', marginBottom: '16px' },
    titleArea: { display: 'flex', flexDirection: 'column', gap: '4px' },
    id: { margin: 0, fontSize: '20px', fontWeight: 600 },
    customerName: { color: '#595959', fontSize: '14px' },
    badge: { backgroundColor: '#fff7e6', color: '#fa8c16', padding: '4px 12px', borderRadius: '4px', fontSize: '12px', border: '1px solid #ffd591', fontWeight: 600 },
    backBtn: { background: 'none', border: 'none', color: '#1890ff', cursor: 'pointer', fontSize: '14px', padding: 0, marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '4px' },
    
    tabRow: { display: 'flex', gap: '24px', marginBottom: '24px', borderBottom: '1px solid #f0f0f0' },
    tab: { padding: '12px 0', background: 'none', border: 'none', cursor: 'pointer', color: '#595959', fontSize: '14px', position: 'relative' },
    activeTab: { padding: '12px 0', background: 'none', border: 'none', cursor: 'pointer', color: '#1890ff', fontSize: '14px', borderBottom: '2px solid #1890ff', fontWeight: 600 },
    
    content: { minHeight: '300px' },
    sectionTitle: { fontSize: '16px', fontWeight: 600, marginBottom: '16px', color: '#262626' },
    
    ruleBox: { backgroundColor: '#f9f0ff', padding: '16px', borderRadius: '8px', borderLeft: '4px solid #722ed1', marginBottom: '16px' },
    ruleItem: { marginBottom: '12px' },
    ruleCode: { fontWeight: 700, color: '#722ed1', marginRight: '8px' },
    ruleDesc: { color: '#262626', fontSize: '14px' },
    
    auditForm: { display: 'flex', flexDirection: 'column', gap: '16px', maxWidth: '600px' },
    label: { fontSize: '13px', color: '#595959', marginBottom: '4px', display: 'block' },
    input: { width: '100%', padding: '10px', borderRadius: '4px', border: '1px solid #d9d9d9', fontSize: '14px' },
    textarea: { width: '100%', padding: '10px', height: '100px', borderRadius: '4px', border: '1px solid #d9d9d9', fontSize: '14px', resize: 'vertical' },
    actionBtn: { backgroundColor: '#1890ff', color: '#fff', border: 'none', padding: '10px 24px', borderRadius: '4px', cursor: 'pointer', fontSize: '14px', fontWeight: 600, alignSelf: 'flex-start' }
  };

  return (
    <div style={styles.container}>
      <button onClick={onBack} style={styles.backBtn}>← Back to Queue</button>
      
      <div style={styles.header}>
        <div style={styles.titleArea}>
          <h2 style={styles.id}>Case Investigation: {data.id}</h2>
          <span style={styles.customerName}>{data.customer} (ID: {data.customer_id})</span>
        </div>
        <span style={styles.badge}>PENDING_ASSESSMENT</span>
      </div>

      <div style={styles.tabRow}>
        <button onClick={() => setActiveTab('breakdown')} style={activeTab === 'breakdown' ? styles.activeTab : styles.tab}>Score Breakdown</button>
        <button onClick={() => setActiveTab('mule')} style={activeTab === 'mule' ? styles.activeTab : styles.tab}>Mule Signals</button>
        <button onClick={() => setActiveTab('audit')} style={activeTab === 'audit' ? styles.activeTab : styles.tab}>Three-Point Audit</button>
      </div>

      <div style={styles.content}>
        {activeTab === 'breakdown' && (
          <div style={{maxWidth: '600px'}}>
            <h3 style={styles.sectionTitle}>Risk Dimension Analysis</h3>
            <ProgressBar label="Customer Risk (30%)" value={data.modules.customer} styles={styles} />
            <ProgressBar label="Structuring Detection (25%)" value={data.modules.structuring} styles={styles} />
            <ProgressBar label="Geography Risk (25%)" value={data.modules.geo} styles={styles} />
            <ProgressBar label="Transaction Type (20%)" value={data.modules.transaction} styles={styles} />
            <ProgressBar label="Mule Cluster Score (MCS)" value={data.modules.mule} color="#722ed1" styles={styles} />
            
            <div style={{marginTop: '24px', padding: '16px', backgroundColor: '#fafafa', borderRadius: '8px', border: '1px solid #f0f0f0'}}>
              <div style={{display: 'flex', justifyContent: 'space-between', marginBottom: '8px'}}>
                <span style={{fontWeight: 600}}>Composite Risk Score (CRS):</span>
                <span style={{fontWeight: 700, color: '#d4380d'}}>{data.crs}</span>
              </div>
              <div style={{display: 'flex', justifyContent: 'space-between'}}>
                <span style={{fontWeight: 600}}>Mule Cluster Score (MCS):</span>
                <span style={{fontWeight: 700, color: '#722ed1'}}>{data.mcs}</span>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'mule' && (
          <div>
            <h3 style={styles.sectionTitle}>Mule Intelligence (MuleCatcher™)</h3>
            <div style={styles.ruleBox}>
              <div style={styles.ruleItem}>
                <span style={styles.ruleCode}>MUL-001:</span>
                <span style={styles.ruleDesc}><strong>Rapid Depletion</strong> - Account balance reduced by &gt;90% via external transfers within 24 hours of high-value credit.</span>
              </div>
              <div style={styles.ruleItem}>
                <span style={styles.ruleCode}>MUL-002:</span>
                <span style={styles.ruleDesc}><strong>Fan-In Nexus</strong> - Account receiving multiple credits from 5+ unrelated individuals followed by single large debit.</span>
              </div>
              <div style={styles.ruleItem}>
                <span style={styles.ruleCode}>GEO-1C:</span>
                <span style={styles.ruleDesc}><strong>Grey-List Corridor</strong> - Transaction involves a jurisdiction on the Feb 2026 FATF increased monitoring list.</span>
              </div>
            </div>
            <div style={{fontSize: '13px', color: '#595959', padding: '12px', backgroundColor: '#fffbe6', border: '1px solid #ffe58f', borderRadius: '4px'}}>
              <strong>Analyst Guidance:</strong> These signals are consistent with "Modern Mule" typologies. Check for device fingerprint overlaps with other accounts in the database.
            </div>
          </div>
        )}

        {activeTab === 'audit' && (
          <div style={styles.auditForm}>
             <h3 style={styles.sectionTitle}>Audit Trail - Three Point Standard</h3>
             <p style={{fontSize: '13px', color: '#8c8c8c', marginBottom: '16px'}}>Required for False Positive clearance or Match Confirmation per AUDIT_REQUIREMENTS.md Section 3.</p>
             
             <div>
               <label style={styles.label}>Point 1: Identifier & Source</label>
               <input style={styles.input} placeholder="e.g. Passport #A1234567 (Gov Database)" />
             </div>
             
             <div>
               <label style={styles.label}>Point 2: Identifier & Source</label>
               <input style={styles.input} placeholder="e.g. Utility Bill (British Gas)" />
             </div>
             
             <div>
               <label style={styles.label}>Point 3: Identifier & Source</label>
               <input style={styles.input} placeholder="e.g. Entity Registry (Companies House)" />
             </div>
             
             <div>
               <label style={styles.label}>Analyst Rationale</label>
               <textarea style={styles.textarea} placeholder="Document your reasoning for the disposal decision here. Every rule fired above must be addressed..."></textarea>
             </div>
             
             <button style={styles.actionBtn}>Submit Decision & Close Case</button>
          </div>
        )}
      </div>
    </div>
  );
};

const ProgressBar = ({ label, value, color = "#1890ff", styles }) => (
  <div style={{marginBottom: '16px'}}>
    <div style={{display: 'flex', justifyContent: 'space-between', fontSize: '13px', marginBottom: '6px'}}>
      <span style={{color: '#595959'}}>{label}</span>
      <span style={{fontWeight: 600}}>{value}%</span>
    </div>
    <div style={{width: '100%', height: '8px', backgroundColor: '#f0f0f0', borderRadius: '4px', overflow: 'hidden'}}>
      <div style={{width: `${value}%`, height: '100%', backgroundColor: color, borderRadius: '4px'}}></div>
    </div>
  </div>
);

export default CaseDetail;
