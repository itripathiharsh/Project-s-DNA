import React from 'react';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    this.setState({
      error: error,
      errorInfo: errorInfo
    });
    console.error("ErrorBoundary caught an error", error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="flex-1 flex flex-col items-center justify-center text-center gap-4 py-20 px-6 min-h-[50vh]">
          <div className="w-16 h-16 rounded-xl bg-signal-rose/20 border border-signal-rose flex items-center justify-center">
            <span className="material-symbols-outlined text-[32px] text-signal-rose">error</span>
          </div>
          <div className="max-w-xl">
            <h3 className="font-bold text-lg text-on-surface mb-2">Something went wrong.</h3>
            <p className="text-on-surface-variant text-sm leading-relaxed mb-6">
              The application encountered an unexpected error. You can try refreshing the page or contact support if the issue persists.
            </p>
            {this.state.error && (
              <div className="bg-surface-container-high p-4 rounded-lg text-left overflow-auto max-h-[200px] border border-border-subtle mb-6">
                <code className="text-xs text-signal-rose font-code">{this.state.error.toString()}</code>
              </div>
            )}
            <button 
              onClick={() => window.location.reload()}
              className="bg-primary hover:bg-primary-hover text-white px-6 py-2.5 rounded-lg text-sm font-bold shadow-lg shadow-primary/20 transition-all"
            >
              Reload Page
            </button>
          </div>
        </div>
      );
    }

    return this.props.children; 
  }
}

export default ErrorBoundary;
