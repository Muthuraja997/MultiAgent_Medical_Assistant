import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

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
  response: string;
  agent_name?: string;
  confidence?: number;
  metadata?: any;
}

export interface UploadResponse {
  filename: string;
  filepath: string;
  message: string;
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
    return response.data;
  },

  // Image upload
  uploadImage: async (file: File): Promise<UploadResponse> => {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await apiClient.post('/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  // Image analysis with query
  analyzeImage: async (imagePath: string, query: string): Promise<ChatResponse> => {
    const response = await apiClient.post('/chat', {
      query,
      image_path: imagePath,
    });
    return response.data;
  },

  // Validate query
  validateQuery: async (query: string) => {
    const response = await apiClient.post('/validate', { query });
    return response.data;
  },

  // Speech to text
  transcribeAudio: async (file: File) => {
    const formData = new FormData();
    formData.append('audio_file', file);
    
    const response = await apiClient.post('/transcribe', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
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
};

export default apiClient;
