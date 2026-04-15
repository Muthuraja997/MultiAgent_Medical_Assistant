export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  agent?: string;
  confidence?: number;
  metadata?: any;
  image_path?: string;
  /** Data URL of image the user sent (shown in the user bubble). */
  attachedImageDataUrl?: string;
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
