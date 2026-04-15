import { Brain, Search, Stethoscope, Shield, Eye, Mic } from 'lucide-react';

const AgentsPage = () => {
  const agents = [
    {
      name: 'Psychology Agent',
      icon: Brain,
      description: 'Mental health support and psychological counseling',
      color: 'purple',
      status: 'active',
      capabilities: ['Mental Health', 'Emotional Support', 'Crisis Management'],
    },
    {
      name: 'RAG Agent',
      icon: Search,
      description: 'Medical knowledge retrieval from vast medical databases',
      color: 'blue',
      status: 'active',
      capabilities: ['Knowledge Search', 'Evidence-Based', 'Research Articles'],
    },
    {
      name: 'Web Search Agent',
      icon: Search,
      description: 'Real-time medical research and latest information',
      color: 'green',
      status: 'active',
      capabilities: ['Latest Research', 'Clinical Trials', 'Medical News'],
    },
    {
      name: 'Chest X-ray Agent',
      icon: Stethoscope,
      description: 'Chest X-ray analysis for COVID-19 and lung diseases',
      color: 'orange',
      status: 'active',
      capabilities: ['COVID Detection', 'Pneumonia', 'Lung Diseases'],
    },
    {
      name: 'Skin Lesion Agent',
      icon: Eye,
      description: 'Dermatology analysis and skin condition classification',
      color: 'pink',
      status: 'active',
      capabilities: ['Skin Analysis', 'Lesion Classification', 'Dermatology'],
    },
    {
      name: 'Guardrails Agent',
      icon: Shield,
      description: 'Safety and accuracy validation for all responses',
      color: 'gray',
      status: 'active',
      capabilities: ['Safety Check', 'Validation', 'Quality Assurance'],
    },
    {
      name: 'Voice Agent',
      icon: Mic,
      description: 'Realtime voice Q&A for wellness and mental health (Deepgram + Hugging Face Llama)',
      color: 'indigo',
      status: 'active',
      capabilities: ['Voice STT/TTS', 'Mental Health', 'Medical Education'],
    },
  ];

  return (
    <div className="space-y-6">
      <div className="glass-morphism rounded-2xl p-8">
        <h2 className="text-3xl font-bold font-display gradient-text mb-2">
          AI Agents Overview
        </h2>
        <p className="text-slate-600 mb-8">
          7 specialized AI agents working together to provide comprehensive medical assistance
        </p>

        <div className="grid grid-cols-2 gap-6">
          {agents.map((agent, idx) => (
            <div key={idx} className="bg-white rounded-2xl p-6 border-2 border-slate-200 hover:border-blue-400 hover:shadow-xl transition-all duration-300 card-hover">
              <div className="flex items-start space-x-4">
                <div className={`w-14 h-14 bg-gradient-to-br from-${agent.color}-400 to-${agent.color}-600 rounded-xl flex items-center justify-center flex-shrink-0`}>
                  <agent.icon className="w-7 h-7 text-white" />
                </div>
                
                <div className="flex-1">
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="text-xl font-bold text-slate-800">{agent.name}</h3>
                    <span className="px-3 py-1 bg-green-100 text-green-700 text-xs font-semibold rounded-full">
                      {agent.status}
                    </span>
                  </div>
                  
                  <p className="text-sm text-slate-600 mb-4">{agent.description}</p>
                  
                  <div className="flex flex-wrap gap-2">
                    {agent.capabilities.map((cap, capIdx) => (
                      <span key={capIdx} className="px-3 py-1 bg-slate-100 text-slate-700 text-xs font-medium rounded-lg">
                        {cap}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default AgentsPage;
