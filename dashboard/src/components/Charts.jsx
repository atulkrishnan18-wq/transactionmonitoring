import React from 'react';
import { 
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  BarChart, Bar, 
  PieChart, Pie, Cell,
  AreaChart, Area
} from 'recharts';
import { AlertTriangle, Globe, Filter } from 'lucide-react';

const Charts = () => {
  // Mock Data: Alert Volume over the last 30 days (requested)
  const volumeData = Array.from({ length: 30 }, (_, i) => ({
    date: `May ${i + 1}`,
    alerts: Math.floor(Math.random() * 20) + 10,
    highRisk: Math.floor(Math.random() * 8)
  }));

  // Mock Data: Risk by Country
  const countryData = [
    { country: 'India', score: 85 },
    { country: 'UAE', score: 72 },
    { country: 'Nigeria', score: 91 },
    { country: 'Singapore', score: 45 },
    { country: 'UK', score: 38 },
  ];

  // Mock Data: Alert Type Breakdown (requested)
  const typeData = [
    { name: 'AML Risk', value: 45, color: '#1890ff' },
    { name: 'Mule Cluster', value: 30, color: '#722ed1' },
    { name: 'Sanctions', value: 15, color: '#cf1322' },
    { name: 'PEP Match', value: 10, color: '#fa8c16' },
  ];

  const styles = {
    container: { padding: '24px', backgroundColor: '#f5f7fa', minHeight: '100vh', fontFamily: 'Segoe UI, Roboto, sans-serif' },
    header: { marginBottom: '24px' },
    title: { margin: 0, fontSize: '24px', fontWeight: 600, color: '#262626' },
    grid: { display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '24px' },
    card: { backgroundColor: '#fff', padding: '20px', borderRadius: '12px', border: '1px solid #e8e8e8', boxShadow: '0 2px 8px rgba(0,0,0,0.04)' },
    cardHeader: { display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '20px', borderBottom: '1px solid #f0f0f0', paddingBottom: '12px' },
    cardTitle: { margin: 0, fontSize: '16px', fontWeight: 600, color: '#595959' },
    fullWidth: { gridColumn: 'span 2' },
    miniStat: { backgroundColor: '#fff', padding: '16px', borderRadius: '12px', border: '1px solid #e8e8e8', display: 'flex', flexDirection: 'column' },
    statValue: { fontSize: '24px', fontWeight: 700, color: '#262626' },
    statLabel: { fontSize: '12px', color: '#8c8c8c' }
  };

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <h1 style={styles.title}>System Analytics & Risk Insights</h1>
      </div>

      <div style={{ display: 'flex', gap: '24px', marginBottom: '24px' }}>
        <div style={{...styles.miniStat, flex: 1}}>
          <span style={styles.statLabel}>False Positive Rate</span>
          <span style={{...styles.statValue, color: '#52c41a'}}>35%</span>
        </div>
        <div style={{...styles.miniStat, flex: 1}}>
          <span style={styles.statLabel}>Detection Efficiency</span>
          <span style={{...styles.statValue, color: '#1890ff'}}>82%</span>
        </div>
        <div style={{...styles.miniStat, flex: 1}}>
          <span style={styles.statLabel}>Avg Investigation Time</span>
          <span style={styles.statValue}>4.2h</span>
        </div>
      </div>

      <div style={styles.grid}>
        <div style={{...styles.card, ...styles.fullWidth}}>
          <div style={styles.cardHeader}>
            <AlertTriangle size={18} color="#1890ff" />
            <h3 style={styles.cardTitle}>Alert Volume Trends (Last 30 Days)</h3>
          </div>
          <div style={{ height: '300px' }}>
            <ResponsiveContainer>
              <AreaChart data={volumeData}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f0f0f0" />
                <XAxis dataKey="date" hide />
                <YAxis axisLine={false} tickLine={false} />
                <Tooltip />
                <Area type="monotone" dataKey="alerts" name="Total Alerts" stroke="#1890ff" fill="#e6f7ff" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div style={styles.card}>
          <div style={styles.cardHeader}>
            <Globe size={18} color="#722ed1" />
            <h3 style={styles.cardTitle}>Risk Exposure by Jurisdiction</h3>
          </div>
          <div style={{ height: '300px' }}>
            <ResponsiveContainer>
              <BarChart data={countryData} layout="vertical">
                <XAxis type="number" hide />
                <YAxis dataKey="country" type="category" axisLine={false} tickLine={false} width={80} />
                <Tooltip />
                <Bar dataKey="score" fill="#1890ff" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div style={styles.card}>
          <div style={styles.cardHeader}>
            <Filter size={18} color="#fa8c16" />
            <h3 style={styles.cardTitle}>Alert Type Breakdown</h3>
          </div>
          <div style={{ height: '300px' }}>
            <ResponsiveContainer>
              <PieChart>
                <Pie data={typeData} innerRadius={60} outerRadius={80} paddingAngle={5} dataKey="value">
                  {typeData.map((entry, index) => <Cell key={index} fill={entry.color} />)}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Charts;
