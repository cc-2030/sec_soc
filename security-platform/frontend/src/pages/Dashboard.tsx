import { useEffect, useState } from 'react';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import { ShieldCheck, AlertTriangle, CheckCircle, Server } from 'lucide-react';

interface Overview {
  securityScore: number;
  activeThreats: number;
  resolvedToday: number;
  totalAssets: number;
  trends: { threats: number[]; incidents: number[] };
}

interface Alert {
  id: string;
  severity: string;
  title: string;
  time: string;
  status: string;
}

export default function Dashboard() {
  const [overview, setOverview] = useState<Overview | null>(null);
  const [alerts, setAlerts] = useState<Alert[]>([]);

  useEffect(() => {
    fetch('/api/dashboard/overview').then(r => r.json()).then(setOverview);
    fetch('/api/dashboard/alerts').then(r => r.json()).then(setAlerts);
  }, []);

  const chartData = overview?.trends.threats.map((t, i) => ({
    day: `Day ${i + 1}`,
    threats: t,
    incidents: overview.trends.incidents[i],
  })) || [];

  return (
    <div>
      <div className="page-header">
        <h2>安全态势总览</h2>
        <p>实时监控系统安全状态</p>
      </div>

      <div className="grid grid-4" style={{ marginBottom: 20 }}>
        <div className="card">
          <div className="card-header"><span className="card-title">安全评分</span><ShieldCheck color="#22c55e" /></div>
          <div className="stat-value green">{overview?.securityScore || '-'}</div>
        </div>
        <div className="card">
          <div className="card-header"><span className="card-title">活跃威胁</span><AlertTriangle color="#ef4444" /></div>
          <div className="stat-value red">{overview?.activeThreats || '-'}</div>
        </div>
        <div className="card">
          <div className="card-header"><span className="card-title">今日已处理</span><CheckCircle color="#38bdf8" /></div>
          <div className="stat-value blue">{overview?.resolvedToday || '-'}</div>
        </div>
        <div className="card">
          <div className="card-header"><span className="card-title">资产总数</span><Server color="#eab308" /></div>
          <div className="stat-value yellow">{overview?.totalAssets || '-'}</div>
        </div>
      </div>

      <div className="grid grid-2">
        <div className="card">
          <div className="card-header"><span className="card-title">威胁趋势 (7天)</span></div>
          <ResponsiveContainer width="100%" height={200}>
            <LineChart data={chartData}>
              <XAxis dataKey="day" stroke="#64748b" fontSize={12} />
              <YAxis stroke="#64748b" fontSize={12} />
              <Tooltip contentStyle={{ background: '#1e293b', border: '1px solid #334155' }} />
              <Line type="monotone" dataKey="threats" stroke="#ef4444" strokeWidth={2} dot={false} />
              <Line type="monotone" dataKey="incidents" stroke="#38bdf8" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="card">
          <div className="card-header"><span className="card-title">实时告警</span></div>
          {alerts.map(alert => (
            <div key={alert.id} className="alert-item">
              <span className={`badge ${alert.severity}`}>{alert.severity}</span>
              <div style={{ flex: 1 }}>
                <div style={{ fontWeight: 500 }}>{alert.title}</div>
                <div style={{ fontSize: 12, color: '#64748b' }}>{alert.time}</div>
              </div>
              <span className={`badge ${alert.status === 'resolved' ? 'low' : 'medium'}`}>{alert.status}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
