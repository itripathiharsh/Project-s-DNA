import { NavLink, useNavigate } from 'react-router-dom';
import { useAnalysis } from '../store/analysis';

const NAV = [
  { to: '/dashboard', label: 'Dashboard', icon: 'grid_view' },
  { to: '/explorer', label: 'Explorer', icon: 'folder_open' },
  { to: '/graph', label: 'Graph Workspace', icon: 'account_tree' },
  { to: '/intelligence', label: 'Intelligence Center', icon: 'psychology' },
  { to: '/risk', label: 'Risk Center', icon: 'security' },
  { to: '/knowledge', label: 'Knowledge Map', icon: 'menu_book' },
  { to: '/evolution', label: 'Evolution Timeline', icon: 'query_stats' },
];

const SECONDARY = [
  { to: '/ai-assistant', label: 'AI Assistant', icon: 'smart_toy' },
  { to: '/cross-repo', label: 'Cross-Repo', icon: 'compare' },
  { to: '/reviews', label: 'Code Reviews', icon: 'rate_review' },
  { to: '/refactoring', label: 'Refactoring Pipeline', icon: 'construction' },
  { to: '/notifications', label: 'Notifications', icon: 'notifications' },
  { to: '/settings', label: 'Settings', icon: 'settings' },
  { to: '/api-docs', label: 'API Docs', icon: 'description' },
  { to: '/admin', label: 'Organization Admin', icon: 'corporate_fare' },
];

export default function Sidebar() {
  const navigate = useNavigate();
  const { repoPath, reset } = useAnalysis();

  return (
    <aside className="hidden md:flex bg-[#09090e]/95 border-r border-border-subtle fixed left-0 top-0 h-full w-sidebar-width flex-col py-4 z-40 shadow-[4px_0_24px_rgba(0,0,0,0.5)] backdrop-blur-md">
      {/* Branding header */}
      <div className="px-gutter mb-5 flex flex-col gap-1">
        <button
          onClick={() => navigate('/')}
          className="flex items-center gap-2 text-left group transition-all"
        >
          <div className="w-7 h-7 rounded-lg bg-primary/10 border border-primary/30 flex items-center justify-center shadow-[0_0_15px_rgba(157,78,221,0.15)] group-hover:border-primary/60 transition-all duration-300">
            <span className="material-symbols-outlined text-[16px] text-primary" style={{ fontVariationSettings: "'FILL' 1" }}>science</span>
          </div>
          <div>
            <div className="font-headline-md text-sm text-on-surface font-extrabold tracking-tight group-hover:text-primary transition-colors">Project DNA</div>
            <div className="text-[10px] text-text-muted font-medium flex items-center gap-1.5 mt-0.5">
              <span className="w-1.5 h-1.5 rounded-full bg-signal-emerald animate-pulse" />
              v4.2.0-stable
            </div>
          </div>
        </button>
      </div>

      {/* Repo Selector / Switcher */}
      <div className="px-gutter mb-4">
        <div className="flex items-center gap-2 px-3 py-2 bg-surface-container-low/60 border border-border-subtle rounded-lg cursor-pointer hover:border-outline/35 hover:bg-surface-container-high/30 transition-all duration-200">
          <span className="material-symbols-outlined text-[15px] text-primary">hub</span>
          <span className="text-[11px] font-semibold text-on-surface truncate flex-1">
            {repoPath ? repoPath.split(/[\\/]/).pop() : 'no-active-repo'}
          </span>
          <span className="material-symbols-outlined text-[14px] text-text-muted">unfold_more</span>
        </div>
      </div>

      {/* Primary Actions */}
      <div className="px-gutter mb-4">
        <button
          onClick={() => {
            localStorage.removeItem('skip_onboarding');
            reset();
            navigate('/onboarding');
          }}
          className="w-full btn-primary py-2 rounded-lg flex items-center justify-center gap-1.5 hover:opacity-90 transition-all shadow-[0_4px_16px_rgba(157,78,221,0.2)]"
        >
          <span className="material-symbols-outlined text-[15px]">add</span>
          New Analysis
        </button>
      </div>

      {/* Nav List */}
      <div className="flex-1 overflow-y-auto px-3 space-y-4 scrollbar-hide">
        <div>
          <div className="px-3 text-[10px] font-bold text-text-muted uppercase tracking-wider mb-2">Core Explorer</div>
          <nav className="space-y-1">
            {NAV.map((n) => (
              <NavLink
                key={n.to}
                to={n.to}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-3 py-2 rounded-lg transition-all duration-200 ${
                    isActive
                      ? 'bg-primary/10 text-primary border border-primary/20 shadow-[0_0_12px_rgba(157,78,221,0.06)] font-semibold'
                      : 'text-on-surface-variant hover:bg-surface-container-high/40 hover:text-on-surface font-medium'
                  }`
                }
              >
                <span className="material-symbols-outlined text-[17px]">{n.icon}</span>
                <span className="text-[12px]">{n.label}</span>
              </NavLink>
            ))}
          </nav>
        </div>

        <div>
          <div className="px-3 text-[10px] font-bold text-text-muted uppercase tracking-wider mb-2">Management & AI</div>
          <nav className="space-y-1">
            {SECONDARY.map((n) => (
              <NavLink
                key={n.to}
                to={n.to}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-3 py-2 rounded-lg transition-all duration-200 ${
                    isActive
                      ? 'bg-primary/10 text-primary border border-primary/20 shadow-[0_0_12px_rgba(157,78,221,0.06)] font-semibold'
                      : 'text-on-surface-variant hover:bg-surface-container-high/40 hover:text-on-surface font-medium'
                  }`
                }
              >
                <span className="material-symbols-outlined text-[17px]">{n.icon}</span>
                <span className="text-[12px]">{n.label}</span>
              </NavLink>
            ))}
          </nav>
        </div>
      </div>

      {/* User profile & Workspace switcher bottom panel */}
      <div className="mt-auto px-gutter pt-3 border-t border-border-subtle flex items-center gap-2.5">
        <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-primary to-signal-cyan flex items-center justify-center font-bold text-xs text-white shadow-[0_0_12px_rgba(157,78,221,0.25)]">
          AD
        </div>
        <div className="flex flex-col min-w-0 flex-1">
          <span className="text-[11px] font-semibold text-on-surface truncate leading-tight">Admin Operator</span>
          <span className="text-[9px] text-text-muted truncate leading-tight mt-0.5">dna-admin@enterprise.io</span>
        </div>
        <span className="material-symbols-outlined text-text-muted text-[16px] cursor-pointer hover:text-on-surface transition-colors">settings</span>
      </div>
    </aside>
  );
}
