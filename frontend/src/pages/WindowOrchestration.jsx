import { useState, useEffect } from 'react';
import PageHeader from '../components/PageHeader';
import { getSettings, saveSettings } from '../services/api';

export default function WindowOrchestration() {
  const [layout, setLayout] = useState('split');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function loadLayout() {
      try {
        const settings = await getSettings();
        if (settings.layout_grid_orchestration) {
          setLayout(settings.layout_grid_orchestration);
        }
      } catch (err) {
        setError(err.message || String(err));
      } finally {
        setLoading(false);
      }
    }
    loadLayout();
  }, []);

  const handleSaveLayout = async (selectedLayout) => {
    try {
      setLayout(selectedLayout);
      await saveSettings({
        layout_grid_orchestration: selectedLayout
      });
      alert(`Workspace layout '${selectedLayout}' successfully saved to database configuration.`);
    } catch (err) {
      alert('Failed to save layout: ' + err.message);
    }
  };

  const LAYOUTS = [
    { id: 'focus', name: 'Focus Mode', desc: 'Single panel maximized for high-priority inspection', icon: 'fullscreen' },
    { id: 'split', name: 'Split Panel', desc: 'Side-by-side split screen for file and AST compare', icon: 'splitscreen' },
    { id: 'triple', name: 'Triple Column', desc: 'Three panels showing Explorer, Code, and Graph details', icon: 'view_column' },
    { id: 'grid', name: 'Quad Grid', desc: 'Four equal tiles for comprehensive telemetry', icon: 'grid_view' },
  ];

  return (
    <>
      <PageHeader title="Window Layout Orchestration" subtitle="Configure and persist the multi-pane panel layout config" />
      <div className="p-6 flex flex-col gap-6 max-w-4xl font-body-sm">
        {loading ? (
          <div className="flex justify-center items-center py-16">
            <div className="w-10 h-10 border-4 border-surface-container-high border-t-primary rounded-full animate-spin" />
          </div>
        ) : error ? (
          <div className="text-signal-rose card-base">{error}</div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {LAYOUTS.map((lay) => {
              const isSelected = layout === lay.id;
              return (
                <div
                  key={lay.id}
                  onClick={() => handleSaveLayout(lay.id)}
                  className={`card-base flex flex-col justify-between cursor-pointer transition-all border ${
                    isSelected ? 'border-primary bg-primary/10' : 'border-border-subtle hover:bg-surface-container-high'
                  }`}
                >
                  <div className="flex items-start gap-4 mb-4">
                    <div className={`p-3 rounded-lg border ${isSelected ? 'bg-primary/20 border-primary/30' : 'bg-surface-container-high border-border-subtle'}`}>
                      <span className="material-symbols-outlined text-[24px] text-primary">{lay.icon}</span>
                    </div>
                    <div>
                      <h4 className="font-headline-md text-headline-md font-bold text-on-surface mb-1">{lay.name}</h4>
                      <p className="text-xs text-text-muted leading-relaxed">{lay.desc}</p>
                    </div>
                  </div>

                  <div className="flex items-center justify-between border-t border-border-subtle/50 pt-3">
                    <span className="text-[10px] text-text-muted font-bold uppercase">PERSISTED IN SQLite</span>
                    {isSelected ? (
                      <span className="badge badge-ok text-[10px] flex items-center gap-1">
                        <span className="material-symbols-outlined text-[10px]">check</span> Active Layout
                      </span>
                    ) : (
                      <span className="text-[10px] text-primary hover:underline">Select & Save</span>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </>
  );
}
