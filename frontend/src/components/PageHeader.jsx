export default function PageHeader({ title, subtitle, actions }) {
  return (
    <header className="px-6 py-5 flex flex-wrap justify-between items-center gap-3 border-b border-border-subtle/50 sticky top-0 bg-[#09090e]/75 backdrop-blur-xl z-30">
      <div className="flex flex-col gap-0.5">
        <div className="flex items-center gap-1 text-[10px] font-bold text-text-muted uppercase tracking-widest">
          <span>Project DNA</span>
          <span className="material-symbols-outlined text-[11px]">chevron_right</span>
          <span className="text-primary/95">{title}</span>
        </div>
        <h1 className="font-extrabold text-[20px] text-on-surface tracking-tight leading-tight mt-1">{title}</h1>
        {subtitle && (
          <div className="mt-1 text-[11px] text-on-surface-variant font-medium font-code-sm bg-[#161625]/40 px-2.5 py-1 border border-border-subtle rounded-lg flex items-center gap-1.5 w-max shadow-inner">
            <span className="w-1.5 h-1.5 rounded-full bg-primary/70 animate-pulse" />
            {subtitle}
          </div>
        )}
      </div>
      {actions && <div className="flex items-center gap-2">{actions}</div>}
    </header>
  );
}
