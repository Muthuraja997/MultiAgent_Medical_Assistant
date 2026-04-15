import { useCallback, useEffect, useRef, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { MessageCircle, Send, Loader2, RefreshCw, User } from 'lucide-react';
import { api, type DirectMessageItem } from '../services/api';

export default function Messages() {
  const [searchParams, setSearchParams] = useSearchParams();
  const me = localStorage.getItem('user_id') || '';
  const myType = localStorage.getItem('user_type') || '';

  const [peerId, setPeerId] = useState(() => (searchParams.get('peer') || '').trim());
  const [draftPeer, setDraftPeer] = useState(() => (searchParams.get('peer') || '').trim());
  const [messages, setMessages] = useState<DirectMessageItem[]>([]);
  const [text, setText] = useState('');
  const [loading, setLoading] = useState(false);
  const [sending, setSending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [doctors, setDoctors] = useState<{ doctor_id: string; doc_name?: string }[]>([]);
  /** Patients (USER accounts) for doctors to pick when starting a chat */
  const [patientUsers, setPatientUsers] = useState<{ user_id: string; user_name?: string }[]>([]);
  const bottomRef = useRef<HTMLDivElement>(null);

  const peerDisplayLabel = (id: string) => {
    const doc = doctors.find((d) => d.doctor_id === id);
    if (doc?.doc_name) return doc.doc_name;
    const u = patientUsers.find((p) => p.user_id === id);
    if (u?.user_name) return u.user_name;
    return '';
  };

  const scrollToBottom = () => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const loadThread = useCallback(async () => {
    if (!me || !peerId.trim()) {
      setMessages([]);
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const data = await api.listDirectMessages(me, peerId.trim(), 200);
      setMessages(data.messages || []);
      setTimeout(scrollToBottom, 100);
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : 'Failed to load messages';
      setError(typeof e === 'object' && e && 'response' in e ? String((e as { response?: { data?: { detail?: string } } }).response?.data?.detail) : msg);
      setMessages([]);
    } finally {
      setLoading(false);
    }
  }, [me, peerId]);

  useEffect(() => {
    void loadThread();
  }, [loadThread]);

  useEffect(() => {
    if (!peerId.trim()) return;
    const t = window.setInterval(() => void loadThread(), 5000);
    return () => window.clearInterval(t);
  }, [peerId, loadThread]);

  useEffect(() => {
    if (myType !== 'USER') return;
    let cancelled = false;
    (async () => {
      try {
        const r = await fetch('/api/doctors');
        if (!r.ok) return;
        const data = await r.json();
        if (!cancelled && Array.isArray(data)) {
          setDoctors(
            data.map((d: { doctor_id?: string; doc_name?: string }) => ({
              doctor_id: d.doctor_id || '',
              doc_name: d.doc_name,
            }))
          );
        }
      } catch {
        /* ignore */
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [myType]);

  useEffect(() => {
    if (myType !== 'DOCTOR') return;
    let cancelled = false;
    (async () => {
      try {
        const r = await fetch('/api/users');
        if (!r.ok) return;
        const data = await r.json();
        if (!cancelled && Array.isArray(data)) {
          const rows = data
            .map((u: { user_id?: string; user_name?: string }) => ({
              user_id: u.user_id || '',
              user_name: u.user_name,
            }))
            .filter((u: { user_id: string }) => u.user_id);
          rows.sort((a: { user_name?: string; user_id: string }, b: { user_name?: string; user_id: string }) =>
            (a.user_name || a.user_id).localeCompare(b.user_name || b.user_id, undefined, { sensitivity: 'base' })
          );
          setPatientUsers(rows);
        }
      } catch {
        /* ignore */
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [myType]);

  const openChat = () => {
    const p = draftPeer.trim();
    setPeerId(p);
    if (p) {
      setSearchParams({ peer: p });
    } else {
      setSearchParams({});
    }
  };

  const handleSend = async () => {
    const body = text.trim();
    if (!me || !peerId.trim() || !body) return;
    setSending(true);
    setError(null);
    try {
      await api.sendDirectMessage(me, peerId.trim(), body);
      setText('');
      await loadThread();
    } catch (e: unknown) {
      const ax = e as { response?: { data?: { detail?: string } } };
      setError(ax.response?.data?.detail || 'Failed to send message');
    } finally {
      setSending(false);
    }
  };

  if (!me) {
    return (
      <div className="glass-morphism rounded-2xl p-8 text-center text-slate-600">
        Please log in to use direct messages.
      </div>
    );
  }

  const headerPeerName = peerId.trim() ? peerDisplayLabel(peerId) : '';

  return (
    <div className="h-full flex flex-col max-w-4xl mx-auto">
      <div className="glass-morphism rounded-2xl p-6 mb-4 flex flex-col sm:flex-row sm:items-end gap-4">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
            <MessageCircle className="w-6 h-6 text-white" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-slate-800">Messages</h2>
            <p className="text-sm text-slate-500 flex items-center gap-1">
              <User className="w-3.5 h-3.5" />
              You: <span className="font-mono text-slate-700">{me}</span>
              <span className="text-slate-400">({myType || '?'})</span>
            </p>
          </div>
        </div>
        <div className="flex flex-1 flex-col sm:flex-row gap-2 sm:items-end min-w-0">
          {myType === 'USER' && doctors.length > 0 && (
            <select
              className="px-3 py-2 rounded-lg border border-slate-200 text-sm bg-white text-slate-800 max-w-xs"
              value=""
              onChange={(e) => {
                const v = e.target.value;
                if (v) {
                  setDraftPeer(v);
                  e.currentTarget.value = '';
                }
              }}
            >
              <option value="">Pick a doctor…</option>
              {doctors
                .filter((d) => d.doctor_id)
                .map((d) => (
                  <option key={d.doctor_id} value={d.doctor_id}>
                    {d.doc_name || d.doctor_id} ({d.doctor_id})
                  </option>
                ))}
            </select>
          )}
          {myType === 'DOCTOR' && patientUsers.length > 0 && (
            <select
              className="px-3 py-2 rounded-lg border border-slate-200 text-sm bg-white text-slate-800 max-w-xs"
              value=""
              onChange={(e) => {
                const v = e.target.value;
                if (v) {
                  setDraftPeer(v);
                  e.currentTarget.value = '';
                }
              }}
            >
              <option value="">Pick a patient…</option>
              {patientUsers.map((u) => (
                <option key={u.user_id} value={u.user_id}>
                  {u.user_name || u.user_id} ({u.user_id})
                </option>
              ))}
            </select>
          )}
          <input
            type="text"
            placeholder={
              myType === 'DOCTOR'
                ? 'Patient user_id (or pick from list)'
                : 'Other party user_id or doctor_id'
            }
            value={draftPeer}
            onChange={(e) => setDraftPeer(e.target.value)}
            className="flex-1 min-w-0 px-4 py-2 rounded-lg border border-slate-200 text-sm"
          />
          <button
            type="button"
            onClick={openChat}
            className="px-4 py-2 rounded-lg bg-blue-600 text-white text-sm font-semibold hover:bg-blue-700 shrink-0"
          >
            Open chat
          </button>
          <button
            type="button"
            onClick={() => void loadThread()}
            className="p-2 rounded-lg border border-slate-200 hover:bg-slate-50 shrink-0"
            title="Refresh"
          >
            <RefreshCw className={`w-5 h-5 text-slate-600 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {error && (
        <div className="mb-3 px-4 py-2 rounded-lg bg-red-50 text-red-700 text-sm border border-red-100">{error}</div>
      )}

      <div className="flex-1 glass-morphism rounded-2xl flex flex-col overflow-hidden min-h-[420px]">
        {!peerId.trim() ? (
          <div className="flex-1 flex items-center justify-center text-slate-500 text-sm p-8 text-center">
            Enter a doctor or patient login id and click <strong className="text-slate-700">Open chat</strong>.
          </div>
        ) : (
          <>
            <div className="px-4 py-2 border-b border-slate-200/80 bg-slate-50/80 text-xs text-slate-600">
              Thread with{' '}
              {headerPeerName ? (
                <>
                  <span className="font-semibold text-slate-800">{headerPeerName}</span>
                  <span className="text-slate-500"> · </span>
                  <span className="font-mono font-semibold text-slate-800">{peerId}</span>
                </>
              ) : (
                <span className="font-mono font-semibold text-slate-800">{peerId}</span>
              )}
            </div>
            <div className="flex-1 overflow-y-auto p-4 space-y-3">
              {loading && messages.length === 0 ? (
                <div className="flex justify-center py-12 text-slate-500">
                  <Loader2 className="w-8 h-8 animate-spin" />
                </div>
              ) : (
                messages.map((m) => {
                  const mine = m.sender_id === me;
                  return (
                    <div key={m.message_id} className={`flex ${mine ? 'justify-end' : 'justify-start'}`}>
                      <div
                        className={`max-w-[85%] rounded-2xl px-4 py-2 text-sm ${
                          mine
                            ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white'
                            : 'bg-white border border-slate-200 text-slate-800'
                        }`}
                      >
                        <p className="whitespace-pre-wrap break-words">{m.message}</p>
                        <p className={`text-[10px] mt-1 ${mine ? 'text-blue-100' : 'text-slate-400'}`}>
                          {m.sender_id} → {m.receiver_id} ·{' '}
                          {new Date(m.created_at).toLocaleString()}
                        </p>
                      </div>
                    </div>
                  );
                })
              )}
              <div ref={bottomRef} />
            </div>
            <div className="p-3 border-t border-slate-200/80 bg-slate-50/80 flex gap-2">
              <input
                type="text"
                value={text}
                onChange={(e) => setText(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    void handleSend();
                  }
                }}
                placeholder="Type a message…"
                disabled={sending}
                className="flex-1 px-4 py-3 rounded-xl border border-slate-200 text-sm outline-none focus:border-blue-400"
              />
              <button
                type="button"
                onClick={() => void handleSend()}
                disabled={sending || !text.trim()}
                className="px-4 py-3 rounded-xl bg-blue-600 text-white disabled:opacity-50 flex items-center gap-2"
              >
                {sending ? <Loader2 className="w-5 h-5 animate-spin" /> : <Send className="w-5 h-5" />}
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
