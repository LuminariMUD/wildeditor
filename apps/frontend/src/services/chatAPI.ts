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

interface ToolCall {
  tool_name: string;
  args: Record<string, unknown>;
}

interface ChatResponse {
  response: string | {
    message: string;
    actions: ChatAction[];
    tool_calls: ToolCall[];
    suggestions: string[];
    warnings: string[];
  };
  actions?: ChatAction[]; // Legacy format
  session_id: string;
  message_id: string;
  timestamp: string;
}

interface StreamChunk {
  type: 'status' | 'chunk' | 'actions' | 'complete' | 'error';
  content?: string;
  message?: string;
  actions?: ChatAction[];
  error?: string;
}

class ChatAPIClient {
  private baseUrl: string;

  constructor() {
    // Use HTTPS URL with Apache reverse proxy
    this.baseUrl = import.meta.env.VITE_CHAT_API_URL || 'https://luminarimud.com/chat';
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

  async *sendMessageStream(
    message: string, 
    sessionId: string,
    onChunk?: (chunk: StreamChunk) => void
  ): AsyncGenerator<StreamChunk, void, unknown> {
    const response = await fetch(`${this.baseUrl}/api/chat/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'text/event-stream',
      },
      body: JSON.stringify({
        message,
        session_id: sessionId
      })
    });

    if (!response.ok) {
      throw new Error(`Failed to start streaming: ${response.status}`);
    }

    if (!response.body) {
      throw new Error('Response body is null');
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    try {
      while (true) {
        const { done, value } = await reader.read();
        
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || ''; // Keep incomplete line in buffer

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = line.slice(6); // Remove 'data: ' prefix
              if (data.trim()) {
                const chunk: StreamChunk = JSON.parse(data);
                
                // Call optional callback
                if (onChunk) {
                  onChunk(chunk);
                }
                
                yield chunk;
                
                // Break on completion or error
                if (chunk.type === 'complete' || chunk.type === 'error') {
                  return;
                }
              }
            } catch (parseError) {
              console.warn('Failed to parse SSE data:', line, parseError);
            }
          }
        }
      }
    } finally {
      reader.releaseLock();
    }
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
      if (error instanceof TypeError && error.message.includes('fetch')) {
        console.error('Chat service blocked by mixed content policy (HTTPS→HTTP). Configure reverse proxy or use HTTP development server.');
      } else {
        console.error('Chat service health check failed:', error);
      }
      return false;
    }
  }
}

export const chatAPI = new ChatAPIClient();
export type { ChatSession, ChatMessage, ChatResponse, ChatAction, StreamChunk };