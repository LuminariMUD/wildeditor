import React, { useState, useRef, useEffect, useCallback } from 'react';
import { MessageCircle, X, Send, Loader2, Bot, User } from 'lucide-react';
import { chatAPI, ChatAction } from '../services/chatAPI';

interface ChatMessage {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  actions?: ChatAction[];
}

interface ChatAssistantProps {
  onExecuteAction?: (action: ChatAction) => void;
}

export const ChatAssistant: React.FC<ChatAssistantProps> = ({
  onExecuteAction
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const addMessage = (message: ChatMessage) => {
    // Validate message structure before adding
    const validatedMessage: ChatMessage = {
      id: message.id || `msg-${Date.now()}`,
      type: message.type || 'assistant',
      content: typeof message.content === 'string' ? message.content : 'Invalid message',
      timestamp: message.timestamp instanceof Date ? message.timestamp : new Date(),
      actions: Array.isArray(message.actions) ? message.actions : []
    };
    
    setMessages(prev => {
      if (!Array.isArray(prev)) {
        console.warn('[ChatAssistant] Previous messages is not an array:', prev);
        return [validatedMessage];
      }
      return [...prev, validatedMessage];
    });
  };

  const initializeSession = useCallback(async () => {
    try {
      const session = await chatAPI.createSession();
      setSessionId(session.session_id);
      
      // Add welcome message
      addMessage({
        id: 'welcome',
        type: 'assistant',
        content: "Hi! I'm your wilderness building assistant. I can help you create regions, paths, generate descriptions, and more. What would you like to build?",
        timestamp: new Date()
      });
    } catch (error) {
      console.error('Failed to initialize chat session:', error);
      addMessage({
        id: 'error',
        type: 'assistant', 
        content: "Sorry, I'm having trouble connecting. Please try again later.",
        timestamp: new Date()
      });
    }
  }, []);

  // Initialize session when component opens
  useEffect(() => {
    if (isOpen && !sessionId) {
      initializeSession();
    }
    
    // Focus input when chat opens
    if (isOpen && inputRef.current) {
      const timer = setTimeout(() => {
        inputRef.current?.focus();
      }, 100);
      return () => clearTimeout(timer);
    }
  }, [isOpen, sessionId, initializeSession]);

  // Auto-scroll to bottom when new messages arrive  
  useEffect(() => {
    try {
      if (messagesEndRef.current) {
        messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
      }
    } catch (scrollError) {
      console.warn('[ChatAssistant] Scroll error:', scrollError);
      // Fallback: try without smooth behavior
      try {
        messagesEndRef.current?.scrollIntoView();
      } catch (fallbackError) {
        console.warn('[ChatAssistant] Fallback scroll also failed:', fallbackError);
      }
    }
  }, [messages]);

  // Restore input focus after loading completes
  useEffect(() => {
    if (!isLoading && isOpen && inputRef.current) {
      // Small delay to ensure DOM updates are complete
      const timer = setTimeout(() => {
        inputRef.current?.focus();
      }, 100);
      return () => clearTimeout(timer);
    }
  }, [isLoading, isOpen]);

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isLoading || !sessionId) return;

    const userMessage: ChatMessage = {
      id: `user-${Date.now()}`,
      type: 'user',
      content: inputValue,
      timestamp: new Date()
    };

    addMessage(userMessage);
    setInputValue('');
    setIsLoading(true);

    try {
      const data = await chatAPI.sendMessage(inputValue, sessionId);
      
      // Validate API response structure
      if (!data || typeof data !== 'object') {
        throw new Error('Invalid API response format');
      }
      
      // Handle nested response structure from chat agent
      let responseContent: string;
      let responseActions: ChatAction[];
      
      if (data.response && typeof data.response === 'object') {
        // New nested structure: data.response.message
        responseContent = typeof data.response.message === 'string' 
          ? data.response.message 
          : "I received your message but couldn't process it properly.";
        responseActions = Array.isArray(data.response.actions) 
          ? data.response.actions.filter(action => action && typeof action.type === 'string')
          : [];
      } else {
        // Legacy flat structure: data.response  
        responseContent = typeof data.response === 'string' 
          ? data.response 
          : "I received your message but couldn't process it properly.";
        responseActions = Array.isArray(data.actions) 
          ? data.actions.filter(action => action && typeof action.type === 'string')
          : [];
      }
      
      const assistantMessage: ChatMessage = {
        id: `assistant-${Date.now()}`,
        type: 'assistant',
        content: responseContent,
        timestamp: new Date(),
        actions: responseActions
      };

      addMessage(assistantMessage);

      // Execute any actions returned by the assistant
      if (data.actions && data.actions.length > 0 && onExecuteAction) {
        console.log('[ChatAssistant] Executing actions:', data.actions);
        for (const action of data.actions) {
          try {
            await onExecuteAction(action);
          } catch (actionError) {
            console.error('[ChatAssistant] Action execution failed:', actionError);
            // Show error message to user
            addMessage({
              id: `action-error-${Date.now()}`,
              type: 'assistant',
              content: `Sorry, I couldn't complete the action "${action.type}". Error: ${actionError instanceof Error ? actionError.message : 'Unknown error'}`,
              timestamp: new Date()
            });
          }
        }
      }

    } catch (error) {
      console.error('Failed to send message:', error);
      addMessage({
        id: `error-${Date.now()}`,
        type: 'assistant',
        content: "Sorry, I couldn't process your message. Please try again.",
        timestamp: new Date()
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const formatTime = (date: Date) => {
    try {
      if (!(date instanceof Date) || isNaN(date.getTime())) {
        return 'Invalid time';
      }
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    } catch (error) {
      console.warn('[ChatAssistant] Error formatting time:', error);
      return 'Time error';
    }
  };

  if (!isOpen) {
    return (
      <button
        onClick={() => setIsOpen(true)}
        className="fixed bottom-6 right-6 bg-blue-600 hover:bg-blue-700 text-white p-3 rounded-full shadow-lg transition-colors z-50"
        title="Open Chat Assistant"
      >
        <MessageCircle className="w-6 h-6" />
      </button>
    );
  }

  return (
    <div className="fixed bottom-6 right-6 w-96 h-[500px] bg-gray-900 border border-gray-700 rounded-lg shadow-xl flex flex-col z-50">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-700">
        <div className="flex items-center gap-2">
          <Bot className="w-5 h-5 text-blue-400" />
          <h3 className="text-white font-medium">Wilderness Assistant</h3>
        </div>
        <button
          onClick={() => setIsOpen(false)}
          className="text-gray-400 hover:text-white p-1"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.filter(Boolean).map((message) => {
          // Extra validation for each message during render
          if (!message || !message.id) {
            console.warn('[ChatAssistant] Skipping invalid message:', message);
            return null;
          }
          
          return (
          <div
            key={message.id}
            className={`flex gap-3 ${message.type === 'user' ? 'flex-row-reverse' : 'flex-row'}`}
          >
            <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
              message.type === 'user' 
                ? 'bg-blue-600' 
                : 'bg-gray-700'
            }`}>
              {message.type === 'user' ? (
                <User className="w-4 h-4 text-white" />
              ) : (
                <Bot className="w-4 h-4 text-blue-400" />
              )}
            </div>
            <div className={`max-w-[80%] ${message.type === 'user' ? 'text-right' : 'text-left'}`}>
              <div className={`inline-block p-3 rounded-lg ${
                message.type === 'user'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-800 text-gray-100'
              }`}>
                <div className="text-sm whitespace-pre-wrap">
                  {(() => {
                    try {
                      const content = message.content;
                      if (typeof content !== 'string') {
                        console.warn('[ChatAssistant] Non-string message content:', content);
                        return 'Invalid message content';
                      }
                      if (content.length > 10000) {
                        console.warn('[ChatAssistant] Message too long, truncating');
                        return content.substring(0, 10000) + '...';
                      }
                      return content;
                    } catch (renderError) {
                      console.error('[ChatAssistant] Content render error:', renderError);
                      return 'Content render error';
                    }
                  })()}
                </div>
                {message.actions && message.actions.length > 0 && (
                  <div className="mt-2 text-xs text-gray-300">
                    <div className="flex items-center gap-1">
                      <Bot className="w-3 h-3" />
                      <span>Executed {message.actions.length} action{message.actions.length > 1 ? 's' : ''}</span>
                    </div>
                  </div>
                )}
              </div>
              <div className="text-xs text-gray-500 mt-1">
                {formatTime(message.timestamp)}
              </div>
            </div>
          </div>
          );
        }).filter(Boolean)}
        
        {/* Loading indicator */}
        {isLoading && (
          <div className="flex gap-3">
            <div className="w-8 h-8 rounded-full bg-gray-700 flex items-center justify-center flex-shrink-0">
              <Bot className="w-4 h-4 text-blue-400" />
            </div>
            <div className="bg-gray-800 rounded-lg p-3">
              <div className="flex items-center gap-2">
                <Loader2 className="w-4 h-4 animate-spin text-blue-400" />
                <span className="text-sm text-gray-300">Thinking...</span>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="p-4 border-t border-gray-700">
        <div className="flex gap-2">
          <input
            ref={inputRef}
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask me to create regions, paths, descriptions..."
            className="flex-1 bg-gray-800 border border-gray-600 rounded-lg px-3 py-2 text-white text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            disabled={isLoading}
          />
          <button
            onClick={handleSendMessage}
            disabled={!inputValue.trim() || isLoading}
            className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white p-2 rounded-lg transition-colors"
          >
            <Send className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
};