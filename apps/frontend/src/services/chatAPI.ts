interface ChatSession {
  session_id: string;
  created_at: string;
}

interface ChatMessage {
  message: string;
  session_id: string;
}

interface ChatAction {
  type: 'create_region' | 'create_path' | 'stage_description' | 'stage_hints' | 'select_item' | 'center_view';
  params: Record<string, unknown>;
  ui_hints?: {
    select?: boolean;
    center_map?: boolean;
    highlight?: boolean;
  };
}

interface ChatResponse {
  response: string;
  actions: ChatAction[];
  session_id: string;
}

class ChatAPIClient {
  private baseUrl: string;

  constructor() {
    // Use environment variable or fallback to production URL  
    // TODO: Configure reverse proxy for chat service
    this.baseUrl = import.meta.env.VITE_CHAT_API_URL || 'https://wildedit.luminarimud.com/chat';
  }

  async createSession(): Promise<ChatSession> {
    const response = await fetch(`${this.baseUrl}/api/session/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({})
    });

    if (!response.ok) {
      throw new Error(`Failed to create chat session: ${response.status}`);
    }

    return response.json();
  }

  async sendMessage(message: string, sessionId: string): Promise<ChatResponse> {
    const response = await fetch(`${this.baseUrl}/api/chat/message`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message,
        session_id: sessionId
      })
    });

    if (!response.ok) {
      throw new Error(`Failed to send message: ${response.status}`);
    }

    return response.json();
  }

  async getHistory(sessionId: string): Promise<Record<string, unknown>> {
    const response = await fetch(`${this.baseUrl}/api/chat/history?session_id=${sessionId}`);

    if (!response.ok) {
      throw new Error(`Failed to get chat history: ${response.status}`);
    }

    return response.json();
  }

  async healthCheck(): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseUrl}/health/`, {
        method: 'GET'
      });
      return response.ok;
    } catch (error) {
      console.error('Chat service health check failed:', error);
      return false;
    }
  }
}

export const chatAPI = new ChatAPIClient();
export type { ChatSession, ChatMessage, ChatResponse, ChatAction };