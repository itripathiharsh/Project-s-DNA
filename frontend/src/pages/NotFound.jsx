import { useNavigate } from 'react-router-dom';

export default function NotFound() {
  const navigate = useNavigate();

  return (
    <div className="flex-1 flex flex-col items-center justify-center px-6 py-20 text-center">
      <div className="w-20 h-20 rounded-full bg-surface-container-high border border-border-subtle flex items-center justify-center mb-6">
        <span className="material-symbols-outlined text-[40px] text-on-surface-variant">explore_off</span>
      </div>
      <h1 className="font-display-xl text-display-xl text-on-surface mb-2">404</h1>
      <h2 className="font-headline-lg text-headline-lg text-on-surface mb-2">Page not found</h2>
      <p className="text-on-surface-variant font-body-md max-w-md mb-8">
        This route does not exist in the current application. The path may have been removed or the URL may be incorrect.
      </p>
      <div className="flex flex-col sm:flex-row gap-3">
        <button onClick={() => navigate('/')} className="btn-secondary">
          <span className="material-symbols-outlined text-[16px]">home</span>
          Return Home
        </button>
        <button onClick={() => navigate('/dashboard')} className="btn-primary">
          <span className="material-symbols-outlined text-[16px]">dashboard</span>
          Repository Dashboard
        </button>
      </div>
    </div>
  );
}
