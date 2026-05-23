import React, { useState, useEffect } from 'react';
import { 
  User, Activity, Smartphone, MapPin, 
  ExternalLink, ShieldCheck, AlertCircle, Clock, Search
} from 'lucide-react';

const CustomerProfile = () => {
  const [customerId, setCustomerId] = useState('CUST-002');
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

  useEffect(() => {
    const fetchCustomer = async () => {
      setLoading(true);
      try {
        const response = await fetch(`${API_URL}/api/customers/${customerId}`);
        const result = await response.json();
        setData(result);
      } catch (error) {
        console.error("Failed to fetch customer:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchCustomer();
  }, [customerId]);

  const styles = {
    container: { padding: '24px', backgroundColor: '#f5f7fa', minHeight: '100vh', fontFamily: 'Segoe UI, Roboto, sans-serif' },
    searchRow: { marginBottom: '24px', display: 'flex', gap: '12px' },
    input: { padding: '8px 12px', borderRadius: '6px', border: '1px solid #d9d9d9', width: '200px' },
    btn: { padding: '8px 16px', backgroundColor: '#1890ff', color: '#fff', border: 'none', borderRadius: '6px', cursor: 'pointer' },
    
    header: { display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '24px' },
    profileCard: { backgroundColor: '#fff', padding: '24px', borderRadius: '12px', border: '1px solid #e8e8e8', display: 'flex', gap: '24px', flex: 1 },
    avatar: { width: '80px', height: '80px', backgroundColor: '#e6f7ff', borderRadius: '12px', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#1890ff' },
    infoGrid: { display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '16px', marginTop: '16px' },
    infoItem: { display: 'flex', flexDirection: 'column', gap: '4px' },
    label: { fontSize: '12px', color: '#8c8c8c' },
    value: { fontSize: '14px', fontWeight: 600, color: '#262626' },
    
    sectionTitle: { fontSize: '18px', fontWeight: 600, margin: '32px 0 16px 0', color: '#262626', display: 'flex', alignItems: 'center', gap: '8px' },
    card: { backgroundColor: '#fff', borderRadius: '12px', border: '1px solid #e8e8e8', overflow: 'hidden' },
    table: { width: '100%', borderCollapse: 'collapse' },
    th: { padding: '12px 16px', backgroundColor: '#fafafa', borderBottom: '1px solid #f0f0f0', textAlign: 'left', fontSize: '12px', color: '#8c8c8c', fontWeight: 600 },
    td: { padding: '12px 16px', borderBottom: '1px solid #f0f0f0', fontSize: '13px' },
    
    riskBadge: (band) => ({
       backgroundColor: band.includes('HIGH') ? '#fff2f0' : '#f6ffed',
       color: band.includes('HIGH') ? '#ff4d4f' : '#52c41a',
       border: `1px solid ${band.includes('HIGH') ? '#ffccc7' : '#b7eb8f'}`,
       padding: '4px 12px', borderRadius: '16px', fontSize: '12px', fontWeight: 600
    })
  };

  if (loading) return <div style={styles.container}>Loading Profile...</div>;
  if (!data || !data.customer) return <div style={styles.container}>Customer Not Found.</div>;

  const { customer, history } = data;

  return (
    <div style={styles.container}>
      <div style={styles.searchRow}>
        <input 
          style={styles.input} 
          placeholder="Enter Customer ID..." 
          value={customerId} 
          onChange={(e) => setCustomerId(e.target.value)} 
        />
        <div style={{...styles.btn, display: 'flex', alignItems: 'center', gap: '8px'}}><Search size={14}/> Find</div>
      </div>

      <div style={styles.header}>
        <div style={styles.profileCard}>
          <div style={styles.avatar}>
            <User size={40} />
          </div>
          <div style={{ flex: 1 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <h1 style={{ margin: 0, fontSize: '22px' }}>{customer.full_name}</h1>
              <span style={styles.riskBadge(customer.risk_band)}>{customer.risk_band}</span>
            </div>
            <div style={styles.infoGrid}>
              <InfoItem label="Customer ID" value={customer.customer_id} styles={styles} />
              <InfoItem label="CCRS Score" value={customer.ccrs} styles={styles} />
              <InfoItem label="Device Nexus" value={customer.device_nexus_count} styles={styles} />
              <InfoItem label="PEP Tier" value={customer.pep_tier || 'None'} styles={styles} />
              <InfoItem label="Last Reviewed" value={customer.last_reviewed || 'Never'} styles={styles} />
              <InfoItem label="Entity Type" value={customer.customer_type} styles={styles} />
              <InfoItem label="Jurisdiction" value={customer.country_of_domicile} styles={styles} />
            </div>
          </div>
        </div>
      </div>

      <h3 style={styles.sectionTitle}><Activity size={18} /> Transaction History</h3>
      <div style={styles.card}>
        <table style={styles.table}>
          <thead>
            <tr>
              <th style={styles.th}>Date</th>
              <th style={styles.th}>TXN ID</th>
              <th style={styles.th}>Amount</th>
              <th style={styles.th}>Type</th>
              <th style={styles.th}>Status</th>
            </tr>
          </thead>
          <tbody>
            {history.map(txn => (
              <tr key={txn.transaction_id}>
                <td style={styles.td}>{txn.date.split('T')[0]}</td>
                <td style={styles.td}>{txn.transaction_id}</td>
                <td style={{...styles.td, fontWeight: 600}}>{txn.currency} {txn.amount.toLocaleString()}</td>
                <td style={styles.td}>{txn.type}</td>
                <td style={styles.td}>
                  <span style={{ color: txn.status === 'FLAGGED' ? '#faad14' : '#52c41a' }}>{txn.status}</span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

const InfoItem = ({ label, value, styles }) => (
  <div style={styles.infoItem}>
    <span style={styles.label}>{label}</span>
    <span style={styles.value}>{value}</span>
  </div>
);

export default CustomerProfile;
