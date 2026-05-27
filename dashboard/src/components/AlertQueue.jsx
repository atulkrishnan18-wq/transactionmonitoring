import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

const AlertQueue = () => {
  const navigate = useNavigate();
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeStage, setActiveStage] = useState('ALL');
  const [typeFilter, setTypeFilter] = useState('ALL');

  const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';
  const READ_KEY = process.env.REACT_APP_READ_API_KEY || 'SCORESENTINEL_READ_2027';

  useEffect(() => {
    const fetchAlerts = async () => {
      setLoading(true);
      try {
        const url = activeStage === 'ALL' 
          ? `${API_URL}/api/alerts` 
          : `${API_URL}/api/alerts?stage=${activeStage}`;
        const response = await fetch(url, {
          headers: { 'X-READ-API-KEY': READ_KEY }
        });
        const data = await response.json();
        setAlerts(data.alerts || []);
      } catch (error) {
        console.error("Failed to fetch alerts:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchAlerts();
  }, [activeStage, API_URL, READ_KEY]);

  const stages = [
    { id: 'ALL', label: 'All Alerts' },
    { id: 'PENDING_ASSESSMENT', label: 'Pending Assessment' },
    { id: 'PENDING_ACTION', label: 'Pending Action' },
    { id: 'SENT_FOR_REVIEW', label: 'Sent for Review' },
    { id: 'RESOLVED', label: 'Resolved' },
  ];

  const filteredAlerts = typeFilter === 'ALL' 
    ? alerts 
    : alerts.filter(a => a.alert_type === typeFilter);

  const getRiskColor = (risk) => {
    if (risk === 'AUTO' || (typeof risk === 'number' && risk >= 80)) return '#cf1322';
    if (typeof risk === 'number' && risk >= 60) return '#d46b08';
    return '#1890ff';
  };

  const styles = {
    container: { padding: '24px', backgroundColor: '#f5f7fa', minHeight: '100vh', fontFamily: 'Segoe UI, Roboto, sans-serif' },
    header: { display: 'flex', justifyContent: 'space-between', marginBottom: '24px' },
    title: { margin: 0, fontSize: '24px', fontWeight: 600 },
    statsRow: { display: 'flex', gap: '12px' },
    statCard: { backgroundColor: '#fff', padding: '8px 20px', borderRadius: '8px', border: '1px solid #e8e8e8', display: 'flex', flexDirection: 'column', alignItems: 'center' },
    
    controlsRow: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' },
    tabRow: { display: 'flex', gap: '24px', borderBottom: '1px solid #e8e8e8' },
    tab: { padding: '12px 4px', border: 'none', background: 'none', cursor: 'pointer', fontSize: '14px', display: 'flex', alignItems: 'center', gap: '8px' },
    badge: { backgroundColor: '#f0f0f0', padding: '2px 8px', borderRadius: '10px', fontSize: '12px' },
    
    filterGroup: { display: 'flex', gap: '12px' },
    select: { padding: '8px 12px', borderRadius: '6px', border: '1px solid #d9d9d9', backgroundColor: '#fff', fontSize: '13px' },
    
    tableWrapper: { backgroundColor: '#fff', borderRadius: '8px', boxShadow: '0 2px 8px rgba(0,0,0,0.05)' },
    table: { width: '100%', borderCollapse: 'collapse' },
    tableHeader: { backgroundColor: '#fafafa', borderBottom: '1px solid #f0f0f0', textAlign: 'left' },
    th: { padding: '16px', fontSize: '13px', color: '#595959', fontWeight: 600 },
    tr: { borderBottom: '1px solid #f0f0f0' },
    td: { padding: '16px', fontSize: '14px' },
    typeTag: (type) => ({ 
      backgroundColor: type.includes('Mule') ? '#f9f0ff' : '#e6f7ff', 
      color: type.includes('Mule') ? '#722ed1' : '#1890ff', 
      padding: '2px 8px', borderRadius: '4px', fontSize: '11px', fontWeight: 600 
    }),
    stageTag: (stage) => ({
       padding: '2px 8px', borderRadius: '12px', fontSize: '11px', fontWeight: 500,
       backgroundColor: stage === 'RESOLVED' ? '#f6ffed' : '#fff7e6',
       color: stage === 'RESOLVED' ? '#52c41a' : '#fa8c16',
       border: `1px solid ${stage === 'RESOLVED' ? '#b7eb8f' : '#ffd591'}`
    }),
    viewBtn: { backgroundColor: '#1890ff', color: '#fff', border: 'none', padding: '6px 16px', borderRadius: '4px', cursor: 'pointer', fontSize: '13px' }
  };

  return (
    <div className="alert-queue-container" style={styles.container}>
      <div style={styles.header}>
        <h1 style={styles.title}>ScoreSentinel Alert Queue</h1>
        <div style={styles.statsRow}>
          <StatCard label="Total Alerts" value={alerts.length} color="#1890ff" styles={styles} />
          <StatCard label="Critical Risk" value={alerts.filter(a => a.crs === 'AUTO' || a.crs >= 80).length} color="#cf1322" styles={styles} />
        </div>
      </div>

      <div style={styles.controlsRow}>
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
              {stage.id === 'ALL' && <span style={styles.badge}>{alerts.length}</span>}
            </button>
          ))}
        </div>

        <div style={styles.filterGroup}>
          <select 
            style={styles.select} 
            value={typeFilter} 
            onChange={(e) => setTypeFilter(e.target.value)}
          >
            <option value="ALL">All Types</option>
            <option value="AML_RISK">AML Risk</option>
            <option value="Mule Cluster Alert">Mule Cluster</option>
            <option value="SANCTIONS">Sanctions</option>
          </select>
        </div>
      </div>

      <div style={styles.tableWrapper}>
        <table style={styles.table}>
          <thead>
            <tr style={styles.tableHeader}>
              <th style={styles.th}>Alert ID</th>
              <th style={styles.th}>Customer</th>
              <th style={styles.th}>CRS Score</th>
              <th style={styles.th}>Alert Type</th>
              <th style={styles.th}>Current Stage</th>
              <th style={styles.th}>Action</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr><td colSpan="6" style={{...styles.td, textAlign: 'center'}}>Loading alerts...</td></tr>
            ) : filteredAlerts.length === 0 ? (
              <tr><td colSpan="6" style={{...styles.td, textAlign: 'center'}}>No alerts found for this criteria.</td></tr>
            ) : (
              filteredAlerts.map(alert => (
                <tr key={alert.alert_id} style={styles.tr}>
                  <td style={{...styles.td, borderLeft: `4px solid ${getRiskColor(alert.crs)}`}}>
                    {alert.alert_id}
                  </td>
                  <td style={styles.td}>
                    <div style={{fontWeight: 500}}>{alert.customer_name}</div>
                    <div style={{fontSize: '11px', color: '#8c8c8c'}}>ID: {alert.customer_id}</div>
                  </td>
                  <td style={{...styles.td, fontWeight: 700}}>
                    {alert.crs}
                  </td>
                  <td style={styles.td}>
                    <span style={styles.typeTag(alert.alert_type)}>{alert.alert_type}</span>
                  </td>
                  <td style={styles.td}>
                    <span style={styles.stageTag(alert.stage)}>{alert.stage}</span>
                  </td>
                  <td style={styles.td}>
                    <button 
                      style={styles.viewBtn}
                      onClick={() => navigate(`/alerts/${alert.alert_id}`)}
                    >
                      View Case
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

const StatCard = ({ label, value, color, styles }) => (
  <div style={styles.statCard}>
    <span style={{fontSize: '12px', color: '#8c8c8c'}}>{label}</span>
    <span style={{fontSize: '20px', fontWeight: 700, color}}>{value}</span>
  </div>
);

export default AlertQueue;
