import { useEffect, useState } from 'react';
import { Brain, Zap, AlertCircle, Lightbulb } from 'lucide-react';

interface Threat {
  id: string;
  type: string;
  confidence: number;
  source: string;
  target: string;
}

interface Recommendation {
  priority: string;
  category: string;
  title: string;
  description: string;
}

interface Analysis {
  summary: string;
  riskLevel: string;
  findings: { type: string; severity: string; count: number; recommendation: string }[];
  patterns: string[];
  recommendations: string[];
}

export default function AIAnalysis() {
  const [threats, setThreats] = useState<Threat[]>([]);
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [analysis, setAnalysis] = useState<Analysis | null>(null);
  const [analyzing, setAnalyzing] = useState(false);

  useEffect(() => {
    fetch('/api/ai/detect-threats', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: '{}' })
      .then(r => r.json()).then(d => setThreats(d.threats));
    fetch('/api/ai/recommendations').then(r => r.json()).then(d => setRecommendations(d.recommendations));
  }, []);

  const runAnalysis = async () => {
    setAnalyzing(true);
    const logs = await fetch('/api/logs').then(r => r.json());
    const result = await fetch('/api/ai/analyze-logs', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ logs }),
    }).then(r => r.json());
    setAnalysis(result);
    setAnalyzing(false);
  };

  return (
    <div>
      <div className="page-header">
        <h2>AI 智能分析</h2>
        <p>基于 AI 的威胁检测和安全建议</p>
      </div>

      <div className="card ai-panel" style={{ marginBottom: 20 }}>
        <div className="card-header">
          <span className="card-title"><Brain size={18} style={{ marginRight: 8 }} />AI 日志分析</span>
          <button className="btn btn-primary" onClick={runAnalysis} disabled={analyzing}>
            <Zap size={16} /> {analyzing ? '分析中...' : '开始分析'}
          </button>
        </div>
        {analysis && (
          <div style={{ marginTop: 16 }}>
            <div style={{ display: 'flex', gap: 20, marginBottom: 16 }}>
              <div><strong>风险等级:</strong> <span className={`badge ${analysis.riskLevel === 'high' ? 'critical' : analysis.riskLevel === 'medium' ? 'high' : 'low'}`}>{analysis.riskLevel}</span></div>
              <div><strong>摘要:</strong> {analysis.summary}</div>
            </div>
            <div style={{ marginBottom: 16 }}>
              <strong>发现的问题:</strong>
              <div style={{ display: 'flex', gap: 12, marginTop: 8, flexWrap: 'wrap' }}>
                {analysis.findings.map((f, i) => (
                  <div key={i} style={{ background: '#0f172a', padding: 12, borderRadius: 8, flex: '1 1 200px' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                      <span>{f.type}</span>
                      <span className={`badge ${f.severity}`}>{f.severity}</span>
                    </div>
                    <div style={{ fontSize: 12, color: '#94a3b8', marginTop: 8 }}>{f.recommendation}</div>
                  </div>
                ))}
              </div>
            </div>
            <div>
              <strong>检测到的模式:</strong>
              <div style={{ display: 'flex', gap: 8, marginTop: 8 }}>
                {analysis.patterns.map((p, i) => <span key={i} className="badge medium">{p}</span>)}
              </div>
            </div>
          </div>
        )}
      </div>

      <div className="grid grid-2">
        <div className="card">
          <div className="card-header"><span className="card-title"><AlertCircle size={18} style={{ marginRight: 8 }} />威胁检测</span></div>
          {threats.map(threat => (
            <div key={threat.id} className="alert-item">
              <div style={{ flex: 1 }}>
                <div style={{ fontWeight: 500 }}>{threat.type.replace('_', ' ')}</div>
                <div style={{ fontSize: 12, color: '#64748b' }}>{threat.source} → {threat.target}</div>
              </div>
              <div style={{ textAlign: 'right' }}>
                <div style={{ fontSize: 20, fontWeight: 600, color: threat.confidence > 0.8 ? '#ef4444' : '#eab308' }}>
                  {Math.round(threat.confidence * 100)}%
                </div>
                <div style={{ fontSize: 11, color: '#64748b' }}>置信度</div>
              </div>
            </div>
          ))}
        </div>

        <div className="card">
          <div className="card-header"><span className="card-title"><Lightbulb size={18} style={{ marginRight: 8 }} />AI 安全建议</span></div>
          {recommendations.map((rec, i) => (
            <div key={i} style={{ padding: '12px 0', borderBottom: i < recommendations.length - 1 ? '1px solid #334155' : 'none' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
                <span className={`badge ${rec.priority === 'high' ? 'critical' : rec.priority === 'medium' ? 'high' : 'low'}`}>{rec.priority}</span>
                <span style={{ fontWeight: 500 }}>{rec.title}</span>
              </div>
              <div style={{ fontSize: 13, color: '#94a3b8' }}>{rec.description}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
