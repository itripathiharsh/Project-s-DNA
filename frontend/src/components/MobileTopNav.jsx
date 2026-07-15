import { NavLink, useNavigate } from 'react-router-dom';

const ITEMS = [
  { to: '/dashboard', icon: 'dashboard' },
  { to: '/explorer', icon: 'folder_open' },
  { to: '/graph', icon: 'account_tree' },
  { to: '/intelligence', icon: 'psychology' },
  { to: '/risk', icon: 'security' },
  { to: '/knowledge', icon: 'menu_book' },
  { to: '/evolution', icon: 'query_stats' },
  { to: '/settings', icon: 'settings' },
];

export default function MobileTopNav() {
  const navigate = useNavigate();
  return (
    <nav className="md:hidden bg-surface-container-low border-b border-border-subtle fixed top-0 w-full h-row-height-standard flex justify-between items-center px-gutter z-50">
      <button onClick={() => navigate('/')} className="font-headline-md text-headline-md font-bold text-on-surface">
        Project DNA
      </button>
      <div className="flex items-center gap-2">
        {ITEMS.slice(0, 6).map((i) => (
          <NavLink key={i.to} to={i.to} className="p-1.5 rounded hover:bg-surface-container">
            <span className="material-symbols-outlined text-[20px] text-on-surface-variant">{i.icon}</span>
          </NavLink>
        ))}
        <NavLink to="/settings" className="p-1.5 rounded hover:bg-surface-container">
          <span className="material-symbols-outlined text-[20px] text-on-surface-variant">settings</span>
        </NavLink>
      </div>
    </nav>
  );
}
