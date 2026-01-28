import { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import Analytics from './pages/Analytics';
import AgentsPage from './pages/AgentsPage';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import { api } from './services/api';
import HospitalLocator from './pages/HospitalLocator';
import VideoConsultation from './pages/VideoConsultation';

function App() {
  const [isConnected, setIsConnected] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check backend connection
    const checkHealth = async () => {
      try {
        await api.healthCheck();
        setIsConnected(true);
      } catch (error) {
        console.error('Backend connection failed:', error);
        setIsConnected(false);
      } finally {
        setLoading(false);
      }
    };

    checkHealth();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-900 via-blue-900 to-purple-900">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-blue-400 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-white text-xl font-semibold">Initializing Medical AI Assistant...</p>
        </div>
      </div>
    );
  }

  return (
    <Router>
      <div className="flex h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-purple-50 overflow-hidden">
        <Sidebar />
        
        <div className="flex-1 flex flex-col overflow-hidden">
          <Header isConnected={isConnected} />
          
          <main className="flex-1 overflow-y-auto p-6">
            <Routes>
              <Route path="/" element={<Navigate to="/dashboard" replace />} />
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/analytics" element={<Analytics />} />
              <Route path="/agents" element={<AgentsPage />} />
              <Route path="/hospitals" element={<HospitalLocator />} />
              <Route path="/video-consultation" element={<VideoConsultation />} />
            </Routes>
          </main>
        </div>
      </div>
    </Router>
  );
}

export default App;
