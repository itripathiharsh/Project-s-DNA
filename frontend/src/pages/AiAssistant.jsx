import { useState, useRef, useEffect } from 'react';
import PageHeader from '../components/PageHeader';
import { queryAssistant } from '../services/api';

export default function AiAssistant() {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      text: "Hello! I am your Project DNA assistant. I am connected directly to the codebase entity graph and reasoning engines.\n\nYou can ask me questions about structural risks, file complexity, contributors, or key findings.",
      timestamp: new Date().toLocaleTimeString()
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const feedEndRef = useRef(null);

  const scrollToBottom = () => {
    feedEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userQuery = input.trim();
    setMessages((prev) => [
      ...prev,
      { role: 'user', text: userQuery, timestamp: new Date().toLocaleTimeString() }
    ]);
    setInput('');
    setLoading(true);

    try {
      const res = await queryAssistant(userQuery);
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          text: res.answer,
          timestamp: new Date(res.timestamp || Date.now()).toLocaleTimeString()
        }
      ]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          text: `Error querying assistant: ${err.message || err}`,
          timestamp: new Date().toLocaleTimeString(),
          isError: true
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const SUGGESTED_QUERIES = [
    'What structural risks exist in this codebase?',
    'Show me the most complex files.',
    'Who are the top contributors?',
    'List the top insights from the analysis.'
  ];

  return (
    <>
      <PageHeader title="AI Assistant" subtitle="Ask questions and query structural findings from the codebase reasoning engine" />
      
      <div className="p-6 flex-1 flex flex-col lg:flex-row gap-6 overflow-hidden max-h-[calc(100vh-140px)] max-w-[1600px] mx-auto w-full">
        {/* Chat Feed */}
        <div className="flex-1 card-base flex flex-col overflow-hidden bg-[#0a0a0f]/60 border border-border-subtle p-0 shadow-2xl relative">
          <div className="flex-1 overflow-y-auto p-5 flex flex-col gap-4">
            {messages.map((msg, idx) => (
              <div
                key={idx}
                className={`max-w-[80%] flex flex-col gap-1.5 p-4 rounded-xl border transition-all duration-300 ${
                  msg.role === 'user'
                    ? 'self-end bg-gradient-to-tr from-primary to-primary-fixed-dim border-primary/20 text-white shadow-[0_4px_16px_rgba(157,78,221,0.15)] rounded-tr-none'
                    : msg.isError
                    ? 'self-start bg-signal-rose/10 border-signal-rose/20 text-signal-rose rounded-tl-none'
                    : 'self-start bg-surface-container/60 border-border-subtle border-l-4 border-l-primary text-on-surface rounded-tl-none'
                }`}
              >
                <div className={`flex justify-between items-center text-[10px] uppercase font-bold tracking-wider mb-0.5 ${msg.role === 'user' ? 'text-primary-fixed/80' : 'text-text-muted'}`}>
                  <span>{msg.role === 'user' ? 'Operator' : 'DNA reasoning agent'}</span>
                  <span className="font-normal">{msg.timestamp}</span>
                </div>
                <p className="whitespace-pre-wrap leading-relaxed text-xs">{msg.text}</p>
              </div>
            ))}
            {loading && (
              <div className="self-start bg-surface-container/60 border border-border-subtle border-l-4 border-l-signal-cyan p-4 rounded-xl rounded-tl-none flex items-center gap-3">
                <div className="flex items-center gap-1">
                  <span className="w-1.5 h-1.5 rounded-full bg-signal-cyan animate-bounce" style={{ animationDelay: '0ms' }} />
                  <span className="w-1.5 h-1.5 rounded-full bg-signal-cyan animate-bounce" style={{ animationDelay: '150ms' }} />
                  <span className="w-1.5 h-1.5 rounded-full bg-signal-cyan animate-bounce" style={{ animationDelay: '300ms' }} />
                </div>
                <span className="text-[11px] font-medium text-text-muted">Analyzing AST graphs...</span>
              </div>
            )}
            <div ref={feedEndRef} />
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit} className="border-t border-border-subtle/50 p-4 bg-[#0d0d14]/80 backdrop-blur-xl flex gap-2.5 items-center">
            <input
              type="text"
              required
              disabled={loading}
              placeholder="Ask a question (e.g. 'Show me the dependency risk hotspot files')..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              className="input-base bg-surface-container-lowest/50 border border-border-subtle"
            />
            <button
              type="submit"
              disabled={loading || !input.trim()}
              className="btn-primary px-5 py-2.5 rounded-lg flex items-center gap-1.5 h-[42px] shrink-0 hover:scale-[1.02] active:scale-[0.98] transition-all"
            >
              <span className="material-symbols-outlined text-[15px]">send</span>
              <span className="hidden sm:inline">Send</span>
            </button>
          </form>
        </div>

        {/* Suggestions & Info */}
        <div className="w-full lg:w-80 flex flex-col gap-4 flex-shrink-0">
          <div className="card-base flex flex-col gap-3">
            <h3 className="font-bold text-xs text-on-surface uppercase tracking-wider flex items-center gap-1.5 pb-2 border-b border-border-subtle/50">
              <span className="material-symbols-outlined text-primary text-[18px]">tips_and_updates</span> 
              <span>Suggested Queries</span>
            </h3>
            <p className="text-[11px] text-text-muted leading-relaxed">Click any quick prompt below to populate the input box:</p>
            <div className="flex flex-col gap-2 mt-1">
              {SUGGESTED_QUERIES.map((q, idx) => (
                <button
                  key={idx}
                  onClick={() => {
                    if (!loading) setInput(q);
                  }}
                  disabled={loading}
                  className="text-left p-3 rounded-lg bg-surface-container-low/40 border border-border-subtle/60 hover:border-primary/45 hover:bg-surface-container-high/30 transition-all text-[11px] leading-relaxed text-on-surface-variant hover:text-on-surface font-medium"
                >
                  {q}
                </button>
              ))}
            </div>
          </div>

          <div className="card-base bg-gradient-to-br from-[#0c0c16] to-[#0e0c16]">
            <span className="block text-[9px] text-text-muted font-bold uppercase tracking-wider mb-1.5">Context Scope</span>
            <p className="text-[11px] text-text-muted leading-relaxed">
              The reasoning agent utilizes locally parsed syntax structures, SCM metrics, and evidence tables. Queries are resolved deterministically against the codebase graph without external network dependencies.
            </p>
          </div>
        </div>
      </div>
    </>
  );
}
