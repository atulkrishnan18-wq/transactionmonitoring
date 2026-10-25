import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import './App.css';
import AlertQueue from './components/AlertQueue';
import CaseDetail from './components/CaseDetail';
import Charts from './components/Charts';
import CustomerProfile from './components/CustomerProfile';
import MuleClusterView from './components/MuleClusterView';
import TuningLab from './components/TuningLab';
import { LayoutGrid, BarChart3, Users, Network, ShieldAlert, LogOut, Activity, Sliders } from 'lucide-react';

function isIbmRecord(item) {
  const id = item?.customer_id || '';
  const name = item?.customer_name || item?.full_name || '';
  return String(id).startsWith('IBM-') || String(name).startsWith('IBM-');
}

function DemoBanner() {
  const API_URL = process.env.REACT_APP_API_URL || 'https://scoresentinel-api.onrender.com';
  const READ_KEY = process.env.REACT_APP_READ_API_KEY;
  const DEMO_KEY = process.env.REACT_APP_DEMO_API_KEY;
  const [ibmActive, setIbmActive] = React.useState(false);
  const [resetting, setResetting] = React.useState(false);
  const [resetMessage, setResetMessage] = React.useState('');

  const refreshFlag = React.useCallback(() => {
    fetch(`${API_URL}/api/alerts`, { headers: { 'X-READ-API-KEY': READ_KEY } })
      .then((res) => res.json())
      .then((data) => {
        const alerts = data.alerts || [];
        setIbmActive(alerts.some(isIbmRecord));
      })
      .catch(() => {});
  }, [API_URL, READ_KEY]);

  React.useEffect(() => {
    refreshFlag();
    const timer = setInterval(refreshFlag, 8000);
    return () => clearInterval(timer);
  }, [refreshFlag]);

  const handleReset = async () => {
    if (!DEMO_KEY) {
      setResetMessage('Reset unavailable — REACT_APP_DEMO_API_KEY is not configured.');
      return;
    }
    setResetting(true);
    setResetMessage('');
    try {
      const res = await fetch(`${API_URL}/api/demo/reset`, {
        method: 'DELETE',
        headers: { 'X-DEMO-API-KEY': DEMO_KEY, 'Content-Type': 'application/json' }
      });
      const data = await res.json();
      if (res.ok) {
        setResetMessage(data.message || 'Demo environment reset — records deleted');
        setIbmActive(false);
        window.setTimeout(() => window.location.reload(), 800);
      } else {
        setResetMessage(data.message || `Reset failed (${res.status})`);
      }
    } catch (err) {
      setResetMessage('Reset failed — could not reach API.');
    } finally {
      setResetting(false);
    }
  };

  if (!ibmActive && !resetMessage) return null;

  return (
    <div style={{
      backgroundColor: '#111827',
      color: '#fff',
      padding: '10px 24px',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      gap: '16px',
      borderBottom: '3px solid #f59e0b'
    }}>
      <div>
        <strong style={{ color: '#fbbf24' }}>Demo Mode — IBM AML Dataset Active</strong>
        {resetMessage && (
          <div style={{ fontSize: '12px', color: '#d1d5db', marginTop: '2px' }}>{resetMessage}</div>
        )}
      </div>
      <button
        onClick={handleReset}
        disabled={resetting}
        style={{
          backgroundColor: '#f59e0b',
          color: '#111827',
          border: 'none',
          borderRadius: '4px',
          padding: '8px 14px',
          fontWeight: 700,
          cursor: resetting ? 'wait' : 'pointer',
          fontSize: '13px'
        }}
      >
        {resetting ? 'Resetting…' : 'Reset Demo'}
      </button>
    </div>
  );
}

function AppContent() {
  const location = useLocation();
  const currentPath = location.pathname;

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
      transition: 'all 0.3s',
      textDecoration: 'none'
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
          <Link to="/" style={styles.navItem(currentPath === '/' || currentPath.startsWith('/alerts'))}>
            <LayoutGrid size={18} />
            <span>Alert Queue</span>
          </Link>
          <Link to="/transactions" style={styles.navItem(currentPath === '/transactions')}>
            <Activity size={18} />
            <span>Transactions</span>
          </Link>
          <Link to="/analytics" style={styles.navItem(currentPath === '/analytics')}>
            <BarChart3 size={18} />
            <span>Analytics</span>
          </Link>
          <Link to="/customers" style={styles.navItem(currentPath === '/customers')}>
            <Users size={18} />
            <span>Customers</span>
          </Link>
          <Link to="/clusters" style={styles.navItem(currentPath === '/clusters')}>
            <Network size={18} />
            <span>Mule Clusters</span>
          </Link>
          <Link to="/tuning" style={styles.navItem(currentPath === '/tuning')}>
            <Sliders size={18} />
            <span>Tuning Lab</span>
          </Link>
        </div>

        <div style={{...styles.navItem(false), marginTop: 'auto', marginBottom: '8px'}}>
          <LogOut size={18} />
          <span>Logout</span>
        </div>
        
        <div style={styles.footer}>
          ScoreSentinel v2.0 (Enterprise)<br/>
          System Status: Healthy
        </div>
      </div>

      {/* Main Content Area */}
      <div style={styles.content}>
        <DemoBanner />
        <Routes>
          <Route path="/" element={<AlertQueue />} />
          <Route path="/alerts/:id" element={<CaseDetail />} />
          <Route path="/transactions" element={<TransactionHistory />} />
          <Route path="/analytics" element={<Charts />} />
          <Route path="/customers" element={<CustomerProfile />} />
          <Route path="/clusters" element={<MuleClusterView />} />
          <Route path="/tuning" element={<TuningLab />} />
        </Routes>
      </div>
    </div>
  );
}

// Transaction History Component
const TransactionHistory = () => {
  const [transactions, setTransactions] = React.useState([]);
  const [loading, setLoading] = React.useState(true);

  const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';
  const READ_KEY = process.env.REACT_APP_READ_API_KEY;

  React.useEffect(() => {
    fetch(`${API_URL}/api/transactions`, {
      headers: { 'X-READ-API-KEY': READ_KEY }
    })
      .then(res => res.json())
      .then(data => {
        setTransactions(data.transactions || []);
        setLoading(false);
      })
      .catch(err => console.error(err));
  }, [API_URL, READ_KEY]);

  const styles = {
    container: { padding: '24px' },
    table: { width: '100%', borderCollapse: 'collapse', backgroundColor: '#fff', borderRadius: '8px', overflow: 'hidden', boxShadow: '0 2px 8px rgba(0,0,0,0.05)' },
    th: { padding: '16px', backgroundColor: '#fafafa', textAlign: 'left', fontSize: '13px', color: '#595959', fontWeight: 600, borderBottom: '1px solid #f0f0f0' },
    td: { padding: '16px', fontSize: '14px', borderBottom: '1px solid #f0f0f0' },
    riskBadge: (risk) => ({
      padding: '2px 8px', borderRadius: '4px', fontSize: '11px', fontWeight: 600,
      backgroundColor: risk === 'HIGH_RISK' ? '#fff2f0' : '#f6ffed',
      color: risk === 'HIGH_RISK' ? '#ff4d4f' : '#52c41a'
    })
  };

  return (
    <div style={styles.container}>
      <h1 style={{ marginBottom: '24px' }}>Transaction Monitoring Journal</h1>
      {loading ? <p>Loading Transactions...</p> : (
        <table style={styles.table}>
          <thead>
            <tr>
              <th style={styles.th}>Transaction ID</th>
              <th style={styles.th}>Customer</th>
              <th style={styles.th}>CRS</th>
              <th style={styles.th}>Risk Band</th>
              <th style={styles.th}>Timestamp</th>
            </tr>
          </thead>
          <tbody>
            {transactions.map(tx => (
              <tr key={tx.transaction_id}>
                <td style={styles.td}>{tx.transaction_id}</td>
                <td style={styles.td}>{tx.customer_id}</td>
                <td style={styles.td}>{tx.crs || 'N/A'}</td>
                <td style={styles.td}><span style={styles.riskBadge(tx.risk_band)}>{tx.risk_band}</span></td>
                <td style={styles.td}>{new Date(tx.timestamp).toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
};

function App() {
  return (
    <Router>
      <AppContent />
    </Router>
  );
}

export default App;
