import React from 'react';
import { 
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  BarChart, Bar, 
  PieChart, Pie, Cell,
  AreaChart, Area
} from 'recharts';
import { AlertTriangle, Globe, CheckCircle, TrendingUp } from 'lucide-react';

const Charts = () => {
  // Mock Data: Alert Volume over the last 7 days
  const volumeData = [
    { date: 'May 14', alerts: 12, highRisk: 2 },
    { date: 'May 15', alerts: 18, highRisk: 5 },
    { date: 'May 16', alerts: 15, highRisk: 3 },
    { date: 'May 17', alerts: 25, highRisk: 8 },
    { date: 'May 18', alerts: 20, highRisk: 4 },
    { date: 'May 19', alerts: 30, highRisk: 12 },
    { date: 'May 20', alerts: 22, highRisk: 6 },
  ];

  // Mock Data: Risk by Country (Top 5)
  const countryData = [
    { country: 'India', score: 85 },
    { country: 'UAE', score: 72 },
    { country: 'Nigeria', score: 91 },
    { country: 'Singapore', score: 45 },
    { country: 'UK', score: 38 },
  ];

  // Mock Data: False Positive Rate
  const fpData = [
    { name: 'True Positive', value: 65, color: '#cf1322' },
    { name: 'False Positive', value: 35, color: '#d9d9d9' },
  ];

  const styles = {
    container: { padding: '24px', backgroundColor: '#f5f7fa', minHeight: '100vh', fontFamily: 'Segoe UI, Roboto, sans-serif' },
    header: { marginBottom: '24px' },
    title: { margin: 0, fontSize: '24px', fontWeight: 600, color: '#262626' },
    subtitle: { color: '#8c8c8c', fontSize: '14px', marginTop: '4px' },
    grid: { display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '24px' },
    card: { backgroundColor: '#fff', padding: '20px', borderRadius: '12px', border: '1px solid #e8e8e8', boxShadow: '0 2px 8px rgba(0,0,0,0.04)' },
    cardHeader: { display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '20px', borderBottom: '1px solid #f0f0f0', paddingBottom: '12px' },
    cardTitle: { margin: 0, fontSize: '16px', fontWeight: 600, color: '#595959' },
    fullWidth: { gridColumn: 'span 2' },
    statRow: { display: 'flex', gap: '24px', marginBottom: '24px' },
    miniStat: { flex: 1, backgroundColor: '#fff', padding: '16px', borderRadius: '12px', border: '1px solid #e8e8e8', display: 'flex', flexDirection: 'column' },
    statLabel: { fontSize: '12px', color: '#8c8c8c', marginBottom: '4px' },
    statValue: { fontSize: '24px', fontWeight: 700, color: '#262626' },
    statTrend: { fontSize: '12px', marginTop: '4px', display: 'flex', alignItems: 'center', gap: '4px' }
  };

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <h1 style={styles.title}>System Analytics & Risk Insights</h1>
        <p style={styles.subtitle}>ScoreSentinel Executive Dashboard | Real-time monitoring of AML & Mule Cluster trends</p>
      </div>

      <div style={styles.statRow}>
        <div style={styles.miniStat}>
          <span style={styles.statLabel}>Total Alerts (7d)</span>
          <span style={styles.statValue}>142</span>
          <span style={{...styles.statTrend, color: '#52c41a'}}><TrendingUp size={14} /> +12% vs last week</span>
        </div>
        <div style={styles.miniStat}>
          <span style={styles.statLabel}>Avg Risk Score</span>
          <span style={styles.statValue}>64.2</span>
          <span style={{...styles.statTrend, color: '#cf1322'}}><TrendingUp size={14} /> +4.1 (Increased volatility)</span>
        </div>
        <div style={styles.miniStat}>
          <span style={styles.statLabel}>Mule Networks Detected</span>
          <span style={styles.statValue}>8</span>
          <span style={{...styles.statTrend, color: '#1890ff'}}>Active monitoring</span>
        </div>
        <div style={styles.miniStat}>
          <span style={styles.statLabel}>False Positive Rate</span>
          <span style={styles.statValue}>35%</span>
          <span style={{...styles.statTrend, color: '#52c41a'}}>Target: &lt;40%</span>
        </div>
      </div>

      <div style={styles.grid}>
        {/* Alert Volume Chart */}
        <div style={{...styles.card, ...styles.fullWidth}}>
          <div style={styles.cardHeader}>
            <AlertTriangle size={18} color="#1890ff" />
            <h3 style={styles.cardTitle}>Alert Volume & Severity Trends</h3>
          </div>
          <div style={{ height: '300px', width: '100%' }}>
            <ResponsiveContainer>
              <AreaChart data={volumeData}>
                <defs>
                  <linearGradient id="colorAlerts" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#1890ff" stopOpacity={0.1}/>
                    <stop offset="95%" stopColor="#1890ff" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f0f0f0" />
                <XAxis dataKey="date" axisLine={false} tickLine={false} tick={{fontSize: 12, fill: '#8c8c8c'}} dy={10} />
                <YAxis axisLine={false} tickLine={false} tick={{fontSize: 12, fill: '#8c8c8c'}} />
                <Tooltip 
                  contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 12px rgba(0,0,0,0.1)' }}
                />
                <Legend iconType="circle" />
                <Area type="monotone" dataKey="alerts" name="Total Alerts" stroke="#1890ff" strokeWidth={2} fillOpacity={1} fill="url(#colorAlerts)" />
                <Line type="monotone" dataKey="highRisk" name="Critical/High Risk" stroke="#cf1322" strokeWidth={2} dot={{ r: 4, fill: '#cf1322' }} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Risk by Country */}
        <div style={styles.card}>
          <div style={styles.cardHeader}>
            <Globe size={18} color="#722ed1" />
            <h3 style={styles.cardTitle}>Risk Exposure by Jurisdiction</h3>
          </div>
          <div style={{ height: '300px', width: '100%' }}>
            <ResponsiveContainer>
              <BarChart data={countryData} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#f0f0f0" />
                <XAxis type="number" hide />
                <YAxis dataKey="country" type="category" axisLine={false} tickLine={false} tick={{fontSize: 12, fill: '#595959'}} width={80} />
                <Tooltip cursor={{fill: '#f5f7fa'}} contentStyle={{ borderRadius: '8px' }} />
                <Bar dataKey="score" name="Avg Risk Score" radius={[0, 4, 4, 0]}>
                  {countryData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.score > 80 ? '#cf1322' : '#1890ff'} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* False Positive Rate */}
        <div style={styles.card}>
          <div style={styles.cardHeader}>
            <CheckCircle size={18} color="#52c41a" />
            <h3 style={styles.cardTitle}>False Positive Analysis</h3>
          </div>
          <div style={{ height: '300px', width: '100%' }}>
            <ResponsiveContainer>
              <PieChart>
                <Pie
                  data={fpData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={80}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {fpData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend verticalAlign="bottom" align="center" />
              </PieChart>
            </ResponsiveContainer>
            <div style={{textAlign: 'center', marginTop: '-160px', position: 'relative', zIndex: -1}}>
              <div style={{fontSize: '24px', fontWeight: 700}}>35%</div>
              <div style={{fontSize: '12px', color: '#8c8c8c'}}>FP Rate</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Charts;
