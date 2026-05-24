import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import './App.css';
import AlertQueue from './components/AlertQueue';
import CaseDetail from './components/CaseDetail';
import Charts from './components/Charts';
import CustomerProfile from './components/CustomerProfile';
import MuleClusterView from './components/MuleClusterView';
import { LayoutGrid, BarChart3, Users, Network, ShieldAlert, LogOut, Activity } from 'lucide-react';

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
        <Routes>
          <Route path="/" element={<AlertQueue />} />
          <Route path="/alerts/:id" element={<CaseDetail />} />
          <Route path="/transactions" element={<TransactionHistory />} />
          <Route path="/analytics" element={<Charts />} />
          <Route path="/customers" element={<CustomerProfile />} />
          <Route path="/clusters" element={<MuleClusterView />} />
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

  React.useEffect(() => {
    fetch(`${API_URL}/api/transactions`)
      .then(res => res.json())
      .then(data => {
        setTransactions(data.transactions || []);
        setLoading(false);
      })
      .catch(err => console.error(err));
  }, [API_URL]);

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
