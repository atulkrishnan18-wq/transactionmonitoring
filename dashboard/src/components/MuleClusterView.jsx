import React, { useState, useEffect } from 'react';

const MuleClusterView = () => {
  const [clusters, setClusters] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedCluster, setSelectedCluster] = useState(null);

  const API_URL = process.env.REACT_APP_API_URL || 'https://scoresentinel-api.onrender.com';
  const READ_KEY = process.env.REACT_APP_READ_API_KEY || 'SCORESENTINEL_READ_2027';

  useEffect(() => {
    const fetchClusters = async () => {
      try {
        const response = await fetch(`${API_URL}/api/clusters`, {
          headers: { 'X-READ-API-KEY': READ_KEY }
        });
        const data = await response.json();
        setClusters(data.clusters || []);
        if (data.clusters && data.clusters.length > 0) {
          setSelectedCluster(data.clusters[0]);
        }
      } catch (error) {
        console.error("Failed to fetch clusters:", error);
      } finally {
        setLoading(false);
      }
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
    fetchClusters();
  }, [API_URL]);

  const styles = {
    container: { padding: '24px', backgroundColor: '#f5f7fa', minHeight: '100vh', fontFamily: 'Segoe UI, Roboto, sans-serif' },
    header: { display: 'flex', justifyContent: 'space-between', marginBottom: '24px' },
    title: { margin: 0, fontSize: '24px', fontWeight: 600, color: '#262626' },
    mainGrid: { display: 'grid', gridTemplateColumns: '300px 1fr 320px', gap: '20px', height: 'calc(100vh - 120px)' },
    sidebar: { backgroundColor: '#fff', borderRadius: '12px', border: '1px solid #e8e8e8', overflowY: 'auto', padding: '16px' },
    clusterItem: (active) => ({
      padding: '12px', borderRadius: '8px', 
      border: active ? '1px solid #1890ff' : '1px solid #f0f0f0',
      backgroundColor: active ? '#e6f7ff' : '#fff', marginBottom: '12px', cursor: 'pointer'
    }),
    mapArea: { backgroundColor: '#fff', borderRadius: '12px', border: '1px solid #e8e8e8', position: 'relative', overflow: 'hidden', display: 'flex', flexDirection: 'column' },
    analysisPanel: { backgroundColor: '#fff', borderRadius: '12px', border: '1px solid #e8e8e8', overflowY: 'auto', padding: '20px' },
    scoreBadge: (score) => ({ 
      backgroundColor: score > 80 ? '#fff1f0' : '#f9f0ff', color: score > 80 ? '#cf1322' : '#722ed1',
      padding: '2px 8px', borderRadius: '4px', fontSize: '11px', fontWeight: 700 
    }),
    actionBtn: (primary) => ({
      width: '100%', padding: '10px', borderRadius: '6px', 
      backgroundColor: primary ? '#cf1322' : '#fff', color: primary ? '#fff' : '#595959',
      border: primary ? 'none' : '1px solid #d9d9d9', fontWeight: 600, cursor: 'pointer', marginBottom: '10px'
    })
  };

  if (loading) return <div style={styles.container}>Loading Cluster Intelligence...</div>;

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <h1 style={styles.title}>MuleCatcher™ Network Intelligence</h1>
      </div>

      <div style={styles.mainGrid}>
        <div style={styles.sidebar}>
          <h3 style={{ fontSize: '12px', color: '#8c8c8c', textTransform: 'uppercase', marginBottom: '16px' }}>Active Clusters</h3>
          {clusters.map(clu => (
            <div key={clu.cluster_id} style={styles.clusterItem(selectedCluster?.cluster_id === clu.cluster_id)} onClick={() => setSelectedCluster(clu)}>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ fontWeight: 600, fontSize: '14px' }}>{clu.cluster_id}</span>
                <span style={{ fontSize: '12px', color: '#cf1322', fontWeight: 700 }}>MCS {clu.mcs}</span>
              </div>
              <div style={{ fontSize: '12px', color: '#595959', marginTop: '4px' }}>{clu.cluster_type}</div>
              <div style={{ fontSize: '11px', color: '#8c8c8c', marginTop: '8px' }}>{clu.account_ids.length} accounts involved</div>
            </div>
          ))}
        </div>

        <div style={styles.mapArea}>
          {selectedCluster ? (
             <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
                <div style={{ padding: '16px', borderBottom: '1px solid #f0f0f0', fontWeight: 600 }}>Network Graph: {selectedCluster.cluster_id}</div>
                <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                   <svg width="400" height="400" viewBox="0 0 400 400">
                      <circle cx="200" cy="200" r="40" fill="#fff1f0" stroke="#cf1322" strokeWidth="3" />
                      <text x="200" y="205" textAnchor="middle" fontSize="10" fontWeight="700" fill="#cf1322">CONCENTRATOR</text>
                      {selectedCluster.account_ids.map((id, i) => {
                         const angle = (i * 360) / selectedCluster.account_ids.length;
                         const x = 200 + 120 * Math.cos((angle * Math.PI) / 180);
                         const y = 200 + 120 * Math.sin((angle * Math.PI) / 180);
                         return (
                           <g key={id}>
                              <line x1="200" y1="200" x2={x} y2={y} stroke="#1890ff" strokeWidth="1" opacity="0.5" />
                              <circle cx={x} cy={y} r="15" fill="#e6f7ff" stroke="#1890ff" strokeWidth="2" />
                              <text x={x} y={y + 4} textAnchor="middle" fontSize="8" fill="#1890ff">{id.slice(-4)}</text>
                           </g>
                         );
                      })}
                   </svg>
                </div>
             </div>
          ) : <div>No cluster selected</div>}
        </div>

        <div style={styles.analysisPanel}>
          {selectedCluster && (
            <>
              <h3 style={{ fontSize: '16px', fontWeight: 600, marginBottom: '20px' }}>Cluster Risk Profile</h3>
              <div style={{ marginBottom: '20px' }}>
                <div style={{ fontSize: '12px', color: '#8c8c8c' }}>Risk Band</div>
                <div style={{ fontSize: '14px', fontWeight: 700, color: '#cf1322' }}>{selectedCluster.risk_band}</div>
              </div>
              <div style={{ marginBottom: '20px' }}>
                <div style={{ fontSize: '12px', color: '#8c8c8c' }}>STR Filed Status</div>
                <div style={{ fontSize: '14px', fontWeight: 600, color: selectedCluster.str_filed ? '#52c41a' : '#fa8c16' }}>
                  {selectedCluster.str_filed ? '✓ STR FILED' : '⚠ ACTION REQUIRED'}
                </div>
              </div>
              <div style={{ marginBottom: '20px' }}>
                <div style={{ fontSize: '12px', color: '#8c8c8c', marginBottom: '8px' }}>Accounts in Cluster</div>
                {selectedCluster.account_ids.map(id => (
                  <div key={id} style={{ fontSize: '13px', padding: '4px 0', borderBottom: '1px solid #f5f5f5' }}>{id}</div>
                ))}
              </div>
              <button style={styles.actionBtn(true)}>Freeze All {selectedCluster.account_ids.length} Accounts</button>
              <button style={styles.actionBtn(false)}>File Bulk STR</button>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default MuleClusterView;
