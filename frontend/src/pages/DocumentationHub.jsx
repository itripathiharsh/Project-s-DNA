import React, { useState, useEffect, useRef } from 'react';
import PageHeader from '../components/PageHeader';
import { API_BASE, getHeaders } from '../services/api';
import DOMPurify from 'dompurify';

const DOC_TYPES = [
  { id: 'readme', label: 'Auto README Generator', icon: 'article', desc: 'Auto-generated project overview' },
  { id: 'architecture', label: 'Auto Architecture Docs', icon: 'account_tree', desc: 'High-level component hierarchy' },
  { id: 'api', label: 'API Documentation', icon: 'api', desc: 'Endpoints and function signatures' },
  { id: 'sequence', label: 'Sequence Diagram', icon: 'linear_scale', desc: 'Call flows and interactions' },
  { id: 'mermaid', label: 'Mermaid Generator', icon: 'polyline', desc: 'System flowchart diagrams' },
  { id: 'c4', label: 'C4 Diagram', icon: 'view_comfy', desc: 'C4 Model Context visualization' },
  { id: 'er', label: 'ER Diagram', icon: 'schema', desc: 'Entity relationships and schemas' },
  { id: 'module', label: 'Module Documentation', icon: 'inventory_2', desc: 'File and folder summaries' },
  { id: 'class', label: 'Class Documentation', icon: 'data_object', desc: 'Object-oriented structures' },
  { id: 'wiki', label: 'Project Wiki Generator', icon: 'menu_book', desc: 'Full indexed knowledge base' }
];

export default function DocumentationHub() {
  const [activeDoc, setActiveDoc] = useState('readme');
  const [content, setContent] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [docCache, setDocCache] = useState({}); // New cache state
  
  const mermaidRef = useRef(null);

  useEffect(() => {
    // Load Mermaid.js from CDN to render diagrams dynamically
    const script = document.createElement('script');
    script.src = 'https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js';
    script.async = true;
    script.onload = () => {
      if (window.mermaid) {
        window.mermaid.initialize({ startOnLoad: false, theme: 'dark', fontFamily: 'Inter' });
      }
    };
    document.body.appendChild(script);
    return () => { document.body.removeChild(script); };
  }, []);

  useEffect(() => {
    const endpoint = `${API_BASE}/v1/documentation/generate/${activeDoc}`;
    
    // Use cached content if available to prevent re-fetching
    if (docCache[endpoint]) {
      setContent(docCache[endpoint]);
      return;
    }

    const controller = new AbortController();
    
    setLoading(true);
    setError(null);
    fetch(endpoint, { headers: getHeaders(), signal: controller.signal })
      .then(res => {
        if (!res.ok) throw new Error('Failed to generate documentation');
        return res.json();
      })
      .then(data => {
        setContent(data.content || '');
        setDocCache(prev => ({ ...prev, [endpoint]: data.content || '' }));
      })
      .catch(err => {
        if (err.name !== 'AbortError') {
          setError(err.message);
        }
      })
      .finally(() => {
        if (!controller.signal.aborted) {
          setLoading(false);
        }
      });
      
    return () => controller.abort();
  }, [activeDoc, docCache]);

  const handleDownload = async () => {
    // 1. Modern approach: Native File System Access API
    // Bypasses the Chrome Blob UUID naming bug and handles unlimited file sizes.
    if ('showSaveFilePicker' in window) {
      try {
        const handle = await window.showSaveFilePicker({
          suggestedName: `${activeDoc}-documentation.md`,
          types: [{
            description: 'Markdown Document',
            accept: { 'text/markdown': ['.md'] },
          }],
        });
        const writable = await handle.createWritable();
        await writable.write(content);
        await writable.close();
        return; // Success
      } catch (err) {
        // If the user cancelled the dialog, just return
        if (err.name === 'AbortError') return;
        console.error('Save file picker failed:', err);
      }
    }

    // 2. Fallback approach for browsers without showSaveFilePicker (e.g., Firefox)
    const blob = new Blob([content], { type: 'text/markdown;charset=utf-8' });
    const blobUrl = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.style.display = 'none';
    a.href = blobUrl;
    a.download = `${activeDoc}-documentation.md`;
    document.body.appendChild(a);
    a.click();
    setTimeout(() => {
      document.body.removeChild(a);
      URL.revokeObjectURL(blobUrl);
    }, 10000);
  };

  useEffect(() => {
    let isMounted = true;
    
    // Attempt to render mermaid if content contains mermaid block
    if (content.includes('```mermaid') && window.mermaid && mermaidRef.current) {
      const matches = content.match(/```mermaid\n([\s\S]*?)```/);
      if (matches && matches[1]) {
        try {
          mermaidRef.current.innerHTML = '';
          const id = `mermaid-${Date.now()}`;
          window.mermaid.render(id, matches[1]).then(result => {
            if (isMounted && mermaidRef.current) {
               mermaidRef.current.innerHTML = result.svg;
               // Fix SVG width/height to avoid microscopic rendering
               const svgEl = mermaidRef.current.querySelector('svg');
               if (svgEl) {
                 svgEl.style.maxWidth = '100%';
                 svgEl.style.height = 'auto';
               }
            }
          }).catch(e => {
            console.error("Mermaid render error:", e);
            // Mermaid leaves a temporary element in the body on failure, which causes the UI bug. Clean it up.
            const tempEl = document.getElementById('d' + id);
            if (tempEl) tempEl.remove();
            
            // Render a friendly error inside the container instead of bleeding over the page
            if (isMounted && mermaidRef.current) {
               mermaidRef.current.innerHTML = `<div class="text-red-400 font-mono text-sm p-4 bg-red-950/30 rounded border border-red-500/30">Failed to render diagram. The AI generated invalid Mermaid syntax.</div>`;
            }
          });
        } catch (e) {
          console.error("Mermaid error:", e);
        }
      }
    }
    
    return () => {
      isMounted = false;
    };
  }, [content]);

  // Basic custom markdown parser for premium display
  const renderContent = () => {
    if (content.includes('```mermaid')) {
      // Split to show text above diagram and diagram itself
      const parts = content.split(/```mermaid\n[\s\S]*?```/);
      return (
        <div className="space-y-6">
          <div className="text-slate-300 whitespace-pre-wrap">{parts[0].replace(/#/g, '')}</div>
          <div className="bg-slate-900/50 p-4 md:p-8 rounded-xl border border-sky-500/20 shadow-[0_0_30px_rgba(14,165,233,0.1)] flex justify-center items-center overflow-x-auto min-h-[300px]">
            <div ref={mermaidRef} className="mermaid-container w-full flex justify-center" />
          </div>
          {parts[1] && <div className="text-slate-300 whitespace-pre-wrap">{parts[1]}</div>}
        </div>
      );
    }

    let inTable = false;
    let tableHeaders = [];
    let tableRows = [];
    const renderedLines = [];

    const parseInline = (text) => {
      if (!text) return '';
      return text
        .replace(/\*\*(.*?)\*\*/g, '<strong class="text-white font-semibold">$1</strong>')
        .replace(/`(.*?)`/g, '<code class="bg-slate-800 text-sky-300 px-1.5 py-0.5 rounded text-sm font-mono">$1</code>')
        .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" class="text-sky-400 hover:underline">$1</a>');
    };

    const lines = content.split('\n');
    for (let i = 0; i < lines.length; i++) {
      let line = lines[i];
      if (line.startsWith('|')) {
        inTable = true;
        const cols = line.split('|').filter(c => c.trim() !== '').map(c => c.trim());
        if (tableHeaders.length === 0) {
          tableHeaders = cols;
        } else if (!line.includes('---')) {
          tableRows.push(cols);
        }
        // If last line or next line is not a table row, render table
        if (i === lines.length - 1 || !lines[i + 1].startsWith('|')) {
          renderedLines.push(
            <div key={`table-${i}`} className="overflow-x-auto my-6 rounded-lg border border-white/10">
              <table className="w-full text-left text-sm text-slate-300">
                <thead className="text-xs text-slate-400 uppercase bg-slate-900/50 border-b border-white/10">
                  <tr>
                    {tableHeaders.map((h, hIdx) => (
                      <th key={hIdx} className="px-6 py-3 font-semibold">{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {tableRows.map((r, rIdx) => (
                    <tr key={rIdx} className="border-b border-white/5 last:border-0 hover:bg-white/5 transition-colors">
                      {r.map((c, cIdx) => (
                        <td key={cIdx} className="px-6 py-4 whitespace-nowrap" dangerouslySetInnerHTML={{__html: DOMPurify.sanitize(parseInline(c))}} />
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          );
          inTable = false;
          tableHeaders = [];
          tableRows = [];
        }
        continue;
      }

      const tLine = line.trimStart();
      if (tLine.match(/^#\s+/)) renderedLines.push(<h1 key={i} className="text-3xl font-black text-white mb-6 tracking-tight border-b border-white/10 pb-4 flex items-center justify-between" dangerouslySetInnerHTML={{__html: DOMPurify.sanitize(parseInline(tLine.replace(/^#\s+/, '')))}} />);
      else if (tLine.match(/^##\s+/)) renderedLines.push(<h2 key={i} id={tLine.replace(/^##\s+/, '').trim().toLowerCase().replace(/[^a-z0-9]+/g, '-')} className="text-xl font-bold text-sky-400 mt-8 mb-4" dangerouslySetInnerHTML={{__html: DOMPurify.sanitize(parseInline(tLine.replace(/^##\s+/, '')))}} />);
      else if (tLine.match(/^###+\s+/)) renderedLines.push(<h3 key={i} className="text-lg font-semibold text-white/90 mt-6 mb-3" dangerouslySetInnerHTML={{__html: DOMPurify.sanitize(parseInline(tLine.replace(/^###+\s+/, '')))}} />);
      else if (tLine.match(/^>\s+/)) renderedLines.push(<blockquote key={i} className="border-l-4 border-sky-500 pl-4 py-2 my-4 text-slate-400 bg-sky-950/20 rounded-r-lg" dangerouslySetInnerHTML={{__html: DOMPurify.sanitize(parseInline(tLine.replace(/^>\s+/, '')))}} />);
      else if (tLine.match(/^[-*]\s+/)) renderedLines.push(
        <div key={i} className="flex items-start gap-3 text-slate-300 ml-4 mb-2">
          <span className="material-symbols-outlined text-[14px] text-sky-500 mt-1">stop_circle</span>
          <span dangerouslySetInnerHTML={{__html: DOMPurify.sanitize(parseInline(tLine.replace(/^[-*]\s+/, '')))}} />
        </div>
      );
      else if (tLine.startsWith('---')) renderedLines.push(<hr key={i} className="border-t border-white/10 my-8" />);
      else if (tLine.match(/^\d+\.\s+/)) renderedLines.push(
        <div key={i} className="text-slate-300 ml-4 mb-2 flex items-start gap-2">
          <span className="text-sky-500 font-bold min-w-[20px]">{tLine.match(/^\d+\./)[0]}</span>
          <span dangerouslySetInnerHTML={{__html: DOMPurify.sanitize(parseInline(tLine.replace(/^\d+\.\s+/, '')))}} />
        </div>
      );
      else if (tLine.trim() === '') renderedLines.push(<div key={i} className="h-2" />);
      else renderedLines.push(<p key={i} className="text-slate-300 leading-relaxed mb-2" dangerouslySetInnerHTML={{__html: DOMPurify.sanitize(parseInline(line))}} />);
    }

    return <div className="space-y-1">{renderedLines}</div>;
  };

  return (
    <div className="h-full flex flex-col bg-slate-950 overflow-hidden font-sans">
      <PageHeader 
        title="Documentation Hub" 
        icon="book_4" 
        description="Auto-generated, deterministic documentation and diagrams derived directly from your codebase."
      />

      <div className="flex-1 flex overflow-hidden">
        {/* Sidebar */}
        <div className="w-80 border-r border-white/10 bg-slate-900/40 flex flex-col overflow-y-auto">
          <div className="p-4 text-xs font-bold text-slate-500 uppercase tracking-widest border-b border-white/5">
            Generators
          </div>
          <div className="p-2 space-y-1">
            {DOC_TYPES.map(doc => {
              const active = doc.id === activeDoc;
              return (
                <button
                  key={doc.id}
                  onClick={() => setActiveDoc(doc.id)}
                  className={`w-full text-left flex items-start gap-3 p-3 rounded-lg transition-all duration-200 ${
                    active 
                      ? 'bg-sky-500/10 border-l-2 border-sky-500 shadow-[inset_0_0_20px_rgba(14,165,233,0.05)]' 
                      : 'hover:bg-white/5 border-l-2 border-transparent'
                  }`}
                >
                  <span className={`material-symbols-outlined ${active ? 'text-sky-400' : 'text-slate-400'}`}>
                    {doc.icon}
                  </span>
                  <div>
                    <div className={`font-semibold text-sm ${active ? 'text-white' : 'text-slate-300'}`}>
                      {doc.label}
                    </div>
                    <div className="text-[10px] text-slate-500 mt-1">{doc.desc}</div>
                  </div>
                </button>
              );
            })}
          </div>
        </div>

        {/* Main Content Area */}
        <div className="flex-1 p-8 overflow-y-auto relative bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-slate-900 via-slate-950 to-black">
          {loading ? (
            <div className="h-full flex flex-col items-center justify-center text-sky-500">
              <span className="material-symbols-outlined text-6xl animate-spin mb-4">settings</span>
              <div className="font-mono text-sm tracking-widest animate-pulse">GENERATING DOCUMENTS...</div>
            </div>
          ) : error ? (
            <div className="p-6 bg-red-950/30 border border-red-500/50 rounded-xl text-red-200">
              <div className="flex items-center gap-2 mb-2">
                <span className="material-symbols-outlined text-red-500">error</span>
                <h3 className="font-bold">Generation Failed</h3>
              </div>
              <p className="text-sm opacity-80">{error}</p>
            </div>
          ) : (
            <div className="max-w-5xl mx-auto">
              <div className="flex justify-end items-center mb-6">
                
                <button 
                  onClick={handleDownload}
                  className="flex items-center gap-2 px-4 py-2 bg-sky-500/10 text-sky-400 hover:bg-sky-500/20 border border-sky-500/30 rounded-lg transition-colors font-semibold text-sm"
                >
                  <span className="material-symbols-outlined text-[18px]">download</span>
                  Download Markdown
                </button>
              </div>
              <div className="bg-slate-900/40 border border-white/10 rounded-2xl p-10 shadow-2xl backdrop-blur-sm relative overflow-hidden">
                {/* Decorative background glow */}
                <div className="absolute top-0 right-0 w-96 h-96 bg-sky-500/10 rounded-full blur-[100px] pointer-events-none transform translate-x-1/2 -translate-y-1/2" />
                
                {renderContent()}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
