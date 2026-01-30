import { Wifi, WifiOff, Bell, User } from 'lucide-react';

interface HeaderProps {
  isConnected: boolean;
}

const Header = ({ isConnected }: HeaderProps) => {
  return (
    <header className="h-20 bg-white/70 backdrop-blur-xl border-b border-slate-200/50 shadow-sm">
      <div className="h-full px-8 flex items-center justify-between">
        {/* Title */}
        <div>
          <h2 className="text-2xl font-bold font-display gradient-text">
            Multi-Agent Medical Assistant
          </h2>
          <p className="text-sm text-slate-600">Powered by 7 Specialized AI Agents</p>
        </div>

        {/* Right section */}
        <div className="flex items-center space-x-6">
          {/* Connection Status */}
          <div className={`flex items-center space-x-2 px-4 py-2 rounded-xl ${ 
            isConnected 
              ? 'bg-green-100 text-green-700' 
              : 'bg-red-100 text-red-700'
          }`}>
            {isConnected ? (
              <Wifi className="w-4 h-4" />
            ) : (
              <WifiOff className="w-4 h-4" />
            )}
            <span className="text-sm font-medium">
              {isConnected ? 'Connected' : 'Disconnected'}
            </span>
          </div>

          {/* Notifications */}
          <button className="relative p-2 hover:bg-slate-100 rounded-xl transition-colors">
            <Bell className="w-5 h-5 text-slate-600" />
            <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
          </button>

          {/* User Profile */}
          <button className="flex items-center space-x-3 px-4 py-2 hover:bg-slate-100 rounded-xl transition-colors">
            <div className="w-9 h-9 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full flex items-center justify-center">
              <User className="w-5 h-5 text-white" />
            </div>
            <div className="text-left">
              <p className="text-sm font-semibold text-slate-800">Medical Professional</p>
              <p className="text-xs text-slate-500">Admin</p>
            </div>
          </button>
        </div>
      </div>
    </header>
  );
};

export default Header;
