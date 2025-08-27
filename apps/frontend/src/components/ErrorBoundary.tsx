import React from 'react';

interface ErrorBoundaryState {
  hasError: boolean;
  error?: Error;
  errorInfo?: React.ErrorInfo;
}

interface ErrorBoundaryProps {
  children: React.ReactNode;
  fallback?: React.ComponentType<{ error: Error; errorInfo?: React.ErrorInfo }>;
}

export class ErrorBoundary extends React.Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('ErrorBoundary caught an error:', error);
    console.error('Error info:', errorInfo);
    
    this.setState({
      hasError: true,
      error,
      errorInfo
    });
  }

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        const FallbackComponent = this.props.fallback;
        return <FallbackComponent error={this.state.error!} errorInfo={this.state.errorInfo} />;
      }

      return (
        <div className="bg-red-900 border border-red-700 rounded-lg p-4 m-4">
          <h2 className="text-red-100 font-semibold mb-2">Something went wrong</h2>
          <details className="text-red-200 text-sm">
            <summary className="cursor-pointer">Error details</summary>
            <pre className="mt-2 whitespace-pre-wrap">{this.state.error?.toString()}</pre>
            {this.state.errorInfo && (
              <pre className="mt-2 whitespace-pre-wrap">{this.state.errorInfo.componentStack}</pre>
            )}
          </details>
          <button 
            onClick={() => this.setState({ hasError: false, error: undefined, errorInfo: undefined })}
            className="mt-3 bg-red-700 hover:bg-red-600 text-white px-3 py-1 rounded text-sm"
          >
            Try Again
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}

// Chat-specific fallback component
export const ChatErrorFallback: React.FC<{ error: Error; errorInfo?: React.ErrorInfo }> = ({ error }) => (
  <div className="bg-red-900 border border-red-700 rounded-lg p-3 m-3">
    <div className="flex items-center gap-2 text-red-100 text-sm">
      <span>⚠️</span>
      <span>Chat assistant encountered an error</span>
    </div>
    <p className="text-red-200 text-xs mt-1">
      {error.message || 'Unknown error occurred'}
    </p>
  </div>
);