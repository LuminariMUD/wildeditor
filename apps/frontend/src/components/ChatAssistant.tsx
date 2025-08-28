import React, { useState, useRef, useEffect, useCallback } from 'react';
import { MessageCircle, X, Send, Loader2, Bot, User, Move, Maximize2, Minimize2 } from 'lucide-react';
import Draggable, { DraggableData, DraggableEvent } from 'react-draggable';
import { ResizableBox, ResizeCallbackData } from 'react-resizable';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { chatAPI, ChatAction, StreamChunk } from '../services/chatAPI';

// Import ResizableBox CSS
import 'react-resizable/css/styles.css';

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

interface WindowState {
  x: number;
  y: number;
  width: number;
  height: number;
  isMinimized: boolean;
}

interface WindowBounds {
  left: number;
  top: number;
  right: number;
  bottom: number;
}

// Default window settings
const DEFAULT_WINDOW: WindowState = {
  x: window.innerWidth - 440, // Position 20px from right edge
  y: 100,
  width: 420,
  height: 600,
  isMinimized: false
};

// Window constraints
const MIN_WIDTH = 300;
const MIN_HEIGHT = 400;
const MAX_WIDTH = Math.min(800, window.innerWidth * 0.8);
const MAX_HEIGHT = Math.min(800, window.innerHeight * 0.9);

// Helper function to get screen bounds (supports multi-monitor)  
const getScreenBounds = (): WindowBounds => {
  return {
    left: -window.screen.width, // Allow dragging to left monitor
    top: 0,
    right: window.screen.width * 2, // Allow dragging to right monitor  
    bottom: window.screen.height
  };
};

export const ChatAssistant: React.FC<ChatAssistantProps> = ({
  onExecuteAction
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [useStreaming, setUseStreaming] = useState(true); // Enable streaming by default
  const [windowState, setWindowState] = useState<WindowState>(() => {
    // Load saved state from localStorage
    try {
      const saved = localStorage.getItem('chat-assistant-window');
      if (saved) {
        const parsed = JSON.parse(saved);
        // Validate bounds are within visible viewport (not just multi-monitor bounds)
        const viewportBounds = {
          left: 0,
          top: 0,
          right: window.innerWidth,
          bottom: window.innerHeight
        };
        
        // Check if at least part of the window would be visible in the main viewport
        if (parsed.x >= -MIN_WIDTH/2 && parsed.x <= viewportBounds.right - MIN_WIDTH/2 &&
            parsed.y >= 0 && parsed.y <= viewportBounds.bottom - MIN_HEIGHT) {
          return { ...DEFAULT_WINDOW, ...parsed };
        }
      }
    } catch (error) {
      console.warn('Failed to load chat window state:', error);
    }
    return DEFAULT_WINDOW;
  });
  
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const nodeRef = useRef<HTMLDivElement>(null);

  // Save window state to localStorage
  const saveWindowState = useCallback((state: WindowState) => {
    try {
      localStorage.setItem('chat-assistant-window', JSON.stringify(state));
    } catch (error) {
      console.warn('Failed to save chat window state:', error);
    }
  }, []);

  // Handle window drag
  const handleDrag = useCallback((_e: DraggableEvent, data: DraggableData) => {
    const newState = { ...windowState, x: data.x, y: data.y };
    setWindowState(newState);
    saveWindowState(newState);
  }, [windowState, saveWindowState]);

  // Handle window resize
  const handleResize = useCallback((_e: React.SyntheticEvent, data: ResizeCallbackData) => {
    const newState = { 
      ...windowState, 
      width: Math.max(MIN_WIDTH, Math.min(MAX_WIDTH, data.size.width)),
      height: Math.max(MIN_HEIGHT, Math.min(MAX_HEIGHT, data.size.height))
    };
    setWindowState(newState);
    saveWindowState(newState);
  }, [windowState, saveWindowState]);

  // Toggle minimize
  const toggleMinimize = useCallback(() => {
    const newState = { ...windowState, isMinimized: !windowState.isMinimized };
    setWindowState(newState);
    saveWindowState(newState);
  }, [windowState, saveWindowState]);

  // Update bounds on window resize to prevent chat from going off-screen
  useEffect(() => {
    const handleWindowResize = () => {
      const bounds = getScreenBounds();
      if (windowState.x > bounds.right - MIN_WIDTH || windowState.y > bounds.bottom - MIN_HEIGHT) {
        const newState = {
          ...windowState,
          x: Math.min(windowState.x, bounds.right - MIN_WIDTH),
          y: Math.min(windowState.y, bounds.bottom - MIN_HEIGHT)
        };
        setWindowState(newState);
        saveWindowState(newState);
      }
    };

    window.addEventListener('resize', handleWindowResize);
    return () => window.removeEventListener('resize', handleWindowResize);
  }, [windowState, saveWindowState]);

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
    <div style={{ 
      position: 'fixed', 
      top: 0, 
      left: 0, 
      width: '100vw', 
      height: '100vh', 
      pointerEvents: 'none',
      zIndex: 1000
    }}>
      <Draggable
        nodeRef={nodeRef}
        position={{ x: windowState.x, y: windowState.y }}
        onDrag={handleDrag}
        handle=".chat-drag-handle"
        bounds={{
          left: 0,
          top: 0,
          right: window.innerWidth - MIN_WIDTH,
          bottom: window.innerHeight - MIN_HEIGHT
        }}
        enableUserSelectHack={false}
      >
        <div 
          ref={nodeRef} 
          style={{ 
            position: 'absolute',
            pointerEvents: 'auto'
          }}
        >
        <ResizableBox
          width={windowState.width}
          height={windowState.isMinimized ? 50 : windowState.height}
          minConstraints={[MIN_WIDTH, windowState.isMinimized ? 50 : MIN_HEIGHT]}
          maxConstraints={[MAX_WIDTH, windowState.isMinimized ? 50 : MAX_HEIGHT]}
          onResize={handleResize}
          resizeHandles={windowState.isMinimized ? [] : ['se', 'sw', 'nw', 'ne', 'w', 'e', 's', 'n']}
          handleStyle={{
            se: { cursor: 'se-resize', touchAction: 'none' },
            sw: { cursor: 'sw-resize', touchAction: 'none' },
            nw: { cursor: 'nw-resize', touchAction: 'none' },
            ne: { cursor: 'ne-resize', touchAction: 'none' },
            w: { cursor: 'w-resize', touchAction: 'none' },
            e: { cursor: 'e-resize', touchAction: 'none' },
            s: { cursor: 's-resize', touchAction: 'none' },
            n: { cursor: 'n-resize', touchAction: 'none' }
          }}
        >
          <div className="w-full h-full bg-gray-900 border border-gray-700 rounded-lg shadow-xl flex flex-col" style={{ position: 'relative', zIndex: 50 }}>
            {/* Header */}
            <div 
              className="chat-drag-handle flex items-center justify-between p-3 border-b border-gray-700 cursor-move bg-gray-800 rounded-t-lg"
              style={{ touchAction: 'none', userSelect: 'none' }}
            >
              <div className="flex items-center gap-2">
                <Move className="w-4 h-4 text-gray-400" />
                <Bot className="w-5 h-5 text-blue-400" />
                <h3 className="text-white font-medium">Wilderness Assistant</h3>
              </div>
              <div className="flex items-center gap-1">
                <button
                  onClick={() => setUseStreaming(!useStreaming)}
                  className={`p-1 rounded text-xs px-2 transition-colors ${
                    useStreaming 
                      ? 'bg-green-600 text-white' 
                      : 'bg-gray-600 text-gray-300 hover:bg-gray-500'
                  }`}
                  title={useStreaming ? "Streaming: ON" : "Streaming: OFF"}
                >
                  {useStreaming ? "LIVE" : "BATCH"}
                </button>
                <button
                  onClick={toggleMinimize}
                  className="text-gray-400 hover:text-white p-1 rounded"
                  title={windowState.isMinimized ? "Maximize" : "Minimize"}
                >
                  {windowState.isMinimized ? (
                    <Maximize2 className="w-4 h-4" />
                  ) : (
                    <Minimize2 className="w-4 h-4" />
                  )}
                </button>
                <button
                  onClick={() => setIsOpen(false)}
                  className="text-gray-400 hover:text-white p-1 rounded"
                  title="Close"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            </div>

            {/* Messages - hidden when minimized */}
            {!windowState.isMinimized && (
              <>
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
                <div className="text-sm prose prose-invert prose-sm max-w-none">
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
                      
                      // For user messages, just return plain text
                      if (message.type === 'user') {
                        return <div className="whitespace-pre-wrap">{content}</div>;
                      }
                      
                      // For assistant messages, render as markdown
                      return (
                        <ReactMarkdown
                          remarkPlugins={[remarkGfm]}
                          components={{
                            code({inline, className, children, ...props}) {
                              const match = /language-(\w+)/.exec(className || '');
                              return !inline && match ? (
                                <SyntaxHighlighter
                                  style={oneDark}
                                  language={match[1]}
                                  PreTag="div"
                                  className="rounded text-xs"
                                  {...props}
                                >
                                  {String(children).replace(/\n$/, '')}
                                </SyntaxHighlighter>
                              ) : (
                                <code className={`${className} bg-gray-700 px-1 py-0.5 rounded text-xs`} {...props}>
                                  {children}
                                </code>
                              );
                            },
                            p: ({children}) => <div className="mb-2 last:mb-0">{children}</div>,
                            ul: ({children}) => <ul className="list-disc list-inside mb-2 space-y-1">{children}</ul>,
                            ol: ({children}) => <ol className="list-decimal list-inside mb-2 space-y-1">{children}</ol>,
                            blockquote: ({children}) => <blockquote className="border-l-2 border-gray-600 pl-2 italic">{children}</blockquote>
                          }}
                        >
                          {content}
                        </ReactMarkdown>
                      );
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
                      placeholder={isLoading ? "I'm thinking... you can type your next message" : "Ask me to create regions, paths, descriptions..."}
                      className="flex-1 bg-gray-800 border border-gray-600 rounded-lg px-3 py-2 text-white text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      disabled={false}
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
              </>
            )}
          </div>
        </ResizableBox>
        </div>
      </Draggable>
    </div>
  );
};