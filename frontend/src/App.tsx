import { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import AgentsPage from './pages/AgentsPage';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import { api } from './services/api';
import HospitalLocator from './pages/HospitalLocator';
import VideoConsultation from './pages/VideoConsultation';
import AdminDashboard from './pages/AdminDashboard';
import Login from './pages/Login';
import Register from './pages/Register';
import HomePage from './pages/HomePage';
import DoctorAvailability from './pages/DoctorAvailability';
import VoiceAgent from './pages/VoiceAgent';
import Messages from './pages/Messages';

// Protected Route Component
function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const isAuthenticated = localStorage.getItem('user_id') && localStorage.getItem('token');
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" replace />;
}

// Admin Only Route Component
function AdminRoute({ children }: { children: React.ReactNode }) {
  const isAuthenticated = localStorage.getItem('user_id') && localStorage.getItem('token');
  const userType = localStorage.getItem('user_type');
  
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  
  // For now, we'll check if user_type is explicitly ADMIN (you can add ADMIN to UserType enum later)
  // or we can restrict it to specific admin user IDs
  const isAdmin = userType === 'ADMIN' || localStorage.getItem('user_id') === 'admin_001';
  
  return isAdmin ? <>{children}</> : <Navigate to="/dashboard" replace />;
}

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
      <Routes>
        {/* Public Routes */}
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />

        {/* Protected Routes */}
        <Route
          path="/*"
          element={
            <ProtectedRoute>
              <div className="flex h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-purple-50 overflow-hidden">
                <Sidebar />
                
                <div className="flex-1 flex flex-col overflow-hidden">
                  <Header isConnected={isConnected} />
                  
                  <main className="flex-1 overflow-y-auto p-6">
                    <Routes>
                      <Route path="/" element={<Navigate to="/home" replace />} />
                      <Route path="/home" element={<HomePage />} />
                      <Route path="/doctor-status" element={<DoctorAvailability />} />
                      <Route path="/dashboard" element={<Dashboard />} />
                      <Route path="/agents" element={<AgentsPage />} />
                      <Route path="/voice-agent" element={<VoiceAgent />} />
                      <Route path="/messages" element={<Messages />} />
                      <Route path="/hospitals" element={<HospitalLocator />} />
                      <Route path="/video-consultation" element={<VideoConsultation />} />
                      <Route 
                        path="/admin" 
                        element={
                          <AdminRoute>
                            <AdminDashboard />
                          </AdminRoute>
                        } 
                      />
                    </Routes>
                  </main>
                </div>
              </div>
            </ProtectedRoute>
          }
        />
      </Routes>
    </Router>
  );
}

export default App;
