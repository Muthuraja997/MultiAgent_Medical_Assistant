import { useState, useRef } from 'react';
import {
  Send,
  Mic,
  Sparkles,
  Brain,
  Search,
  Stethoscope,
  Shield,
  Upload,
  X,
} from 'lucide-react';
import { api } from '../services/api';
import { Message } from '../types';

const Dashboard = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [selectedImage, setSelectedImage] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleImageSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedImage(file);
      const reader = new FileReader();
      reader.onloadend = () => {
        setImagePreview(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleSendMessage = async () => {
    if (!inputMessage.trim() && !selectedImage) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: inputMessage,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      let response;
      
      if (selectedImage) {
        // Upload image first
        const uploadResponse = await api.uploadImage(selectedImage);
        // Then send query with image
        response = await api.analyzeImage(uploadResponse.filepath, inputMessage || 'Analyze this medical image');
      } else {
        response = await api.chat({
          query: inputMessage,
          conversation_history: messages.map(m => ({ role: m.role, content: m.content })),
        });
      }

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response.response,
        timestamp: new Date(),
        agent: response.agent_name,
        confidence: response.confidence,
      };

      setMessages(prev => [...prev, assistantMessage]);
      setSelectedImage(null);
      setImagePreview(null);
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'Sorry, I encountered an error processing your request. Please try again.',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
      scrollToBottom();
    }
  };

  const quickActions = [
    { icon: Brain, label: 'Mental Health', color: 'purple', query: 'I need mental health support' },
    { icon: Search, label: 'Research', color: 'blue', query: 'Search for latest medical research' },
    { icon: Stethoscope, label: 'Diagnosis', color: 'green', query: 'Help me understand my symptoms' },
    { icon: Shield, label: 'Safety Check', color: 'red', query: 'Is this information medically accurate?' },
  ];

  return (
    <div className="h-full flex flex-col">
      {/* Stats Cards */}
      <div className="grid grid-cols-4 gap-6 mb-6">
        {[
          { label: 'Active Agents', value: '7', icon: Brain, color: 'blue' },
          { label: 'Queries Today', value: '24', icon: Sparkles, color: 'purple' },
          { label: 'Accuracy Rate', value: '99.2%', icon: Shield, color: 'green' },
          { label: 'Response Time', value: '1.2s', icon: Sparkles, color: 'orange' },
        ].map((stat, idx) => (
          <div key={idx} className="glass-morphism rounded-2xl p-6 card-hover">
            <div className="flex items-center justify-between mb-3">
              <stat.icon className={`w-8 h-8 text-${stat.color}-600`} />
              <span className={`text-3xl font-bold text-${stat.color}-600`}>{stat.value}</span>
            </div>
            <p className="text-sm text-slate-600 font-medium">{stat.label}</p>
          </div>
        ))}
      </div>

      {/* Main Chat Interface */}
      <div className="flex-1 glass-morphism rounded-2xl flex flex-col overflow-hidden">
        {/* Chat Header */}
        <div className="px-8 py-6 border-b border-slate-200/50">
          <h3 className="text-2xl font-bold font-display gradient-text mb-2">
            AI Medical Consultation
          </h3>
          <p className="text-sm text-slate-600">
            Ask anything about medical conditions, symptoms, research, or upload medical images for analysis
          </p>
        </div>

        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto p-8 space-y-6">
          {messages.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center text-center">
              <div className="w-20 h-20 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full flex items-center justify-center mb-6 animate-float">
                <Sparkles className="w-10 h-10 text-white" />
              </div>
              <h4 className="text-2xl font-bold text-slate-800 mb-3">
                Welcome to Multi-Agent Medical Assistant
              </h4>
              <p className="text-slate-600 mb-8 max-w-2xl">
                Get instant medical insights powered by 7 specialized AI agents. Ask questions, upload medical images, or get mental health support.
              </p>
              
              {/* Quick Actions */}
              <div className="grid grid-cols-4 gap-4 w-full max-w-4xl">
                {quickActions.map((action, idx) => (
                  <button
                    key={idx}
                    onClick={() => setInputMessage(action.query)}
                    className="p-6 bg-white rounded-2xl border-2 border-slate-200 hover:border-blue-400 hover:shadow-xl transition-all duration-300 group"
                  >
                    <action.icon className={`w-8 h-8 text-${action.color}-600 mx-auto mb-3 group-hover:scale-110 transition-transform`} />
                    <p className="text-sm font-semibold text-slate-700">{action.label}</p>
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <>
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'} animate-fadeIn`}
                >
                  <div
                    className={`max-w-3xl px-6 py-4 rounded-2xl ${
                      message.role === 'user'
                        ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white'
                        : 'bg-white border-2 border-slate-200'
                    }`}
                  >
                    {message.agent && (
                      <div className="flex items-center space-x-2 mb-2 pb-2 border-b border-slate-200">
                        <Brain className="w-4 h-4 text-purple-600" />
                        <span className="text-xs font-semibold text-purple-600">
                          {message.agent}
                        </span>
                        {message.confidence && (
                          <span className="text-xs text-slate-500">
                            • {(message.confidence * 100).toFixed(0)}% confident
                          </span>
                        )}
                      </div>
                    )}
                    <p className={`${message.role === 'user' ? 'text-white' : 'text-slate-800'}`}>
                      {message.content}
                    </p>
                    <p className={`text-xs mt-2 ${message.role === 'user' ? 'text-blue-100' : 'text-slate-400'}`}>
                      {message.timestamp.toLocaleTimeString()}
                    </p>
                  </div>
                </div>
              ))}
              {isLoading && (
                <div className="flex justify-start animate-fadeIn">
                  <div className="max-w-3xl px-6 py-4 bg-white border-2 border-slate-200 rounded-2xl">
                    <div className="flex items-center space-x-3">
                      <div className="flex space-x-2">
                        <div className="w-3 h-3 bg-blue-600 rounded-full animate-bounce"></div>
                        <div className="w-3 h-3 bg-purple-600 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                        <div className="w-3 h-3 bg-pink-600 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></div>
                      </div>
                      <span className="text-slate-600 text-sm">AI agents are analyzing...</span>
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </>
          )}
        </div>

        {/* Input Area */}
        <div className="px-8 py-6 border-t border-slate-200/50 bg-slate-50/50">
          {imagePreview && (
            <div className="mb-4 relative inline-block">
              <img src={imagePreview} alt="Preview" className="h-20 w-20 object-cover rounded-xl border-2 border-blue-400" />
              <button
                onClick={() => {
                  setSelectedImage(null);
                  setImagePreview(null);
                }}
                className="absolute -top-2 -right-2 w-6 h-6 bg-red-500 text-white rounded-full flex items-center justify-center hover:bg-red-600 transition-colors"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          )}
          
          <div className="flex items-center space-x-4">
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleImageSelect}
              accept="image/*"
              className="hidden"
            />
            
            <button
              onClick={() => fileInputRef.current?.click()}
              className="p-4 bg-white rounded-xl border-2 border-slate-200 hover:border-blue-400 hover:shadow-lg transition-all duration-300"
              title="Upload medical image"
            >
              <Upload className="w-5 h-5 text-slate-600" />
            </button>

            <button
              className="p-4 bg-white rounded-xl border-2 border-slate-200 hover:border-purple-400 hover:shadow-lg transition-all duration-300"
              title="Voice input"
            >
              <Mic className="w-5 h-5 text-slate-600" />
            </button>

            <div className="flex-1 relative">
              <input
                type="text"
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                placeholder="Ask about symptoms, conditions, or upload a medical image..."
                className="w-full px-6 py-4 bg-white rounded-xl border-2 border-slate-200 focus:border-blue-400 focus:ring-4 focus:ring-blue-100 outline-none transition-all duration-300 text-slate-800"
                disabled={isLoading}
              />
            </div>

            <button
              onClick={handleSendMessage}
              disabled={isLoading || (!inputMessage.trim() && !selectedImage)}
              className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Send className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
