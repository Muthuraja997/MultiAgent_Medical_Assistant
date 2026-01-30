import { TrendingUp, Users, Clock, CheckCircle } from 'lucide-react';

const Analytics = () => {
  return (
    <div className="space-y-6">
      <div className="glass-morphism rounded-2xl p-8">
        <h2 className="text-3xl font-bold font-display gradient-text mb-6">
          Analytics Dashboard
        </h2>
        
        <div className="grid grid-cols-3 gap-6">
          {[
            { icon: TrendingUp, label: 'Total Queries', value: '1,234', change: '+12%', color: 'blue' },
            { icon: Users, label: 'Active Users', value: '89', change: '+5%', color: 'green' },
            { icon: Clock, label: 'Avg Response Time', value: '1.2s', change: '-8%', color: 'purple' },
            { icon: CheckCircle, label: 'Success Rate', value: '99.2%', change: '+2%', color: 'green' },
          ].map((stat, idx) => (
            <div key={idx} className="bg-white rounded-xl p-6 border-2 border-slate-200">
              <div className="flex items-center justify-between mb-4">
                <stat.icon className={`w-8 h-8 text-${stat.color}-600`} />
                <span className={`text-sm font-semibold ${stat.change.startsWith('+') ? 'text-green-600' : 'text-red-600'}`}>
                  {stat.change}
                </span>
              </div>
              <h3 className="text-3xl font-bold text-slate-800 mb-1">{stat.value}</h3>
              <p className="text-sm text-slate-600">{stat.label}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Analytics;
