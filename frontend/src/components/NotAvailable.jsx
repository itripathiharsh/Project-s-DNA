// Honest "not available" placeholder for screens whose backend API does not exist yet.
// No mock/fake data is rendered; controls are clearly disabled.
export default function NotAvailable({ title, icon = 'cloud_off', description, route }) {
  return (
    <div className="flex-1 flex flex-col items-center justify-center px-6 py-20 text-center">
      <div className="w-20 h-20 rounded-full bg-surface-container-high border border-border-subtle flex items-center justify-center mb-6">
        <span className="material-symbols-outlined text-[40px] text-on-surface-variant">{icon}</span>
      </div>
      <h2 className="font-headline-lg text-headline-lg text-on-surface mb-2">{title}</h2>
      <p className="text-on-surface-variant font-body-md max-w-md mb-1">
        {description || 'This module is part of the unified Project DNA experience but is not connected to a backend data source yet.'}
      </p>
      <p className="font-code-sm text-code-sm text-text-muted mb-8">
        Navigation is live — no placeholder or fabricated data is shown.
      </p>
      <div className="flex flex-col gap-2 w-full max-w-xs opacity-60 pointer-events-none select-none">
        <div className="btn-primary">
          <span className="material-symbols-outlined text-[16px]">lock</span>
          Requires backend integration
        </div>
      </div>
    </div>
  );
}
