import { Routes, Route, NavLink } from 'react-router-dom';
import { Shield, LayoutDashboard, Wrench, FileText, Activity, Brain } from 'lucide-react';
import Dashboard from './pages/Dashboard';
import Tools from './pages/Tools';
import Logs from './pages/Logs';
import Operations from './pages/Operations';
import AIAnalysis from './pages/AIAnalysis';

export default function App() {
  return (
    <div className="app">
      <aside className="sidebar">
        <h1><Shield size={24} /> 安全平台</h1>
        <nav>
          <NavLink to="/" end><LayoutDashboard size={18} /> 仪表盘</NavLink>
          <NavLink to="/tools"><Wrench size={18} /> 安全工具</NavLink>
          <NavLink to="/logs"><FileText size={18} /> 日志分析</NavLink>
          <NavLink to="/operations"><Activity size={18} /> 安全运营</NavLink>
          <NavLink to="/ai"><Brain size={18} /> AI 分析</NavLink>
        </nav>
      </aside>
      <main className="main">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/tools" element={<Tools />} />
          <Route path="/logs" element={<Logs />} />
          <Route path="/operations" element={<Operations />} />
          <Route path="/ai" element={<AIAnalysis />} />
        </Routes>
      </main>
    </div>
  );
}
