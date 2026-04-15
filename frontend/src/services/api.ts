import axios from 'axios';

// Use relative URL for API calls - will use Vite proxy in development
// For production, set VITE_API_URL environment variable
const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true,
});

export interface QueryRequest {
  query: string;
  conversation_history?: Array<{role: string; content: string}>;
}

export interface ChatResponse {
  status?: string;
  response: string;
  /** Backend field name for the handling agent */
  agent?: string;
  agent_name?: string;
  result_image?: string | null;
  confidence?: number;
  metadata?: any;
}

/** Matches backend `UploadResponse` — upload runs full image analysis in one request. */
export interface UploadResponse {
  status: string;
  response: string;
  agent: string;
  result_image?: string | null;
}

/** POST `/api/validate` — human-in-the-loop confirmation for imaging agents */
export interface HumanValidationRequest {
  validation_result: string;
  comments?: string | null;
}

export interface HumanValidationResponse {
  status: string;
  message: string;
  response: string;
  comments?: string | null;
}

/** User ↔ doctor (or any two accounts) direct chat */
export interface DirectMessageItem {
  message_id: string;
  sender_id: string;
  receiver_id: string;
  message: string;
  created_at: string;
}

export interface DirectMessageListResponse {
  messages: DirectMessageItem[];
}

function authUserIdHeaders(): Record<string, string> {
  const uid = localStorage.getItem('user_id');
  return uid ? { 'x-user-id': uid } : {};
}

export const api = {
  // Health check
  healthCheck: async () => {
    const response = await apiClient.get('/health');
    return response.data;
  },

  // Chat endpoint
  chat: async (data: QueryRequest): Promise<ChatResponse> => {
    const response = await apiClient.post('/chat', data);
    const d = response.data as ChatResponse;
    return { ...d, agent_name: d.agent_name ?? d.agent };
  },

  /**
   * Upload medical image — backend expects form field `image` (not `file`) and optional `text`.
   * Processing completes in this call (no separate filepath step).
   */
  uploadImage: async (file: File, text?: string): Promise<UploadResponse> => {
    const formData = new FormData();
    formData.append('image', file);
    if (text != null && text !== '') {
      formData.append('text', text);
    }

    const response = await apiClient.post('/upload', formData, {
      transformRequest: [
        (data, headers) => {
          delete headers['Content-Type'];
          return data as FormData;
        },
      ],
    });
    return response.data;
  },

  /** Legacy: `/api/chat` does not accept `image_path`; use `uploadImage` instead. */
  analyzeImage: async (imagePath: string, query: string): Promise<ChatResponse> => {
    const response = await apiClient.post('/chat', {
      query,
      image_path: imagePath,
    });
    const d = response.data as ChatResponse;
    return { ...d, agent_name: d.agent_name ?? d.agent };
  },

  /** Human validation for medical CV output (Yes/No + optional comments for No). */
  submitHumanValidation: async (
    data: HumanValidationRequest
  ): Promise<HumanValidationResponse> => {
    const response = await apiClient.post('/validate', {
      validation_result: data.validation_result,
      comments: data.comments ?? undefined,
    });
    return response.data;
  },

  // Speech to text
  transcribeAudio: async (file: File) => {
    const formData = new FormData();
    formData.append('audio_file', file);

    const response = await apiClient.post('/transcribe', formData, {
      transformRequest: [
        (data, headers) => {
          delete headers['Content-Type'];
          return data as FormData;
        },
      ],
    });
    return response.data;
  },

  // Text to speech
  generateSpeech: async (text: string, voice?: string) => {
    const response = await apiClient.post('/generate-speech', {
      text,
      voice: voice || 'Rachel',
    }, {
      responseType: 'blob',
    });
    return response.data;
  },

  // Find nearby hospitals
  findNearbyHospitals: async (lat: number, lon: number, radius: number = 5000) => {
    const response = await apiClient.get('/hospitals/nearby', {
      params: { lat, lon, radius },
    });
    return response.data;
  },

  getDoctor: async (doctorId: string) => {
    const response = await apiClient.get(`/doctors/${encodeURIComponent(doctorId)}`);
    return response.data;
  },

  /** Sets doctor available_status in MongoDB */
  updateDoctorAvailability: async (doctorId: string, available: boolean) => {
    const response = await apiClient.patch(`/doctors/${encodeURIComponent(doctorId)}/availability`, null, {
      params: { available },
    });
    return response.data;
  },

  /** Remove ACCEPTED appointment + meeting after consultation (user or doctor). */
  completeAppointmentConsultation: async (requestId: string, actorId: string) => {
    const response = await apiClient.delete(`/appointment-requests/${encodeURIComponent(requestId)}`, {
      params: { actor_id: actorId },
    });
    return response.data;
  },

  /** List messages between logged-in user_id and peer_id (both are user_id or doctor_id strings). */
  listDirectMessages: async (
    userId: string,
    peerId: string,
    limit = 200
  ): Promise<DirectMessageListResponse> => {
    const response = await apiClient.get('/messages', {
      params: { user_id: userId, peer_id: peerId, limit },
      headers: authUserIdHeaders(),
    });
    return response.data;
  },

  /** Send a direct message (sender_id must match logged-in user when x-user-id is used). */
  sendDirectMessage: async (
    sender_id: string,
    receiver_id: string,
    message: string
  ): Promise<DirectMessageItem> => {
    const response = await apiClient.post(
      '/messages',
      { sender_id, receiver_id, message },
      { headers: authUserIdHeaders() }
    );
    return response.data;
  },

  /** LiveKit JWT for the medical voice agent (Deepgram STT/TTS + Hugging Face LLM). */
  getLiveKitVoiceToken: async (roomName?: string | null) => {
    const uid = localStorage.getItem('user_id');
    const response = await apiClient.post(
      '/voice/livekit-token',
      { room_name: roomName ?? null },
      {
        headers: uid ? { 'x-user-id': uid } : {},
      }
    );
    return response.data as {
      url: string;
      token: string;
      room_name: string;
      agent_name: string;
    };
  },
};

export default apiClient;
