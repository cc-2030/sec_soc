import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import { logRoutes } from './routes/logs.js';
import { toolRoutes } from './routes/tools.js';
import { aiRoutes } from './routes/ai.js';
import { dashboardRoutes } from './routes/dashboard.js';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 3001;

app.use(cors());
app.use(express.json());

// 路由
app.use('/api/logs', logRoutes);
app.use('/api/tools', toolRoutes);
app.use('/api/ai', aiRoutes);
app.use('/api/dashboard', dashboardRoutes);

app.listen(PORT, () => {
  console.log(`安全平台后端运行在 http://localhost:${PORT}`);
});
