import { useState, useRef, useCallback } from 'react';
import type { ComponentPropsWithoutRef, ReactNode } from 'react';
import { Link } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';
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
import { api, type ChatResponse, type HumanValidationResponse } from '../services/api';
import { Message } from '../types';

const HITL_MARKER = '\n\n**Human Validation Required:**';

function splitHumanValidationContent(content: string): {
  analysisMarkdown: string;
  showHitlControls: boolean;
} {
  let cut = content.indexOf(HITL_MARKER);
  if (cut < 0) {
    cut = content.indexOf('**Human Validation Required:**');
  }
  if (cut < 0) {
    cut = content.indexOf('Human Validation Required');
  }
  if (cut < 0) {
    return { analysisMarkdown: content, showHitlControls: false };
  }
  return {
    analysisMarkdown: content.slice(0, cut).trimEnd(),
    showHitlControls: true,
  };
}

function stripHumanValidationSection(content: string): string {
  return splitHumanValidationContent(content).analysisMarkdown;
}

function formatValidationFollowUp(res: HumanValidationResponse): string {
  const r = (res.response || '').trim();
  if (!r || /^validation result:\s*yes\b/i.test(r)) {
    return res.message;
  }
  return `${res.message}\n\n${res.response}`;
}

/** Renders model markdown (bold, lists) correctly in assistant bubbles. */
function AssistantMessageBody({ content }: { content: string }) {
  return (
    <div className="text-slate-800 text-[15px] leading-relaxed [&_p]:my-2 [&_p:first-child]:mt-0 [&_p:last-child]:mb-0">
      <ReactMarkdown
        components={{
          strong: ({ children, ...rest }: { children?: ReactNode }) => (
            <strong className="font-semibold text-slate-900" {...rest}>
              {children}
            </strong>
          ),
          em: ({ children, ...rest }) => (
            <em className="italic text-slate-800" {...rest}>
              {children}
            </em>
          ),
          ul: ({ children, ...rest }: ComponentPropsWithoutRef<'ul'>) => (
            <ul className="my-2 list-disc pl-5 space-y-1" {...rest}>
              {children}
            </ul>
          ),
          ol: ({ children, ...rest }: ComponentPropsWithoutRef<'ol'>) => (
            <ol className="my-2 list-decimal pl-5 space-y-1" {...rest}>
              {children}
            </ol>
          ),
          li: ({ children, ...rest }: ComponentPropsWithoutRef<'li'>) => (
            <li className="leading-relaxed" {...rest}>
              {children}
            </li>
          ),
          a: ({ children, ...rest }: ComponentPropsWithoutRef<'a'>) => (
            <a
              className="text-blue-600 underline hover:text-blue-800 break-all"
              target="_blank"
              rel="noopener noreferrer"
              {...rest}
            >
              {children}
            </a>
          ),
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
}

function HumanValidationPanel({
  messageId,
  onDone,
}: {
  messageId: string;
  onDone: (
    messageId: string,
    choice: 'yes' | 'no',
    res: HumanValidationResponse,
    comments?: string
  ) => void;
}) {
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showRejectForm, setShowRejectForm] = useState(false);
  const [comments, setComments] = useState('');

  const submit = async (choice: 'yes' | 'no') => {
    if (choice === 'yes') {
      setShowRejectForm(false);
      setComments('');
    }
    if (choice === 'no' && !showRejectForm) {
      setShowRejectForm(true);
      return;
    }
    setBusy(true);
    setError(null);
    try {
      const res = await api.submitHumanValidation({
        validation_result: choice === 'yes' ? 'Yes' : 'No',
        comments: choice === 'no' ? comments.trim() || undefined : undefined,
      });
      onDone(messageId, choice, res, choice === 'no' ? comments.trim() : undefined);
      setShowRejectForm(false);
      setComments('');
    } catch (e) {
      console.error(e);
      setError('Could not submit validation. Please try again.');
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="mt-4 pt-4 border-t border-slate-200 space-y-3">
      <p className="text-sm font-medium text-slate-700">Please confirm this analysis</p>
      <div className="flex flex-wrap gap-3">
        <button
          type="button"
          disabled={busy}
          onClick={() => submit('yes')}
          className="px-5 py-2.5 rounded-xl bg-emerald-600 text-white text-sm font-semibold shadow hover:bg-emerald-700 disabled:opacity-50 transition-colors"
        >
          Yes — confirm
        </button>
        <button
          type="button"
          disabled={busy}
          onClick={() => submit('no')}
          className="px-5 py-2.5 rounded-xl bg-white border-2 border-slate-300 text-slate-800 text-sm font-semibold hover:border-rose-400 hover:bg-rose-50 disabled:opacity-50 transition-colors"
        >
          {showRejectForm ? 'Submit No' : 'No — needs review'}
        </button>
      </div>
      {showRejectForm && (
        <div className="space-y-2">
          <label htmlFor={`hitl-comments-${messageId}`} className="text-xs font-medium text-slate-600 block">
            Optional comments for the care team
          </label>
          <textarea
            id={`hitl-comments-${messageId}`}
            value={comments}
            onChange={(e) => setComments(e.target.value)}
            rows={3}
            disabled={busy}
            className="w-full px-3 py-2 rounded-lg border border-slate-300 text-sm text-slate-800 focus:border-blue-500 focus:ring-1 focus:ring-blue-200 outline-none"
            placeholder="What should be reviewed or corrected?"
          />
        </div>
      )}
      {error && <p className="text-sm text-red-600">{error}</p>}
    </div>
  );
}

const Dashboard = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [selectedImage, setSelectedImage] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const handleHumanValidationDone = useCallback(
    (
      messageId: string,
      choice: 'yes' | 'no',
      res: HumanValidationResponse,
      comments?: string
    ) => {
      setMessages((prev) => {
        const idx = prev.findIndex((m) => m.id === messageId);
        if (idx < 0) return prev;
        const old = prev[idx];
        const stripped = stripHumanValidationSection(old.content);
        const updatedOld: Message = {
          ...old,
          content: stripped,
          metadata: { ...old.metadata, humanValidationHandled: true },
        };
        const userLine: Message = {
          id: `${Date.now()}-v-user`,
          role: 'user',
          content:
            choice === 'yes'
              ? 'Yes — I confirm the analysis.'
              : `No — needs review.${comments ? ` Comments: ${comments}` : ''}`,
          timestamp: new Date(),
        };
        const assistantLine: Message = {
          id: `${Date.now()}-v-asst`,
          role: 'assistant',
          content: formatValidationFollowUp(res),
          timestamp: new Date(),
        };
        return [...prev.slice(0, idx), updatedOld, userLine, assistantLine, ...prev.slice(idx + 1)];
      });
      setTimeout(() => messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' }), 100);
    },
    []
  );

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

    const caption = inputMessage.trim();
    const imageFile = selectedImage;
    const previewDataUrl = imagePreview;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: caption || (imageFile ? 'Medical image attached for analysis.' : ''),
      timestamp: new Date(),
      attachedImageDataUrl: imageFile && previewDataUrl ? previewDataUrl : undefined,
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setSelectedImage(null);
    setImagePreview(null);
    setIsLoading(true);

    try {
      let response: ChatResponse;

      if (imageFile) {
        // Backend accepts multipart field `image` + optional form `text`; analysis runs in one step.
        const uploadResponse = await api.uploadImage(imageFile, caption);
        response = {
          response: uploadResponse.response,
          agent_name: uploadResponse.agent,
          agent: uploadResponse.agent,
          result_image: uploadResponse.result_image ?? undefined,
        };
      } else {
        response = await api.chat({
          query: caption,
          conversation_history: messages.map(m => ({ role: m.role, content: m.content })),
        });
      }

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response.response,
        timestamp: new Date(),
        agent: response.agent_name ?? response.agent,
        confidence: response.confidence,
        metadata: response.result_image ? { result_image: response.result_image } : undefined,
      };

      setMessages(prev => [...prev, assistantMessage]);
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
        <div className="px-8 py-6 border-b border-slate-200/50 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h3 className="text-2xl font-bold font-display gradient-text mb-2">
              AI Medical Consultation
            </h3>
            <p className="text-sm text-slate-600">
              Ask anything about medical conditions, symptoms, research, or upload medical images for analysis
            </p>
          </div>
          <Link
            to="/voice-agent"
            className="inline-flex items-center justify-center gap-2 shrink-0 px-5 py-3 rounded-xl bg-gradient-to-r from-violet-600 to-blue-600 text-white text-sm font-semibold shadow-md hover:shadow-lg hover:from-violet-500 hover:to-blue-500 transition-all"
          >
            <Mic className="w-5 h-5" />
            Talk to agent
          </Link>
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
                    {message.agent && message.agent !== 'BRAIN_TUMOR_AGENT' && (
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
                    {message.role === 'user' ? (
                      <div className="space-y-3">
                        {message.attachedImageDataUrl && (
                          <img
                            src={message.attachedImageDataUrl}
                            alt="Attached medical image"
                            className="max-h-56 max-w-full rounded-xl border border-white/40 object-contain bg-white/10"
                          />
                        )}
                        <p className="text-white whitespace-pre-wrap">{message.content}</p>
                      </div>
                    ) : (
                      <>
                        {(() => {
                          const { analysisMarkdown, showHitlControls } = splitHumanValidationContent(
                            message.content
                          );
                          const handled = Boolean(message.metadata?.humanValidationHandled);
                          const showPanel = showHitlControls && !handled;
                          return (
                            <>
                              <AssistantMessageBody
                                content={showPanel ? analysisMarkdown : message.content}
                              />
                              {showPanel && (
                                <HumanValidationPanel
                                  messageId={message.id}
                                  onDone={handleHumanValidationDone}
                                />
                              )}
                            </>
                          );
                        })()}
                      </>
                    )}
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
          <div className="flex items-center gap-3">
            {imagePreview && (
              <div className="relative shrink-0 self-center">
                <img
                  src={imagePreview}
                  alt="Pending attachment"
                  className="h-14 w-14 object-cover rounded-lg border-2 border-blue-400 shadow-sm"
                />
                <button
                  type="button"
                  onClick={() => {
                    setSelectedImage(null);
                    setImagePreview(null);
                    if (fileInputRef.current) fileInputRef.current.value = '';
                  }}
                  className="absolute -top-1.5 -right-1.5 w-5 h-5 bg-red-500 text-white rounded-full flex items-center justify-center hover:bg-red-600 transition-colors shadow"
                  aria-label="Remove image"
                >
                  <X className="w-3 h-3" />
                </button>
              </div>
            )}
          <div className="flex flex-1 items-center space-x-4 min-w-0">
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
              className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed shrink-0"
            >
              <Send className="w-5 h-5" />
            </button>
          </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
