import { Link, useLocation } from 'react-router-dom';
import {
  LayoutDashboard,
  Brain,
  BarChart3,
  Settings,
  Activity,
  MapPin,
  Video,
} from 'lucide-react';

const Sidebar = () => {
  const location = useLocation();

  const menuItems = [
    { path: '/dashboard', icon: LayoutDashboard, label: 'Dashboard', color: 'blue' },
    { path: '/agents', icon: Brain, label: 'AI Agents', color: 'purple' },
    { path: '/video-consultation', icon: Video, label: 'Video Call', color: 'indigo' },
    { path: '/hospitals', icon: MapPin, label: 'Hospitals', color: 'red' },
    { path: '/analytics', icon: BarChart3, label: 'Analytics', color: 'green' },
  ];

  return (
    <div className="w-64 bg-gradient-to-b from-slate-900 via-blue-900 to-purple-900 text-white flex flex-col shadow-2xl">
      {/* Logo */}
      <div className="p-6 border-b border-white/10">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-500 rounded-xl flex items-center justify-center">
            <Activity className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-xl font-bold font-display">Medical AI</h1>
            <p className="text-xs text-blue-300">Assistant Platform</p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-2">
        {menuItems.map((item) => {
          const isActive = location.pathname === item.path;
          const Icon = item.icon;
          
          return (
            <Link
              key={item.path}
              to={item.path}
              className={`
                flex items-center space-x-3 px-4 py-3 rounded-xl transition-all duration-300
                ${isActive
                  ? 'bg-white/20 backdrop-blur-xl shadow-lg'
                  : 'hover:bg-white/10 hover:translate-x-1'
                }
              `}
            >
              <Icon className={`w-5 h-5 ${isActive ? 'text-white' : 'text-blue-300'}`} />
              <span className={`font-medium ${isActive ? 'text-white' : 'text-blue-100'}`}>
                {item.label}
              </span>
            </Link>
          );
        })}
      </nav>

      {/* Bottom section */}
      <div className="p-4 border-t border-white/10">
        <Link
          to="/settings"
          className="flex items-center space-x-3 px-4 py-3 rounded-xl hover:bg-white/10 transition-all duration-300"
        >
          <Settings className="w-5 h-5 text-blue-300" />
          <span className="font-medium text-blue-100">Settings</span>
        </Link>
        
        <div className="mt-4 px-4 py-3 bg-white/5 rounded-xl backdrop-blur-xl">
          <p className="text-xs text-blue-300 mb-1">System Status</p>
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
            <span className="text-sm text-white font-medium">All Agents Active</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Sidebar;
