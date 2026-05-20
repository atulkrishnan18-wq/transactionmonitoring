import React, { useState } from 'react';
import { 
  Network, ShieldAlert, Zap, Layers, TrendingDown, 
  Search, Filter, ExternalLink, AlertTriangle, CheckCircle2, 
  Ban, FileText, Smartphone, Globe
} from 'lucide-react';

const MuleClusterView = () => {
  const [selectedNode, setSelectedNode] = useState(null);

  // Mock Data: Active Clusters
  const clusters = [
    { id: 'CLU-2026-001', type: 'Concentrator (Fan-In)', mcs: 95, accounts: 9, status: 'PENDING_ACTION', detected: '2h ago' },
    { id: 'CLU-2026-002', type: 'UPI Smurfing Ring', mcs: 65, accounts: 15, status: 'UNDER_REVIEW', detected: '5h ago' },
  ];

  // Mock Data for the selected "Classic Concentrator Network" (Scenario MC-1)
  const networkData = {
    id: 'CLU-2026-001',
    concentrator: { id: 'ACC-X', name: 'Global Shell Ltd', mcs: 95, balance: '₹74,000' },
    senders: [
      { id: 'S1', amount: '₹9,500', time: '14:20' },
      { id: 'S2', amount: '₹9,500', time: '14:22' },
      { id: 'S3', amount: '₹9,500', time: '14:25' },
      { id: 'S4', amount: '₹9,500', time: '14:28' },
      { id: 'S5', amount: '₹9,500', time: '14:30' },
      { id: 'S6', amount: '₹9,500', time: '14:31' },
      { id: 'S7', amount: '₹9,500', time: '14:35' },
      { id: 'S8', amount: '₹9,500', time: '14:38' },
    ],
    exitPoint: { id: 'EXT-1', type: 'Crypto Exchange', amount: '₹72,000', time: '15:10' },
    sharedDevice: 'DEV-A9283-X'
  };

  const styles = {
    container: { padding: '24px', backgroundColor: '#f5f7fa', minHeight: '100vh', fontFamily: 'Segoe UI, Roboto, sans-serif' },
    header: { display: 'flex', justifyContent: 'space-between', marginBottom: '24px' },
    title: { margin: 0, fontSize: '24px', fontWeight: 600, color: '#262626' },
    
    mainGrid: { display: 'grid', gridTemplateColumns: '300px 1fr 320px', gap: '20px', height: 'calc(100vh - 120px)' },
    
    // Sidebar: Cluster List
    sidebar: { backgroundColor: '#fff', borderRadius: '12px', border: '1px solid #e8e8e8', overflowY: 'auto', padding: '16px' },
    clusterItem: (active) => ({
      padding: '12px', 
      borderRadius: '8px', 
      border: active ? '1px solid #1890ff' : '1px solid #f0f0f0',
      backgroundColor: active ? '#e6f7ff' : '#fff',
      marginBottom: '12px',
      cursor: 'pointer'
    }),
    
    // Center: Network Map
    mapArea: { backgroundColor: '#fff', borderRadius: '12px', border: '1px solid #e8e8e8', position: 'relative', overflow: 'hidden', display: 'flex', flexDirection: 'column' },
    mapHeader: { padding: '16px', borderBottom: '1px solid #f0f0f0', display: 'flex', justifyContent: 'space-between', alignItems: 'center' },
    svgContainer: { flex: 1, position: 'relative' },
    
    // Right: Analysis Panel
    analysisPanel: { backgroundColor: '#fff', borderRadius: '12px', border: '1px solid #e8e8e8', overflowY: 'auto', padding: '20px' },
    dimensionRow: { marginBottom: '16px' },
    scoreBadge: (score) => ({ 
      backgroundColor: score > 80 ? '#fff1f0' : '#f9f0ff', 
      color: score > 80 ? '#cf1322' : '#722ed1',
      padding: '2px 8px', borderRadius: '4px', fontSize: '11px', fontWeight: 700 
    }),
    
    actionBtn: (primary) => ({
      width: '100%', padding: '10px', borderRadius: '6px', border: 'none', 
      backgroundColor: primary ? '#cf1322' : '#fff', 
      color: primary ? '#fff' : '#595959',
      border: primary ? 'none' : '1px solid #d9d9d9',
      fontWeight: 600, cursor: 'pointer', marginBottom: '10px', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px'
    })
  };

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <h1 style={styles.title}>MuleCatcher™ Network Intelligence</h1>
        <div style={{ display: 'flex', gap: '12px' }}>
           <div style={{ backgroundColor: '#fff', padding: '4px 12px', borderRadius: '6px', border: '1px solid #d9d9d9', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Search size={14} color="#8c8c8c" />
              <input style={{ border: 'none', outline: 'none', fontSize: '13px' }} placeholder="Search Cluster ID..." />
           </div>
           <button style={{ backgroundColor: '#fff', padding: '8px 12px', borderRadius: '6px', border: '1px solid #d9d9d9', cursor: 'pointer' }}>
              <Filter size={16} />
           </button>
        </div>
      </div>

      <div style={styles.mainGrid}>
        {/* Cluster List Sidebar */}
        <div style={styles.sidebar}>
          <h3 style={{ fontSize: '14px', color: '#8c8c8c', marginBottom: '16px', textTransform: 'uppercase', letterSpacing: '1px' }}>Active Clusters</h3>
          {clusters.map(clu => (
            <div key={clu.id} style={styles.clusterItem(clu.id === networkData.id)}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                <span style={{ fontWeight: 600, fontSize: '14px' }}>{clu.id}</span>
                <span style={{ fontSize: '12px', color: '#cf1322', fontWeight: 700 }}>MCS {clu.mcs}</span>
              </div>
              <div style={{ fontSize: '12px', color: '#595959', marginBottom: '8px' }}>{clu.type}</div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ fontSize: '11px', color: '#8c8c8c' }}>{clu.accounts} accounts • {clu.detected}</span>
                <span style={{ fontSize: '10px', backgroundColor: '#fffbe6', color: '#d46b08', padding: '2px 6px', borderRadius: '4px' }}>{clu.status}</span>
              </div>
            </div>
          ))}
        </div>

        {/* Network Map Visualisation */}
        <div style={styles.mapArea}>
          <div style={styles.mapHeader}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Network size={20} color="#1890ff" />
              <span style={{ fontWeight: 600 }}>Cluster Graph: {networkData.id}</span>
            </div>
            <div style={{ display: 'flex', gap: '8px' }}>
               <span style={{ fontSize: '12px', color: '#8c8c8c' }}>Legend:</span>
               <div style={{ display: 'flex', alignItems: 'center', gap: '4px', fontSize: '11px' }}>
                 <div style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: '#cf1322' }}></div> Concentrator
               </div>
               <div style={{ display: 'flex', alignItems: 'center', gap: '4px', fontSize: '11px' }}>
                 <div style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: '#1890ff' }}></div> Sender
               </div>
            </div>
          </div>
          
          <div style={styles.svgContainer}>
            <svg width="100%" height="100%" viewBox="0 0 800 500">
              {/* Common Device Nexus Node (Shared hardware) */}
              <circle cx="400" cy="150" r="30" fill="#f9f0ff" stroke="#722ed1" strokeWidth="2" strokeDasharray="4" />
              <text x="400" y="155" textAnchor="middle" fontSize="10" fill="#722ed1" fontWeight="700">DEVICE</text>
              <text x="400" y="195" textAnchor="middle" fontSize="9" fill="#8c8c8c">{networkData.sharedDevice}</text>

              {/* Concentrator Node (Center) */}
              <circle cx="400" cy="280" r="45" fill="#fff1f0" stroke="#cf1322" strokeWidth="3" />
              <text x="400" y="285" textAnchor="middle" fontSize="12" fill="#cf1322" fontWeight="700">CONCENTRATOR</text>
              <text x="400" y="340" textAnchor="middle" fontSize="10" fill="#262626" fontWeight="600">{networkData.concentrator.name}</text>
              
              {/* Exit Point Node */}
              <circle cx="650" cy="280" r="35" fill="#f6ffed" stroke="#52c41a" strokeWidth="2" />
              <text x="650" y="285" textAnchor="middle" fontSize="10" fill="#52c41a" fontWeight="700">EXIT</text>
              <path d="M 445 280 L 615 280" stroke="#52c41a" strokeWidth="2" markerEnd="url(#arrowhead-exit)" strokeDasharray="5,5" />
              <text x="530" y="270" textAnchor="middle" fontSize="10" fill="#52c41a">{networkData.exitPoint.amount}</text>

              {/* Sender Nodes (Circular layout) */}
              {networkData.senders.map((s, i) => {
                const angle = (i * 360) / networkData.senders.length;
                const radius = 180;
                const x = 400 + radius * Math.cos((angle * Math.PI) / 180);
                const y = 280 + radius * Math.sin((angle * Math.PI) / 180);
                
                return (
                  <g key={s.id}>
                    {/* Connection to Concentrator */}
                    <line x1={x} y1={y} x2="400" y2="280" stroke="#1890ff" strokeWidth="1.5" opacity="0.4" />
                    
                    {/* Senders also connect to Device Nexus if shared */}
                    {i < 4 && <line x1={x} y1={y} x2="400" y2="150" stroke="#722ed1" strokeWidth="1" strokeDasharray="2" opacity="0.3" />}

                    <circle cx={x} cy={y} r="20" fill="#e6f7ff" stroke="#1890ff" strokeWidth="2" />
                    <text x={x} y={y + 4} textAnchor="middle" fontSize="9" fill="#1890ff" fontWeight="600">{s.id}</text>
                    
                    {/* Amount Label on path */}
                    <text 
                      x={400 + (radius/2) * Math.cos((angle * Math.PI) / 180)} 
                      y={280 + (radius/2) * Math.sin((angle * Math.PI) / 180)} 
                      fontSize="8" fill="#595959" textAnchor="middle"
                    >
                      {s.amount}
                    </text>
                  </g>
                );
              })}

              {/* Arrowheads Definitions */}
              <defs>
                <marker id="arrowhead-exit" markerWidth="10" markerHeight="7" refX="0" refY="3.5" orientation="auto">
                  <polygon points="0 0, 10 3.5, 0 7" fill="#52c41a" />
                </marker>
              </defs>
            </svg>
            
            {/* Interactive Tooltip Simulation */}
            <div style={{ position: 'absolute', bottom: '20px', left: '20px', backgroundColor: 'rgba(0,0,0,0.8)', color: '#fff', padding: '12px', borderRadius: '8px', fontSize: '12px', maxWidth: '250px' }}>
              <div style={{ fontWeight: 700, marginBottom: '4px', color: '#1890ff' }}>Forensic Observation:</div>
              "All 8 senders transferred funds within a 18-minute window. Identical amounts (₹9,500) indicate coordinated instruction."
            </div>
          </div>
        </div>

        {/* Analysis & Actions Panel */}
        <div style={styles.analysisPanel}>
          <h3 style={{ fontSize: '16px', fontWeight: 600, marginBottom: '20px' }}>Cluster Risk Profile</h3>
          
          <div style={styles.dimensionRow}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
              <span style={{ fontSize: '13px', color: '#595959' }}>Concentration Score</span>
              <span style={styles.scoreBadge(90)}>30/30 (CRITICAL)</span>
            </div>
            <div style={{ width: '100%', height: '6px', backgroundColor: '#f0f0f0', borderRadius: '3px' }}>
              <div style={{ width: '100%', height: '100%', backgroundColor: '#cf1322', borderRadius: '3px' }}></div>
            </div>
          </div>

          <div style={styles.dimensionRow}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
              <span style={{ fontSize: '13px', color: '#595959' }}>Velocity Correlation</span>
              <span style={styles.scoreBadge(90)}>25/25 (MAX)</span>
            </div>
            <div style={{ width: '100%', height: '6px', backgroundColor: '#f0f0f0', borderRadius: '3px' }}>
              <div style={{ width: '100%', height: '100%', backgroundColor: '#cf1322', borderRadius: '3px' }}></div>
            </div>
          </div>

          <div style={styles.dimensionRow}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
              <span style={{ fontSize: '13px', color: '#595959' }}>Amount Pattern</span>
              <span style={styles.scoreBadge(90)}>20/20 (MAX)</span>
            </div>
            <div style={{ width: '100%', height: '6px', backgroundColor: '#f0f0f0', borderRadius: '3px' }}>
              <div style={{ width: '100%', height: '100%', backgroundColor: '#cf1322', borderRadius: '3px' }}></div>
            </div>
          </div>

          <div style={styles.dimensionRow}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
              <span style={{ fontSize: '13px', color: '#595959' }}>Pass-Through Speed</span>
              <span style={styles.scoreBadge(85)}>15/15</span>
            </div>
            <div style={{ width: '100%', height: '6px', backgroundColor: '#f0f0f0', borderRadius: '3px' }}>
              <div style={{ width: '100%', height: '100%', backgroundColor: '#d4380d', borderRadius: '3px' }}></div>
            </div>
          </div>

          <div style={{ marginTop: '24px', padding: '16px', backgroundColor: '#fffbe6', border: '1px solid #ffe58f', borderRadius: '8px', marginBottom: '24px' }}>
            <div style={{ display: 'flex', gap: '8px', alignItems: 'center', marginBottom: '8px' }}>
              <AlertTriangle size={16} color="#fa8c16" />
              <span style={{ fontWeight: 700, color: '#d46b08', fontSize: '13px' }}>SYSTEM RECOMMENDATION</span>
            </div>
            <p style={{ margin: 0, fontSize: '12px', color: '#8c6d1f', lineHeight: '1.5' }}>
              High-confidence <strong>Organised Network</strong> detected. Common Device Nexus found across 4/8 senders. Immediate account freeze and STR filing mandatory.
            </p>
          </div>

          <div style={{ marginTop: 'auto' }}>
            <button style={styles.actionBtn(true)}><Ban size={16} /> Freeze All 9 Accounts</button>
            <button style={styles.actionBtn(false)}><FileText size={16} /> File Bulk STR (FIU-IND)</button>
            <button style={{...styles.actionBtn(false), color: '#52c41a', borderColor: '#b7eb8f'}}><CheckCircle2 size={16} /> Mark as False Positive</button>
          </div>
          
          <div style={{ marginTop: '16px', borderTop: '1px solid #f0f0f0', paddingTop: '16px' }}>
             <div style={{ fontSize: '11px', color: '#8c8c8c', marginBottom: '8px' }}>MuleCatcher™ Insights:</div>
             <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '12px', color: '#595959' }}>
               <Smartphone size={14} /> Shared Device ID: {networkData.sharedDevice}
             </div>
             <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '12px', color: '#595959', marginTop: '4px' }}>
               <Globe size={14} /> Exit: Binance.com (Off-ramp)
             </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MuleClusterView;
