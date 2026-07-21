import { useState, useEffect } from 'react';
import PageHeader from '../components/PageHeader';
import { getExplorerTree, getExplorerFile, getExplorerSymbols } from '../services/api';
import DOMPurify from 'dompurify';

function TreeNode({ node, onFileSelect, selectedPath, searchTerm }) {
  const [isOpen, setIsOpen] = useState(false);
  const isDir = node.type === 'directory';
  
  useEffect(() => {
    if (searchTerm && isDir) {
      setIsOpen(true);
    }
  }, [searchTerm, isDir]);

  const matchesSearch = (n) => {
    if (n.name.toLowerCase().includes(searchTerm.toLowerCase())) return true;
    if (n.children) return n.children.some(matchesSearch);
    return false;
  };

  if (searchTerm && !matchesSearch(node)) {
    return null;
  }

  const handleToggle = () => {
    if (isDir) {
      setIsOpen(!isOpen);
    } else {
      onFileSelect(node.path);
    }
  };

  const isSelected = selectedPath === node.path;

  return (
    <div className="pl-3.5 font-code-sm text-xs">
      <div
        onClick={handleToggle}
        className={`flex items-center gap-2 py-1.5 px-2.5 rounded-lg cursor-pointer transition-all duration-150 ${
          isSelected 
            ? 'bg-primary/15 text-primary font-bold shadow-[0_0_12px_rgba(157,78,221,0.06)] border border-primary/20' 
            : 'text-on-surface-variant hover:bg-surface-container/60 hover:text-on-surface'
        }`}
      >
        <span className="material-symbols-outlined text-[15px] text-text-muted select-none">
          {isDir ? (isOpen ? 'expand_more' : 'chevron_right') : 'description'}
        </span>
        <span className="material-symbols-outlined text-[15px] text-primary/80 shrink-0">
          {isDir ? 'folder' : 'code'}
        </span>
        <span className="truncate">{node.name}</span>
      </div>
      {isDir && isOpen && node.children && (
        <div className="border-l border-border-subtle/50 ml-3.5 pl-1.5 mt-0.5 space-y-0.5">
          {node.children.map((child) => (
            <TreeNode
              key={child.path || child.name}
              node={child}
              onFileSelect={onFileSelect}
              selectedPath={selectedPath}
              searchTerm={searchTerm}
            />
          ))}
        </div>
      )}
    </div>
  );
}

export default function RepositoryExplorer() {
  const [tree, setTree] = useState(null);
  const [selectedFile, setSelectedFile] = useState(null);
  const [symbols, setSymbols] = useState([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const [fileLoading, setFileLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function loadTree() {
      try {
        const t = await getExplorerTree();
        setTree(t);
      } catch (err) {
        setError(err.message || String(err));
      } finally {
        setLoading(false);
      }
    }
    loadTree();
  }, []);

  const handleFileSelect = async (path) => {
    setFileLoading(true);
    try {
      const fileData = await getExplorerFile(path);
      setSelectedFile(fileData);
      
      const symbolData = await getExplorerSymbols(path);
      setSymbols(symbolData.symbols || []);
    } catch (err) {
      console.error('Error loading file details:', err);
      setError('Failed to load file: ' + (err.message || 'Unknown error'));
    } finally {
      setFileLoading(false);
    }
  };

  const jumpToLine = (lineNum) => {
    const el = document.getElementById(`line-${lineNum}`);
    if (el) {
      el.scrollIntoView({ behavior: 'smooth', block: 'center' });
      el.classList.add('bg-primary/20', 'border-l-2', 'border-l-primary');
      setTimeout(() => {
        el.classList.remove('bg-primary/20', 'border-l-2', 'border-l-primary');
      }, 2000);
    }
  };

  // Sleek client-side regex code syntax highligher
  const highlightCode = (lineText) => {
    if (!lineText) return ' ';
    let escaped = lineText
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;");

    // Keywords highlighting
    const keywords = /\b(def|class|return|import|from|const|let|var|function|public|private|static|async|await|try|except|catch|finally|if|else|for|while|in|as)\b/g;
    escaped = escaped.replace(keywords, '<span class="text-primary font-semibold">$1</span>');

    // Strings highlighting
    escaped = escaped.replace(/(['"`])(.*?)\1/g, '<span class="text-signal-emerald">$1$2$1</span>');

    // Comments highlighting
    escaped = escaped.replace(/(#.*|\/\/.*)/g, '<span class="text-text-muted italic">$1</span>');

    return <span dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(escaped) }} />;
  };

  return (
    <>
      <PageHeader title="Repository Explorer" subtitle="Browse files, code symbols, and AST entities" />
      
      <div className="p-6 flex-1 flex flex-col lg:flex-row gap-6 overflow-hidden max-h-[calc(100vh-140px)] max-w-[1600px] mx-auto w-full">
        {/* Left Column: Folder Tree */}
        <div className="w-full lg:w-80 card-base flex flex-col gap-4 overflow-y-auto bg-surface-container/30 border border-border-subtle shadow-xl flex-shrink-0">
          <div className="relative">
            <span className="material-symbols-outlined absolute left-3 top-2.5 text-text-muted text-[16px]">search</span>
            <input
              type="text"
              placeholder="Filter files..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="input-base pl-9 pr-3 text-xs bg-surface-container-lowest/50"
            />
          </div>
          <div className="flex-1 overflow-y-auto pr-1 scrollbar-hide">
            {loading ? (
              <div className="flex items-center justify-center p-8">
                <div className="w-5 h-5 border-2 border-primary/20 border-t-primary rounded-full animate-spin" />
              </div>
            ) : error ? (
              <div className="text-signal-rose text-xs p-4 border border-signal-rose/20 bg-signal-rose/5 rounded-lg">{error}</div>
            ) : tree ? (
              <TreeNode
                node={tree}
                onFileSelect={handleFileSelect}
                selectedPath={selectedFile?.path}
                searchTerm={search}
              />
            ) : (
              <div className="text-text-muted text-xs p-4">No codebase index active.</div>
            )}
          </div>
        </div>

        {/* Middle Column: File Content Preview */}
        <div className="flex-1 card-base flex flex-col overflow-hidden bg-[#050508]/85 border border-border-subtle p-0 shadow-2xl">
          {fileLoading ? (
            <div className="flex-1 flex flex-col items-center justify-center gap-3">
              <div className="w-8 h-8 border-2 border-primary/20 border-t-primary rounded-full animate-spin" />
              <span className="text-text-muted text-xs">Parsing file content...</span>
            </div>
          ) : selectedFile ? (
            <div className="flex-1 flex flex-col overflow-hidden">
              <div className="p-3 border-b border-border-subtle/50 flex items-center justify-between bg-surface-container/40 backdrop-blur-md">
                <span className="font-code-sm text-xs text-primary font-bold">{selectedFile.path}</span>
                <span className="text-text-muted font-code-sm text-[11px] bg-surface-container-low/80 px-2 py-0.5 rounded border border-border-subtle">
                  {selectedFile.content.split('\n').length} lines
                </span>
              </div>
              <div className="flex-1 overflow-auto p-4 font-code-sm text-xs leading-relaxed scrollbar-hide bg-[#050508]">
                <pre className="text-on-surface/90 whitespace-pre">
                  {selectedFile.content.split('\n').map((line, idx) => (
                    <div key={idx} id={`line-${idx + 1}`} className="flex hover:bg-surface-container/30 py-[1px] transition-colors rounded">
                      <span className="w-10 text-right select-none text-text-muted/50 pr-3.5 border-r border-border-subtle/30 mr-3.5">
                        {idx + 1}
                      </span>
                      <code className="text-xs">{highlightCode(line)}</code>
                    </div>
                  ))}
                </pre>
              </div>
            </div>
          ) : (
            <div className="flex-1 flex flex-col items-center justify-center text-center gap-4 py-20 max-w-sm mx-auto">
              <div className="w-12 h-12 rounded-xl bg-surface-container-high/40 border border-border-subtle flex items-center justify-center">
                <span className="material-symbols-outlined text-[28px] text-primary">code</span>
              </div>
              <div>
                <h3 className="font-bold text-xs text-on-surface uppercase tracking-wider mb-1">No file selected</h3>
                <p className="text-on-surface-variant text-[11px] leading-relaxed">
                  Select a module from the repository tree on the left to review its raw declarations and index definitions.
                </p>
              </div>
            </div>
          )}
        </div>

        {/* Right Column: Symbols Panel */}
        <div className="w-full lg:w-80 card-base flex flex-col gap-4 overflow-y-auto bg-surface-container/30 border border-border-subtle shadow-xl flex-shrink-0">
          <h3 className="font-bold text-xs text-on-surface uppercase tracking-wider pb-2 border-b border-border-subtle/50 flex items-center gap-1.5">
            <span className="material-symbols-outlined text-primary text-[18px]">psychology</span> 
            <span>AST Symbols</span>
          </h3>
          <div className="flex-1 overflow-y-auto space-y-2 pr-1 scrollbar-hide">
            {selectedFile ? (
              symbols.length > 0 ? (
                symbols.map((sym, idx) => (
                  <div
                    key={idx}
                    onClick={() => jumpToLine(sym.line)}
                    className="flex flex-col p-2.5 rounded-lg bg-surface-container-low/40 border border-border-subtle/60 hover:border-primary/30 hover:bg-surface-container-high/30 cursor-pointer transition-all duration-150"
                  >
                    <div className="flex items-center justify-between mb-1 gap-2">
                      <span className="font-code-sm text-xs text-primary truncate font-bold" title={sym.name}>{sym.name}</span>
                      <span className={`badge text-[9px] ${sym.kind === 'class' ? 'badge-critical' : sym.kind === 'function' ? 'badge-warn' : 'badge-info'}`}>
                        {sym.kind}
                      </span>
                    </div>
                    <div className="flex items-center justify-between text-text-muted text-[10px]">
                      <span>Line {sym.line}</span>
                      {sym.properties && sym.properties.complexity !== undefined && (
                        <span>Complexity: <strong className="text-signal-rose">{sym.properties.complexity}</strong></span>
                      )}
                    </div>
                  </div>
                ))
              ) : (
                <div className="text-text-muted text-xs text-center py-6">No symbols indexed in this file.</div>
              )
            ) : (
              <div className="text-text-muted text-xs text-center py-6">Select a file to show AST symbol maps.</div>
            )}
          </div>
        </div>
      </div>
    </>
  );
}
