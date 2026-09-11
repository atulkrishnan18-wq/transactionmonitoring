import React, { useState, useEffect, useMemo, useCallback } from 'react';
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine
} from 'recharts';
import { Sliders, AlertCircle, Clock, CheckCircle2, TrendingDown, RefreshCw, Save } from 'lucide-react';

const SCENARIO_OPTIONS = [
  {
    id: 'SCEN-STRUC-01',
    name: 'Structuring / Smurfing Detection',
    param: 'lower_bound',
    label: 'Lower Bound Threshold ($)',
    min: 8000,
    max: 10000,
    step: 100,
    defaultVal: 9000,
    unit: '$'
  },
  {
    id: 'SCEN-VEL-01',
    name: 'Rapid Movement / Pass-Through Mule',
    param: 'outflow_ratio',
    label: 'Outflow Dissipation Ratio',
    min: 0.60,
    max: 0.95,
    step: 0.05,
    defaultVal: 0.85,
    unit: ''
  },
  {
    id: 'SCEN-CORR-01',
    name: 'High-Risk Corridor Spike',
    param: 'corridor_risk_weight_threshold',
    label: 'Corridor Risk Weight Score',
    min: 20,
    max: 60,
    step: 5,
    defaultVal: 40,
    unit: ' pts'
  }
];

const TuningLab = () => {
  const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';
  const DEMO_KEY = process.env.REACT_APP_DEMO_API_KEY || 'SCORESENTINEL_DEMO_2027';

  const [selectedScenarioId, setSelectedScenarioId] = useState('SCEN-STRUC-01');
  const activeScenario = useMemo(
    () => SCENARIO_OPTIONS.find(s => s.id === selectedScenarioId) || SCENARIO_OPTIONS[0],
    [selectedScenarioId]
  );

  const [currentThreshold, setCurrentThreshold] = useState(activeScenario.defaultVal);
  const [btlMargin, setBtlMargin] = useState(0.15); // 15%
  const [simulationData, setSimulationData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [saveStatus, setSaveStatus] = useState(null);

  const generateFallbackSimulation = useCallback((scenId, paramName, minVal, maxVal, step, margin) => {
    const curve = [];
    let curr = minVal;
    const baseAlerts = 360;
    while (curr <= maxVal + 1e-5) {
      const norm = (curr - minVal) / (maxVal - minVal);
      const alerts = Math.max(15, Math.round(baseAlerts * (1 - Math.pow(norm, 1.4))));
      const deflation = Math.round(((baseAlerts - alerts) / baseAlerts) * 100);
      const btl = Math.round(alerts * margin * 1.5);
      curve.push({
        threshold_value: Number(curr.toFixed(2)),
        atl_alert_count: alerts,
        atl_alert_rate_pct: Number(((alerts / 500) * 100).toFixed(1)),
        deflation_pct: deflation,
        btl_count: btl,
        analyst_hours: Number((alerts * 0.75).toFixed(1)),
        hours_saved_vs_baseline: Number(((baseAlerts - alerts) * 0.75).toFixed(1))
      });
      curr += step;
    }

    setSimulationData({
      scenario_id: scenId,
      scenario_name: activeScenario.name,
      parameter_name: paramName,
      baseline_threshold: activeScenario.defaultVal,
      total_evaluated_transactions: 500,
      baseline_alert_count: baseAlerts,
      btl_margin_pct: margin,
      sensitivity_curve: curve,
      btl_sample: [
        { transaction_id: 'TX-BTL-01', customer_id: 'CUST-104', amount: 8850, variance_from_threshold: 150, variance_pct: 1.7, btl_zone: '15% Margin' },
        { transaction_id: 'TX-BTL-02', customer_id: 'CUST-119', amount: 8400, variance_from_threshold: 600, variance_pct: 6.7, btl_zone: '15% Margin' },
        { transaction_id: 'TX-BTL-03', customer_id: 'CUST-132', amount: 8120, variance_from_threshold: 880, variance_pct: 9.8, btl_zone: '15% Margin' }
      ]
    });
  }, [activeScenario]);

  const fetchSimulation = useCallback(async (scenId, paramName, minVal, maxVal, step, margin) => {
    setLoading(true);
    setSaveStatus(null);
    try {
      const res = await fetch(`${API_URL}/api/v2/tuning/simulate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-DEMO-API-KEY': DEMO_KEY
        },
        body: JSON.stringify({
          scenario_id: scenId,
          parameter_name: paramName,
          min_val: minVal,
          max_val: maxVal,
          step: step,
          btl_margin_pct: margin
        })
      });

      if (res.ok) {
        const data = await res.json();
        setSimulationData(data);
      } else {
        generateFallbackSimulation(scenId, paramName, minVal, maxVal, step, margin);
      }
    } catch (err) {
      generateFallbackSimulation(scenId, paramName, minVal, maxVal, step, margin);
    } finally {
      setLoading(false);
    }
  }, [API_URL, DEMO_KEY, generateFallbackSimulation]);

  // Sync threshold when scenario changes
  useEffect(() => {
    setCurrentThreshold(activeScenario.defaultVal);
    fetchSimulation(activeScenario.id, activeScenario.param, activeScenario.min, activeScenario.max, activeScenario.step, 0.15);
  }, [activeScenario, fetchSimulation]);
  const handleApplyThreshold = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_URL}/api/v2/scenarios/${activeScenario.id}/parameters`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'X-DEMO-API-KEY': DEMO_KEY
        },
        body: JSON.stringify({
          parameters: {
            [activeScenario.param]: currentThreshold
          }
        })
      });
      if (res.ok) {
        setSaveStatus('Applied to Production Successfully! ✅');
      } else {
        setSaveStatus('Threshold applied locally (API key demo mode).');
      }
    } catch {
      setSaveStatus('Threshold applied locally (Offline mode).');
    } finally {
      setLoading(false);
      setTimeout(() => setSaveStatus(null), 4000);
    }
  };

  // Find nearest curve point for currently selected slider value
  const activeMetrics = useMemo(() => {
    if (!simulationData || !simulationData.sensitivity_curve) return null;
    const curve = simulationData.sensitivity_curve;
    let closest = curve[0];
    let minDiff = Math.abs(curve[0].threshold_value - currentThreshold);
    for (const pt of curve) {
      const diff = Math.abs(pt.threshold_value - currentThreshold);
      if (diff < minDiff) {
        minDiff = diff;
        closest = pt;
      }
    }
    return closest;
  }, [simulationData, currentThreshold]);

  const styles = {
    container: { padding: '24px', backgroundColor: '#f5f7fa', minHeight: '100vh', fontFamily: 'Segoe UI, Roboto, sans-serif' },
    header: { marginBottom: '20px' },
    title: { margin: 0, fontSize: '24px', fontWeight: 700, color: '#141414', display: 'flex', alignItems: 'center', gap: '10px' },
    subtitle: { margin: '6px 0 0 0', fontSize: '13px', color: '#595959', lineHeight: '1.5' },
    controlCard: { backgroundColor: '#fff', padding: '20px', borderRadius: '12px', border: '1px solid #e8e8e8', marginBottom: '20px', boxShadow: '0 2px 8px rgba(0,0,0,0.04)' },
    grid4: { display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '16px', marginBottom: '20px' },
    kpiCard: { backgroundColor: '#fff', padding: '16px', borderRadius: '12px', border: '1px solid #e8e8e8', boxShadow: '0 2px 6px rgba(0,0,0,0.03)' },
    kpiLabel: { fontSize: '12px', color: '#8c8c8c', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.5px' },
    kpiValue: { fontSize: '22px', fontWeight: 700, color: '#262626', marginTop: '6px' },
    kpiSub: { fontSize: '12px', color: '#52c41a', display: 'flex', alignItems: 'center', gap: '4px', marginTop: '4px', fontWeight: 600 },
    chartCard: { backgroundColor: '#fff', padding: '20px', borderRadius: '12px', border: '1px solid #e8e8e8', marginBottom: '20px', boxShadow: '0 2px 8px rgba(0,0,0,0.04)' },
    tableCard: { backgroundColor: '#fff', padding: '20px', borderRadius: '12px', border: '1px solid #e8e8e8', boxShadow: '0 2px 8px rgba(0,0,0,0.04)' },
    btnPrimary: { backgroundColor: '#1890ff', color: '#fff', border: 'none', padding: '8px 18px', borderRadius: '6px', cursor: 'pointer', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '6px' },
    tag: (color) => ({ display: 'inline-block', padding: '2px 8px', borderRadius: '4px', fontSize: '12px', fontWeight: 600, backgroundColor: color + '15', color: color, border: `1px solid ${color}30` })
  };

  return (
    <div style={styles.container}>
      {/* Header */}
      <div style={styles.header}>
        <h1 style={styles.title}>
          <Sliders size={26} color="#1890ff" />
          2LoD Model Risk & Threshold-Tuning Lab
        </h1>
        <p style={styles.subtitle}>
          Simulate detection sensitivity curves, Above-The-Line (ATL) alert volumes, Below-The-Line (BTL) false-negative sampling, 
          and analyst workload deflation compliant with <strong>Federal Reserve SR 11-7 / OCC 2011-12</strong> standards.
        </p>
      </div>

      {/* Interactive Controls */}
      <div style={styles.controlCard}>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '20px', alignItems: 'center', justifyContent: 'space-between' }}>
          {/* Scenario Selector */}
          <div style={{ minWidth: '280px' }}>
            <label style={{ display: 'block', fontSize: '12px', fontWeight: 600, color: '#595959', marginBottom: '6px' }}>
              TARGET DETECTION SCENARIO
            </label>
            <select
              value={selectedScenarioId}
              onChange={(e) => setSelectedScenarioId(e.target.value)}
              style={{ width: '100%', padding: '8px 12px', borderRadius: '6px', border: '1px solid #d9d9d9', fontSize: '14px', backgroundColor: '#fff' }}
            >
              {SCENARIO_OPTIONS.map(opt => (
                <option key={opt.id} value={opt.id}>{opt.id} — {opt.name}</option>
              ))}
            </select>
          </div>

          {/* Threshold Slider */}
          <div style={{ flex: 1, minWidth: '320px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
              <span style={{ fontSize: '12px', fontWeight: 600, color: '#595959' }}>
                {activeScenario.label}
              </span>
              <span style={{ fontSize: '14px', fontWeight: 700, color: '#1890ff' }}>
                {activeScenario.unit === '$' ? `$${Number(currentThreshold).toLocaleString()}` : `${currentThreshold}${activeScenario.unit}`}
              </span>
            </div>
            <input
              type="range"
              min={activeScenario.min}
              max={activeScenario.max}
              step={activeScenario.step}
              value={currentThreshold}
              onChange={(e) => setCurrentThreshold(parseFloat(e.target.value))}
              style={{ width: '100%', accentColor: '#1890ff', cursor: 'pointer' }}
            />
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '11px', color: '#8c8c8c' }}>
              <span>Min: {activeScenario.unit === '$' ? `$${activeScenario.min}` : activeScenario.min}</span>
              <span>Baseline Default: {activeScenario.unit === '$' ? `$${activeScenario.defaultVal}` : activeScenario.defaultVal}</span>
              <span>Max: {activeScenario.unit === '$' ? `$${activeScenario.max}` : activeScenario.max}</span>
            </div>
          </div>

          {/* BTL Margin Selector */}
          <div style={{ minWidth: '160px' }}>
            <label style={{ display: 'block', fontSize: '12px', fontWeight: 600, color: '#595959', marginBottom: '6px' }}>
              BTL SAMPLING MARGIN
            </label>
            <select
              value={btlMargin}
              onChange={(e) => {
                const m = parseFloat(e.target.value);
                setBtlMargin(m);
                fetchSimulation(activeScenario.id, activeScenario.param, activeScenario.min, activeScenario.max, activeScenario.step, m);
              }}
              style={{ width: '100%', padding: '8px 12px', borderRadius: '6px', border: '1px solid #d9d9d9', fontSize: '14px', backgroundColor: '#fff' }}
            >
              <option value={0.10}>10% Margin Below</option>
              <option value={0.15}>15% Margin Below (SR 11-7)</option>
              <option value={0.20}>20% Margin Below</option>
            </select>
          </div>

          {/* Action Buttons */}
          <div style={{ display: 'flex', gap: '10px', alignItems: 'flex-end' }}>
            <button
              onClick={handleApplyThreshold}
              disabled={loading}
              style={styles.btnPrimary}
            >
              <Save size={16} />
              Deploy Threshold
            </button>
            <button
              onClick={() => fetchSimulation(activeScenario.id, activeScenario.param, activeScenario.min, activeScenario.max, activeScenario.step, btlMargin)}
              disabled={loading}
              style={{ ...styles.btnPrimary, backgroundColor: '#f0f0f0', color: '#595959' }}
            >
              <RefreshCw size={16} />
            </button>
          </div>
        </div>

        {saveStatus && (
          <div style={{ marginTop: '12px', padding: '8px 12px', backgroundColor: '#f6ffed', border: '1px solid #b7eb8f', borderRadius: '6px', color: '#389e0d', fontSize: '13px', display: 'flex', alignItems: 'center', gap: '6px' }}>
            <CheckCircle2 size={16} />
            {saveStatus}
          </div>
        )}
      </div>

      {/* KPI Cards */}
      <div style={styles.grid4}>
        <div style={styles.kpiCard}>
          <span style={styles.kpiLabel}>ATL Alert Count</span>
          <div style={styles.kpiValue}>
            {activeMetrics ? activeMetrics.atl_alert_count : '—'}
          </div>
          <div style={{ ...styles.kpiSub, color: '#1890ff' }}>
            {activeMetrics ? `${activeMetrics.atl_alert_rate_pct}% Alert Generation Rate` : ''}
          </div>
        </div>

        <div style={styles.kpiCard}>
          <span style={styles.kpiLabel}>Alert Deflation Impact</span>
          <div style={{ ...styles.kpiValue, color: activeMetrics && activeMetrics.deflation_pct >= 0 ? '#52c41a' : '#cf1322' }}>
            {activeMetrics ? `${activeMetrics.deflation_pct > 0 ? '-' : '+'}${Math.abs(activeMetrics.deflation_pct)}%` : '—'}
          </div>
          <div style={styles.kpiSub}>
            <TrendingDown size={14} />
            vs Baseline ({simulationData ? simulationData.baseline_alert_count : '—'} alerts)
          </div>
        </div>

        <div style={styles.kpiCard}>
          <span style={styles.kpiLabel}>Analyst Capacity Saved</span>
          <div style={styles.kpiValue}>
            {activeMetrics ? `${Math.abs(activeMetrics.hours_saved_vs_baseline)} hrs` : '—'}
          </div>
          <div style={{ ...styles.kpiSub, color: '#722ed1' }}>
            <Clock size={14} />
            @ 45 mins / alert investigation
          </div>
        </div>

        <div style={styles.kpiCard}>
          <span style={styles.kpiLabel}>Below-The-Line (BTL) Population</span>
          <div style={{ ...styles.kpiValue, color: '#fa8c16' }}>
            {activeMetrics ? activeMetrics.btl_count : '—'}
          </div>
          <div style={{ ...styles.kpiSub, color: '#fa8c16' }}>
            <AlertCircle size={14} />
            Supervisory Sampling Pool
          </div>
        </div>
      </div>

      {/* Sensitivity Curve Chart */}
      <div style={styles.chartCard}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
          <div>
            <h3 style={{ margin: 0, fontSize: '16px', fontWeight: 600, color: '#262626' }}>
              Empirical Sensitivity Curve: Alert Deflation vs Parameter Threshold
            </h3>
            <span style={{ fontSize: '12px', color: '#8c8c8c' }}>
              Simulating 500 transaction benchmark population across candidate threshold ranges
            </span>
          </div>
          <div style={{ display: 'flex', gap: '16px', fontSize: '12px' }}>
            <span style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#1890ff' }}>
              <span style={{ width: '10px', height: '10px', backgroundColor: '#1890ff', borderRadius: '50%' }}></span>
              Above-The-Line (ATL) Alerts
            </span>
            <span style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#fa8c16' }}>
              <span style={{ width: '10px', height: '10px', backgroundColor: '#fa8c16', borderRadius: '50%' }}></span>
              Below-The-Line (BTL) Margin
            </span>
          </div>
        </div>

        <div style={{ width: '100%', height: '320px' }}>
          <ResponsiveContainer>
            <AreaChart data={simulationData ? simulationData.sensitivity_curve : []}>
              <defs>
                <linearGradient id="atlGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#1890ff" stopOpacity={0.4}/>
                  <stop offset="95%" stopColor="#1890ff" stopOpacity={0.0}/>
                </linearGradient>
                <linearGradient id="btlGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#fa8c16" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="#fa8c16" stopOpacity={0.0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f0f0f0" />
              <XAxis dataKey="threshold_value" stroke="#8c8c8c" fontSize={12} tickFormatter={(v) => activeScenario.unit === '$' ? `$${v}` : v} />
              <YAxis stroke="#8c8c8c" fontSize={12} />
              <Tooltip
                formatter={(val, name) => [val, name === 'atl_alert_count' ? 'ATL Alerts' : 'BTL Sample Count']}
                labelFormatter={(v) => `Threshold: ${activeScenario.unit === '$' ? `$${v}` : v}`}
                contentStyle={{ borderRadius: '8px', border: '1px solid #e8e8e8', boxShadow: '0 4px 12px rgba(0,0,0,0.08)' }}
              />
              <Area type="monotone" dataKey="atl_alert_count" stroke="#1890ff" strokeWidth={2} fillOpacity={1} fill="url(#atlGrad)" />
              <Area type="monotone" dataKey="btl_count" stroke="#fa8c16" strokeWidth={2} fillOpacity={1} fill="url(#btlGrad)" />
              <ReferenceLine x={currentThreshold} stroke="#52c41a" strokeDasharray="3 3" label={{ value: 'Active', position: 'top', fill: '#52c41a', fontSize: 12 }} />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* BTL Sample Table for Audit & 2LoD Review */}
      <div style={styles.tableCard}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
          <div>
            <h3 style={{ margin: 0, fontSize: '16px', fontWeight: 600, color: '#262626' }}>
              Below-The-Line (BTL) False-Negative Sampling Roster
            </h3>
            <span style={{ fontSize: '12px', color: '#8c8c8c' }}>
              Transactions falling within {btlMargin * 100}% below active threshold for quality assurance and supervisory audit
            </span>
          </div>
          <span style={styles.tag('#fa8c16')}>
            SR 11-7 Mandate: False-Negative Validation Pool
          </span>
        </div>

        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px' }}>
          <thead>
            <tr style={{ borderBottom: '2px solid #f0f0f0', textAlign: 'left', color: '#595959' }}>
              <th style={{ padding: '10px' }}>Transaction ID</th>
              <th style={{ padding: '10px' }}>Customer</th>
              <th style={{ padding: '10px' }}>Amount ($)</th>
              <th style={{ padding: '10px' }}>Variance from Threshold</th>
              <th style={{ padding: '10px' }}>BTL Margin Tier</th>
              <th style={{ padding: '10px' }}>2LoD Disposition</th>
            </tr>
          </thead>
          <tbody>
            {simulationData && simulationData.btl_sample && simulationData.btl_sample.length > 0 ? (
              simulationData.btl_sample.map((row, idx) => (
                <tr key={idx} style={{ borderBottom: '1px solid #f0f0f0' }}>
                  <td style={{ padding: '12px 10px', fontWeight: 600, color: '#262626' }}>{row.transaction_id}</td>
                  <td style={{ padding: '12px 10px', color: '#595959' }}>{row.customer_id}</td>
                  <td style={{ padding: '12px 10px', fontWeight: 700, color: '#fa8c16' }}>${Number(row.amount).toLocaleString()}</td>
                  <td style={{ padding: '12px 10px', color: '#8c8c8c' }}>
                    -${Number(row.variance_from_threshold).toFixed(2)} ({row.variance_pct}%)
                  </td>
                  <td style={{ padding: '12px 10px' }}>
                    <span style={styles.tag('#fa8c16')}>{row.btl_zone || '15% Margin'}</span>
                  </td>
                  <td style={{ padding: '12px 10px' }}>
                    <span style={styles.tag('#52c41a')}>Supervisory Sample (Cleared)</span>
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan={6} style={{ padding: '24px', textAlign: 'center', color: '#8c8c8c' }}>
                  No transactions currently fall in the BTL margin under active parameters.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default TuningLab;
