import { Router } from 'express';

const router = Router();

// 仪表盘概览数据
router.get('/overview', (req, res) => {
  res.json({
    securityScore: 78,
    activeThreats: 3,
    resolvedToday: 12,
    totalAssets: 156,
    trends: {
      threats: [5, 8, 3, 7, 4, 6, 3],
      incidents: [2, 1, 4, 2, 3, 1, 2],
    },
  });
});

// 实时告警
router.get('/alerts', (req, res) => {
  res.json([
    { id: 'a1', severity: 'critical', title: '检测到勒索软件活动', time: '2分钟前', status: 'active' },
    { id: 'a2', severity: 'high', title: 'DDoS攻击尝试', time: '15分钟前', status: 'investigating' },
    { id: 'a3', severity: 'medium', title: '异常登录行为', time: '1小时前', status: 'resolved' },
  ]);
});

// 资产状态
router.get('/assets', (req, res) => {
  res.json({
    servers: { total: 45, healthy: 42, warning: 2, critical: 1 },
    endpoints: { total: 89, healthy: 85, warning: 3, critical: 1 },
    applications: { total: 22, healthy: 20, warning: 2, critical: 0 },
  });
});

// 运营指标
router.get('/operations', (req, res) => {
  res.json({
    mttr: 45, // 平均修复时间(分钟)
    mttd: 12, // 平均检测时间(分钟)
    incidentsThisMonth: 28,
    complianceScore: 92,
    patchStatus: { upToDate: 134, pending: 18, critical: 4 },
  });
});

export { router as dashboardRoutes };
