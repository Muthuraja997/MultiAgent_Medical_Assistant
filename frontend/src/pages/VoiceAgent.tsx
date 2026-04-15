import { useCallback, useState } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import { LiveKitRoom, RoomAudioRenderer, ControlBar, useRoomContext } from '@livekit/components-react';
import '@livekit/components-styles';
import { Mic, ArrowLeft, Loader2 } from 'lucide-react';
import { api } from '../services/api';
import { VoiceOrbAnimation } from '../components/voice/VoiceOrbAnimation';
import { useVoiceSpeakingState } from '../components/voice/useVoiceSpeakingState';

function VoiceRoomContent({ roomName }: { roomName: string | null }) {
  const room = useRoomContext();
  const { userSpeaking, agentSpeaking } = useVoiceSpeakingState(room);

  return (
    <div className="p-4 space-y-6 text-white">
      {roomName && (
        <p className="text-sm text-slate-300">
          Room: <span className="font-mono text-slate-100">{roomName}</span>
        </p>
      )}
      <VoiceOrbAnimation userSpeaking={userSpeaking} agentSpeaking={agentSpeaking} />
      <RoomAudioRenderer />
      <div className="flex justify-center pt-2">
        <ControlBar controls={{ microphone: true, camera: false, screenShare: false }} />
      </div>
    </div>
  );
}

const VoiceAgent = () => {
  const [url, setUrl] = useState<string | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [roomName, setRoomName] = useState<string | null>(null);
  const [connect, setConnect] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const startSession = useCallback(async () => {
    setError(null);
    setLoading(true);
    try {
      const data = await api.getLiveKitVoiceToken();
      setUrl(data.url);
      setToken(data.token);
      setRoomName(data.room_name);
      setConnect(true);
    } catch (e: unknown) {
      let msg = 'Failed to start voice session';
      if (axios.isAxiosError(e)) {
        const d = e.response?.data?.detail;
        if (typeof d === 'string') msg = d;
        else if (Array.isArray(d)) msg = d.map((x: { msg?: string }) => x.msg).filter(Boolean).join(', ') || msg;
        else if (e.message) msg = e.message;
      } else if (e instanceof Error) {
        msg = e.message;
      }
      setError(msg);
      setConnect(false);
      setUrl(null);
      setToken(null);
      setRoomName(null);
    } finally {
      setLoading(false);
    }
  }, []);

  const handleDisconnected = useCallback(() => {
    setConnect(false);
    setToken(null);
    setUrl(null);
    setRoomName(null);
  }, []);

  return (
    <div className="space-y-6 max-w-3xl mx-auto">
      <div className="flex items-center gap-4">
        <Link
          to="/dashboard"
          className="inline-flex items-center gap-2 text-slate-600 hover:text-blue-600 transition-colors"
        >
          <ArrowLeft className="w-5 h-5" />
          Back to dashboard
        </Link>
      </div>

      <div className="glass-morphism rounded-2xl p-8">
        <h2 className="text-3xl font-bold font-display gradient-text mb-2">Voice medical assistant</h2>
        <p className="text-slate-600 mb-6">
          Speak with the voice agent about wellness, mental health, and general medical education. Uses Deepgram for
          speech-to-text and text-to-speech and a Hugging Face Llama model for answers. This does not replace professional care.
        </p>

        {!connect || !url || !token ? (
          <div className="space-y-4">
            <button
              type="button"
              onClick={startSession}
              disabled={loading}
              className="inline-flex items-center justify-center gap-2 px-8 py-4 rounded-xl bg-gradient-to-r from-violet-600 to-blue-600 text-white font-semibold shadow-lg hover:shadow-xl hover:from-violet-500 hover:to-blue-500 transition-all disabled:opacity-60 disabled:cursor-not-allowed"
            >
              {loading ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  Connecting…
                </>
              ) : (
                <>
                  <Mic className="w-5 h-5" />
                  Talk to agent
                </>
              )}
            </button>
            {error && (
              <p className="text-sm text-red-600 bg-red-50 border border-red-200 rounded-xl px-4 py-3">{error}</p>
            )}
            <p className="text-xs text-slate-500">
              Ensure the backend has <code className="text-slate-700">LIVEKIT_URL</code>,{' '}
              <code className="text-slate-700">LIVEKIT_API_KEY</code>, and{' '}
              <code className="text-slate-700">LIVEKIT_API_SECRET</code> set, and run the voice worker:{' '}
              <code className="text-slate-700">python -m voice_agent.worker dev</code> from the backend folder.
            </p>
          </div>
        ) : (
          <div data-lk-theme="default" className="rounded-xl border border-slate-200 overflow-hidden bg-slate-900">
            <LiveKitRoom
              serverUrl={url}
              token={token}
              connect={connect}
              audio
              video={false}
              onDisconnected={handleDisconnected}
            >
              <VoiceRoomContent roomName={roomName} />
            </LiveKitRoom>
          </div>
        )}
      </div>
    </div>
  );
};

export default VoiceAgent;
