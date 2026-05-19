import React, { useState } from 'react';

const AlertQueue = () => {
  const [activeStage, setActiveStage] = useState('PENDING_ASSESSMENT');

  // Stages based on HRDT Workflow (TECHNICAL_OVERVIEW.md Section 6)
  const stages = [
    { id: 'PENDING_ASSESSMENT', label: 'Pending Assessment', count: 3 },
    { id: 'PENDING_ACTION', label: 'Pending Action', count: 1 },
    { id: 'SENT_FOR_REVIEW', label: 'Sent for Review', count: 0 },
    { id: 'RESOLVED', label: 'Resolved / Completed', count: 12 },
  ];

  const getRiskColor = (risk) => {
    switch(risk) {
      case 'AUTO': return '#cf1322'; // Critical Red
      case 'HIGH': return '#d46b08'; // Warning Orange
      default: return '#1890ff';     // Info Blue
    }
  };

  const styles = {
    container: { padding: '24px', backgroundColor: '#f5f7fa', minHeight: '100vh', fontFamily: 'Segoe UI, Roboto, sans-serif' },
    header: { display: 'flex', justifyContent: 'space-between', marginBottom: '24px' },
    title: { margin: 0, fontSize: '24px', fontWeight: 600 },
    statsRow: { display: 'flex', gap: '12px' },
    statCard: { backgroundColor: '#fff', padding: '8px 20px', borderRadius: '8px', border: '1px solid #e8e8e8', display: 'flex', flexDirection: 'column', alignItems: 'center' },
    tabRow: { display: 'flex', gap: '24px', borderBottom: '1px solid #e8e8e8', marginBottom: '16px' },
    tab: { padding: '12px 4px', border: 'none', background: 'none', cursor: 'pointer', fontSize: '14px', display: 'flex', alignItems: 'center', gap: '8px' },
    badge: { backgroundColor: '#f0f0f0', padding: '2px 8px', borderRadius: '10px', fontSize: '12px' },
    tableWrapper: { backgroundColor: '#fff', borderRadius: '8px', boxShadow: '0 2px 8px rgba(0,0,0,0.05)' },
    table: { width: '100%', borderCollapse: 'collapse' },
    tableHeader: { backgroundColor: '#fafafa', borderBottom: '1px solid #f0f0f0', textAlign: 'left' },
    th: { padding: '16px', fontSize: '13px', color: '#595959', fontWeight: 600 },
    tr: { borderBottom: '1px solid #f0f0f0' },
    td: { padding: '16px', fontSize: '14px' },
    typeTag: { backgroundColor: '#e6f7ff', color: '#1890ff', padding: '2px 8px', borderRadius: '4px', fontSize: '11px', fontWeight: 600 },
    viewBtn: { backgroundColor: '#1890ff', color: '#fff', border: 'none', padding: '6px 16px', borderRadius: '4px', cursor: 'pointer', fontSize: '13px' }
  };

  return (
    <div className="alert-queue-container" style={styles.container}>
      {/* Top Bar Statistics */}
      <div style={styles.header}>
        <h1 style={styles.title}>ScoreSentinel Alert Queue</h1>
        <div style={styles.statsRow}>
          <StatCard label="High Risk Alerts" value="4" color="#cf1322" styles={styles} />
          <StatCard label="Mule Clusters" value="2" color="#722ed1" styles={styles} />
        </div>
      </div>

      {/* HRDT Workflow Tabs */}
      <div style={styles.tabRow}>
        {stages.map(stage => (
          <button
            key={stage.id}
            onClick={() => setActiveStage(stage.id)}
            style={{
              ...styles.tab,
              borderBottom: activeStage === stage.id ? '3px solid #1890ff' : 'none',
              color: activeStage === stage.id ? '#1890ff' : '#595959',
              fontWeight: activeStage === stage.id ? '600' : '400',
            }}
          >
            {stage.label}
            <span style={styles.badge}>{stage.count}</span>
          </button>
        ))}
      </div>

      {/* Alert Table */}
      <div style={styles.tableWrapper}>
        <table style={styles.table}>
          <thead>
            <tr style={styles.tableHeader}>
              <th style={styles.th}>Alert ID</th>
              <th style={styles.th}>Customer</th>
              <th style={styles.th}>CRS (AML)</th>
              <th style={styles.th}>MCS (Mule)</th>
              <th style={styles.th}>Type</th>
              <th style={styles.th}>Action</th>
            </tr>
          </thead>
          <tbody>
            <AlertRow 
              id="ALT-20260514-0001" 
              name="Viktor Vekselberg" 
              type="SANCTIONS" 
              crs="AUTO" 
              mcs="12" 
              color={getRiskColor('AUTO')} 
              styles={styles}
            />
            <AlertRow 
              id="ALT-20260514-0002" 
              name="Global Shell Ltd" 
              type="MULE_CLUSTER" 
              crs="62.70" 
              mcs="85" 
              color={getRiskColor('HIGH')} 
              styles={styles}
            />
          </tbody>
        </table>
      </div>
    </div>
  );
};

// Sub-components for cleaner structure
const AlertRow = ({ id, name, type, crs, mcs, color, styles }) => (
  <tr style={styles.tr}>
    <td style={{...styles.td, borderLeft: `4px solid ${color}`}}>{id}</td>
    <td style={styles.td}>
      <div style={{fontWeight: 500}}>{name}</div>
      <div style={{fontSize: '11px', color: '#8c8c8c'}}>ID: CUST-002</div>
    </td>
    <td style={{...styles.td, fontWeight: crs === 'AUTO' ? 700 : 400}}>{crs}</td>
    <td style={styles.td}>{mcs}</td>
    <td style={styles.td}>
      <span style={styles.typeTag}>{type}</span>
    </td>
    <td style={styles.td}>
      <button style={styles.viewBtn}>View Case</button>
    </td>
  </tr>
);

const StatCard = ({ label, value, color, styles }) => (
  <div style={styles.statCard}>
    <span style={{fontSize: '12px', color: '#8c8c8c'}}>{label}</span>
    <span style={{fontSize: '20px', fontWeight: 700, color}}>{value}</span>
  </div>
);

export default AlertQueue;
