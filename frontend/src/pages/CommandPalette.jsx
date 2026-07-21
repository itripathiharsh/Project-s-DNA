import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import PageHeader from '../components/PageHeader';
import { readAllNotifications } from '../services/api';
import { useAnalysis } from '../store/analysis';
import { useNotification } from '../components/NotificationContext';

export default function CommandPalette() {
  const navigate = useNavigate();
  const { reset } = useAnalysis();
  const [search, setSearch] = useState('');
  const [selectedIndex, setSelectedIndex] = useState(0);
  const inputRef = useRef(null);
  const { toast } = useNotification();

  const COMMANDS = [
    { name: 'Navigate: Go to Dashboard', description: 'Open main dashboard overview', icon: 'dashboard', action: () => navigate('/dashboard') },
    { name: 'Navigate: Go to Explorer', description: 'Browse files & symbols', icon: 'folder_open', action: () => navigate('/explorer') },
    { name: 'Navigate: Go to Dependency Graph', description: 'Visualize file relationships', icon: 'account_tree', action: () => navigate('/graph') },
    { name: 'Navigate: Go to AI Assistant', description: 'Ask questions to the codebase AI', icon: 'smart_toy', action: () => navigate('/ai-assistant') },
    { name: 'Navigate: Go to Risk Center', description: 'Audit security and quality alerts', icon: 'security', action: () => navigate('/risk') },
    { name: 'Navigate: Go to Knowledge Map', description: 'Audit contributions and bus factor', icon: 'menu_book', action: () => navigate('/knowledge') },
    { name: 'Navigate: Go to settings', description: 'Configure analysis engines', icon: 'settings', action: () => navigate('/settings') },
    { name: 'Navigate: Go to Team Reviews', description: 'Open collaborative reviews', icon: 'rate_review', action: () => navigate('/reviews') },
    { name: 'Navigate: Go to Refactoring Roadmap', description: 'View refactoring roadmap and verification', icon: 'construction', action: () => navigate('/refactoring') },
    { name: 'Navigate: Go to Organization Admin', description: 'Configure teams and permissions', icon: 'corporate_fare', action: () => navigate('/admin') },
    { name: 'Navigate: Go to API Docs', description: 'View FastAPI interactive swagger documentation', icon: 'description', action: () => navigate('/api-docs') },
    { name: 'Action: Start New Analysis', description: 'Configure and run codebase analysis', icon: 'add', action: () => { reset(); navigate('/onboarding'); } },
    { name: 'Action: Clear All Notifications', description: 'Mark all background alerts as read', icon: 'notifications_off', action: async () => {
        try {
          await readAllNotifications();
          toast('All notifications marked as read.', 'success');
        } catch (err) {
          toast('Failed to clear notifications: ' + err.message, 'error');
        }
    }},
    { name: 'Action: Open Layout Orchestration', description: 'Manage window layout settings', icon: 'grid_view', action: () => navigate('/orchestration') },
  ];

  const filtered = COMMANDS.filter((cmd) =>
    cmd.name.toLowerCase().includes(search.toLowerCase()) ||
    cmd.description.toLowerCase().includes(search.toLowerCase())
  );

  useEffect(() => {
    // Focus search on mount
    inputRef.current?.focus();
  }, []);

  useEffect(() => {
    setSelectedIndex(0);
  }, [search]);

  const handleKeyDown = (e) => {
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      setSelectedIndex((prev) => (prev + 1) % filtered.length);
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setSelectedIndex((prev) => (prev - 1 + filtered.length) % filtered.length);
    } else if (e.key === 'Enter') {
      e.preventDefault();
      if (filtered[selectedIndex]) {
        filtered[selectedIndex].action();
      }
    }
  };

  return (
    <>
      <PageHeader title="Command Palette" subtitle="Quickly execute actions, navigate, and audit settings" />
      <div className="p-6 flex-1 flex flex-col gap-4 max-w-3xl mx-auto w-full font-body-sm">
        <div className="card-base flex flex-col gap-4 bg-[#0d0d0d]">
          <div className="relative">
            <span className="material-symbols-outlined absolute left-3 top-3 text-primary text-[20px]">keyboard_command_key</span>
            <input
              ref={inputRef}
              type="text"
              placeholder="Search actions & commands... (Use Arrow keys & Enter to select)"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              onKeyDown={handleKeyDown}
              className="input-base pl-10 pr-3 py-3 bg-surface-container-high/90 text-on-surface text-base"
            />
          </div>
          
          <div className="flex flex-col gap-1.5 max-h-[400px] overflow-y-auto pr-1">
            {filtered.map((cmd, idx) => {
              const isSelected = selectedIndex === idx;
              return (
                <div
                  key={idx}
                  onClick={cmd.action}
                  onMouseEnter={() => setSelectedIndex(idx)}
                  className={`flex items-center gap-3.5 p-3 rounded cursor-pointer transition-colors ${
                    isSelected
                      ? 'bg-primary/20 text-on-surface border border-primary/50'
                      : 'bg-surface-container border border-transparent hover:bg-surface-container-high text-on-surface-variant'
                  }`}
                >
                  <span className="material-symbols-outlined text-[18px] text-primary">{cmd.icon}</span>
                  <div className="flex-1">
                    <div className="font-bold text-sm text-on-surface">{cmd.name}</div>
                    <div className="text-xs text-text-muted">{cmd.description}</div>
                  </div>
                  {isSelected && (
                    <span className="font-code-sm text-[10px] bg-primary/20 text-primary px-1.5 py-0.5 rounded border border-primary/30 uppercase">
                      Enter
                    </span>
                  )}
                </div>
              );
            })}
            {filtered.length === 0 && (
              <div className="text-center text-text-muted py-8">No commands found. Try searching navigating or actions.</div>
            )}
          </div>
        </div>

        <div className="text-center text-text-muted text-[11px] mt-2">
          Tip: You can use <kbd className="bg-surface-container-high px-1.5 py-0.5 rounded font-code-sm border border-border-subtle">ArrowUp</kbd> and <kbd className="bg-surface-container-high px-1.5 py-0.5 rounded font-code-sm border border-border-subtle">ArrowDown</kbd> to move selection and <kbd className="bg-surface-container-high px-1.5 py-0.5 rounded font-code-sm border border-border-subtle">Enter</kbd> to run it.
        </div>
      </div>
    </>
  );
}
