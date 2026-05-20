import React from 'react';
import { 
  User, CreditCard, Activity, Smartphone, MapPin, 
  ExternalLink, ShieldCheck, AlertCircle, Clock
} from 'lucide-react';

const CustomerProfile = () => {
  // Mock Data: Customer Information
  const customer = {
    id: "CUST-002",
    name: "Global Shell Ltd",
    type: "Corporate",
    riskTier: "High",
    crs: 62.70,
    mcs: 85.00,
    kycStatus: "Verified",
    onboardingDate: "Jan 12, 2026",
    address: "Level 4, DIFC, Dubai, UAE",
    email: "ops@globalshell.biz"
  };

  // Mock Data: Transaction History
  const transactions = [
    { id: 'TXN-9842', date: 'May 20, 2026', type: 'DEBIT', amount: '₹14,50,000', method: 'NEFT', status: 'Flagged', counterparty: 'Vendor X' },
    { id: 'TXN-9831', date: 'May 19, 2026', type: 'CREDIT', amount: '₹1,20,000', method: 'UPI', status: 'Success', counterparty: 'User A' },
    { id: 'TXN-9830', date: 'May 19, 2026', type: 'CREDIT', amount: '₹1,20,000', method: 'UPI', status: 'Success', counterparty: 'User B' },
    { id: 'TXN-9829', date: 'May 19, 2026', type: 'CREDIT', amount: '₹1,20,000', method: 'UPI', status: 'Success', counterparty: 'User C' },
    { id: 'TXN-9828', date: 'May 19, 2026', type: 'CREDIT', amount: '₹1,20,000', method: 'UPI', status: 'Success', counterparty: 'User D' },
    { id: 'TXN-9827', date: 'May 19, 2026', type: 'CREDIT', amount: '₹1,20,000', method: 'UPI', status: 'Success', counterparty: 'User E' },
  ];

  // Mock Data: Device Nexus (Shared Fingerprints)
  const deviceNexus = [
    { deviceId: 'DEV-A9283-X', type: 'Mobile (iPhone 15)', ip: '192.168.1.45', sharedWith: ['CUST-045', 'CUST-089', 'CUST-112'], lastSeen: '2 hours ago' },
    { deviceId: 'DEV-B4412-K', type: 'Desktop (Chrome/Win)', ip: '103.44.12.98', sharedWith: ['CUST-002'], lastSeen: '12 hours ago' },
  ];

  const styles = {
    container: { padding: '24px', backgroundColor: '#f5f7fa', minHeight: '100vh', fontFamily: 'Segoe UI, Roboto, sans-serif' },
    header: { display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '24px' },
    profileCard: { backgroundColor: '#fff', padding: '24px', borderRadius: '12px', border: '1px solid #e8e8e8', display: 'flex', gap: '24px', flex: 1 },
    avatar: { width: '80px', height: '80px', backgroundColor: '#e6f7ff', borderRadius: '12px', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#1890ff' },
    infoGrid: { display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px', marginTop: '16px' },
    infoItem: { display: 'flex', flexDirection: 'column', gap: '4px' },
    label: { fontSize: '12px', color: '#8c8c8c' },
    value: { fontSize: '14px', fontWeight: 600, color: '#262626' },
    
    sectionTitle: { fontSize: '18px', fontWeight: 600, margin: '32px 0 16px 0', color: '#262626', display: 'flex', alignItems: 'center', gap: '8px' },
    
    grid: { display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '24px' },
    card: { backgroundColor: '#fff', borderRadius: '12px', border: '1px solid #e8e8e8', overflow: 'hidden' },
    table: { width: '100%', borderCollapse: 'collapse' },
    th: { padding: '12px 16px', backgroundColor: '#fafafa', borderBottom: '1px solid #f0f0f0', textAlign: 'left', fontSize: '12px', color: '#8c8c8c', fontWeight: 600 },
    td: { padding: '12px 16px', borderBottom: '1px solid #f0f0f0', fontSize: '13px' },
    
    nexusCard: { padding: '16px', borderBottom: '1px solid #f0f0f0' },
    badge: (color) => ({ backgroundColor: color, color: '#fff', padding: '2px 8px', borderRadius: '4px', fontSize: '11px', fontWeight: 600 }),
    riskBadge: { backgroundColor: '#fff2f0', color: '#ff4d4f', border: '1px solid #ffccc7', padding: '4px 12px', borderRadius: '16px', fontSize: '12px', fontWeight: 600 }
  };

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <div style={styles.profileCard}>
          <div style={styles.avatar}>
            <User size={40} />
          </div>
          <div style={{ flex: 1 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <h1 style={{ margin: 0, fontSize: '22px' }}>{customer.name}</h1>
              <span style={styles.riskBadge}>HIGH RISK (MCS: {customer.mcs})</span>
            </div>
            <div style={styles.infoGrid}>
              <InfoItem label="Customer ID" value={customer.id} icon={<Activity size={14} />} styles={styles} />
              <InfoItem label="Entity Type" value={customer.type} icon={<ShieldCheck size={14} />} styles={styles} />
              <InfoItem label="KYC Status" value={customer.kycStatus} icon={<ShieldCheck size={14} />} styles={styles} />
              <InfoItem label="Onboarding" value={customer.onboardingDate} icon={<Clock size={14} />} styles={styles} />
              <InfoItem label="Jurisdiction" value={customer.address.split(',').pop()} icon={<MapPin size={14} />} styles={styles} />
              <InfoItem label="Composite Score" value={customer.crs} icon={<Activity size={14} />} styles={styles} />
            </div>
          </div>
        </div>
      </div>

      <div style={styles.grid}>
        {/* Left Column: Transaction History */}
        <div>
          <h3 style={styles.sectionTitle}><Activity size={18} /> Recent Transaction History</h3>
          <div style={styles.card}>
            <table style={styles.table}>
              <thead>
                <tr>
                  <th style={styles.th}>Date</th>
                  <th style={styles.th}>Reference</th>
                  <th style={styles.th}>Counterparty</th>
                  <th style={styles.th}>Amount</th>
                  <th style={styles.th}>Type</th>
                  <th style={styles.th}>Status</th>
                </tr>
              </thead>
              <tbody>
                {transactions.map(txn => (
                  <tr key={txn.id}>
                    <td style={styles.td}>{txn.date}</td>
                    <td style={styles.td}>{txn.id}</td>
                    <td style={styles.td}>{txn.counterparty}</td>
                    <td style={{...styles.td, fontWeight: 600}}>{txn.amount}</td>
                    <td style={styles.td}>
                      <span style={{ color: txn.type === 'DEBIT' ? '#cf1322' : '#52c41a' }}>{txn.type}</span>
                    </td>
                    <td style={styles.td}>
                      <span style={{ color: txn.status === 'Flagged' ? '#faad14' : '#52c41a' }}>{txn.status}</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            <div style={{ padding: '16px', textAlign: 'center' }}>
              <button style={{ background: 'none', border: 'none', color: '#1890ff', cursor: 'pointer', fontSize: '13px' }}>
                View All Transactions <ExternalLink size={12} style={{ marginLeft: '4px' }} />
              </button>
            </div>
          </div>
        </div>

        {/* Right Column: Device Nexus (Anti-Mule Intelligence) */}
        <div>
          <h3 style={styles.sectionTitle}><Smartphone size={18} /> Device Nexus Mapping</h3>
          <div style={styles.card}>
            <div style={{ padding: '16px', backgroundColor: '#fff7e6', borderBottom: '1px solid #ffd591', display: 'flex', gap: '8px', alignItems: 'center' }}>
              <AlertCircle size={16} color="#fa8c16" />
              <span style={{ fontSize: '13px', color: '#d46b08', fontWeight: 600 }}>Multiple Account Overlap Detected</span>
            </div>
            {deviceNexus.map((nexus, idx) => (
              <div key={idx} style={styles.nexusCard}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                  <span style={{ fontSize: '13px', fontWeight: 600, color: '#262626' }}>{nexus.type}</span>
                  <span style={{ fontSize: '11px', color: '#8c8c8c' }}>{nexus.lastSeen}</span>
                </div>
                <div style={{ fontSize: '12px', color: '#595959', marginBottom: '12px' }}>
                  IP: <code style={{ backgroundColor: '#f5f5f5', padding: '2px 4px' }}>{nexus.ip}</code>
                </div>
                {nexus.sharedWith.length > 1 && (
                  <div>
                    <div style={styles.label}>SHARED WITH ACCOUNTS:</div>
                    <div style={{ display: 'flex', gap: '4px', marginTop: '4px', flexWrap: 'wrap' }}>
                      {nexus.sharedWith.map(id => (
                        <span key={id} style={{ ...styles.badge('#722ed1'), opacity: id === customer.id ? 0.5 : 1 }}>
                          {id}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
                {nexus.sharedWith.length === 1 && (
                  <span style={{ fontSize: '12px', color: '#52c41a' }}>Unique Device for this profile</span>
                )}
              </div>
            ))}
            <div style={{ padding: '16px', backgroundColor: '#f9f0ff' }}>
              <p style={{ margin: 0, fontSize: '12px', color: '#722ed1', fontStyle: 'italic' }}>
                <strong>Insight:</strong> This device signature (DEV-A9283-X) is linked to a cluster of 5 accounts receiving low-value UPI credits. Consistent with "Money Mule" concentrator behavior.
              </p>
            </div>
          </div>

          <h3 style={styles.sectionTitle}><MapPin size={18} /> Activity Geo-Map</h3>
          <div style={{ ...styles.card, height: '150px', backgroundColor: '#f0f2f5', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
             <span style={{ color: '#8c8c8c', fontSize: '13px' }}>Map Component Placeholder</span>
          </div>
        </div>
      </div>
    </div>
  );
};

const InfoItem = ({ label, value, icon, styles }) => (
  <div style={styles.infoItem}>
    <span style={styles.label}>{label}</span>
    <span style={styles.value}>{value}</span>
  </div>
);

export default CustomerProfile;
