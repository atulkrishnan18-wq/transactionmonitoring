import React, { useState } from 'react';
import './App.css';
import AlertQueue from './components/AlertQueue';
import CaseDetail from './components/CaseDetail';
import Charts from './components/Charts';
import { LayoutGrid, BarChart3, Users, Network, ShieldAlert, LogOut } from 'lucide-react';

function App() {
  const [view, setView] = useState('queue'); // 'queue', 'detail', 'charts', 'profile', 'mule'
  const [selectedAlert, setSelectedAlert] = useState(null);

  const handleViewCase = (alertId) => {
    setSelectedAlert({ id: alertId });
    setView('detail');
  };

  const styles = {
    appContainer: { display: 'flex', height: '100vh', backgroundColor: '#f0f2f5' },
    sidebar: { width: '240px', backgroundColor: '#001529', color: '#fff', display: 'flex', flexDirection: 'column' },
    logoArea: { padding: '24px', borderBottom: '1px solid rgba(255,255,255,0.1)', display: 'flex', alignItems: 'center', gap: '12px' },
    logoText: { fontSize: '18px', fontWeight: 700, letterSpacing: '0.5px' },
    nav: { flex: 1, padding: '16px 0' },
    navItem: (active) => ({
      padding: '12px 24px',
      display: 'flex',
      alignItems: 'center',
      gap: '12px',
      cursor: 'pointer',
      backgroundColor: active ? '#1890ff' : 'transparent',
      color: active ? '#fff' : 'rgba(255,255,255,0.65)',
      transition: 'all 0.3s'
    }),
    content: { flex: 1, overflowY: 'auto' },
    footer: { padding: '16px 24px', borderTop: '1px solid rgba(255,255,255,0.1)', color: 'rgba(255,255,255,0.45)', fontSize: '12px' }
  };

  return (
    <div style={styles.appContainer}>
      {/* Navigation Sidebar */}
      <div style={styles.sidebar}>
        <div style={styles.logoArea}>
          <ShieldAlert size={24} color="#1890ff" />
          <span style={styles.logoText}>ScoreSentinel</span>
        </div>
        
        <div style={styles.nav}>
          <div 
            style={styles.navItem(view === 'queue' || view === 'detail')} 
            onClick={() => setView('queue')}
          >
            <LayoutGrid size={18} />
            <span>Alert Queue</span>
          </div>
          <div 
            style={styles.navItem(view === 'charts')} 
            onClick={() => setView('charts')}
          >
            <BarChart3 size={18} />
            <span>Analytics</span>
          </div>
          <div 
            style={styles.navItem(view === 'profile')} 
            onClick={() => setView('profile')}
          >
            <Users size={18} />
            <span>Customer Profile</span>
          </div>
          <div 
            style={styles.navItem(view === 'mule')} 
            onClick={() => setView('mule')}
          >
            <Network size={18} />
            <span>Mule Clusters</span>
          </div>
        </div>

        <div style={{...styles.navItem(false), marginTop: 'auto', marginBottom: '8px'}}>
          <LogOut size={18} />
          <span>Logout</span>
        </div>
        
        <div style={styles.footer}>
          ScoreSentinel v1.0.2<br/>
          System Status: Healthy
        </div>
      </div>

      {/* Main Content Area */}
      <div style={styles.content}>
        {view === 'queue' && <AlertQueue onViewCase={handleViewCase} />}
        {view === 'charts' && <Charts />}
        {view === 'detail' && (
          <CaseDetail 
            alertData={selectedAlert} 
            onBack={() => setView('queue')} 
          />
        )}
        {(view === 'profile' || view === 'mule') && (
          <div style={{padding: '40px', textAlign: 'center', color: '#8c8c8c'}}>
            <h2>Coming Soon</h2>
            <p>This module is scheduled for implementation in the next phase of the roadmap.</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
