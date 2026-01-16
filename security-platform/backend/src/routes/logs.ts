import { Router } from 'express';
import { v4 as uuidv4 } from 'uuid';

const router = Router();

// 模拟日志数据
const logs: SecurityLog[] = [
  { id: uuidv4(), timestamp: new Date().toISOString(), level: 'warning', source: 'firewall', message: '检测到异常流量', ip: '192.168.1.100', details: { port: 443, protocol: 'HTTPS' } },
  { id: uuidv4(), timestamp: new Date().toISOString(), level: 'error', source: 'ids', message: 'SQL注入攻击尝试', ip: '10.0.0.55', details: { payload: "' OR 1=1 --" } },
  { id: uuidv4(), timestamp: new Date().toISOString(), level: 'info', source: 'auth', message: '用户登录成功', ip: '192.168.1.50', details: { user: 'admin' } },
];

interface SecurityLog {
  id: string;
  timestamp: string;
  level: 'info' | 'warning' | 'error' | 'critical';
  source: string;
  message: string;
  ip?: string;
  details?: Record<string, unknown>;
}

// 获取日志列表
router.get('/', (req, res) => {
  const { level, source, limit = 100 } = req.query;
  let filtered = [...logs];
  if (level) filtered = filtered.filter(l => l.level === level);
  if (source) filtered = filtered.filter(l => l.source === source);
  res.json(filtered.slice(0, Number(limit)));
});

// 添加日志
router.post('/', (req, res) => {
  const log: SecurityLog = { id: uuidv4(), timestamp: new Date().toISOString(), ...req.body };
  logs.unshift(log);
  res.status(201).json(log);
});

// 获取日志统计
router.get('/stats', (req, res) => {
  const stats = {
    total: logs.length,
    byLevel: { info: 0, warning: 0, error: 0, critical: 0 },
    bySource: {} as Record<string, number>,
  };
  logs.forEach(log => {
    stats.byLevel[log.level]++;
    stats.bySource[log.source] = (stats.bySource[log.source] || 0) + 1;
  });
  res.json(stats);
});

export { router as logRoutes };
