export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  agent?: string;
  confidence?: number;
  metadata?: any;
  image_path?: string;
}

export interface Agent {
  id: string;
  name: string;
  description: string;
  icon: string;
  color: string;
  capabilities: string[];
  status: 'active' | 'inactive';
}

export interface AnalyticsData {
  totalQueries: number;
  successRate: number;
  avgResponseTime: number;
  agentUsage: { [key: string]: number };
}
