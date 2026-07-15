import { useState, useEffect } from 'react';
import PageHeader from '../components/PageHeader';
import { getSettings, saveSettings } from '../services/api';

export default function Settings() {
  const [settings, setSettings] = useState({
    max_file_size_mb: '1',
    log_level: 'INFO',
    theme: 'dark',
    network_mode: 'false',
    auto_analysis: 'true',
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const [saveStatus, setSaveStatus] = useState(null); // 'success' or 'failed'

  useEffect(() => {
    async function loadSettings() {
      try {
        const data = await getSettings();
        setSettings((prev) => ({ ...prev, ...data }));
      } catch (err) {
        setError(err.message || String(err));
      } finally {
        setLoading(false);
      }
    }
    loadSettings();
  }, []);

  const handleToggle = (key) => {
    setSettings((prev) => ({
      ...prev,
      [key]: prev[key] === 'true' ? 'false' : 'true',
    }));
  };

  const handleChange = (key, val) => {
    setSettings((prev) => ({
      ...prev,
      [key]: val,
    }));
  };

  const handleSave = async (e) => {
    if (e) e.preventDefault();
    setSaving(true);
    setSaveStatus(null);
    try {
      await saveSettings(settings);
      setSaveStatus('success');
      setTimeout(() => setSaveStatus(null), 3500);
    } catch (err) {
      setSaveStatus('failed');
      setTimeout(() => setSaveStatus(null), 5000);
    } finally {
      setSaving(false);
    }
  };

  const TOGGLES = [
    { key: 'auto_analysis', label: 'Auto Analysis', desc: 'Trigger analysis automatically on repository select', icon: 'sync' },
    { key: 'network_mode', label: 'Network Mode', desc: 'Enable API key authentication for external clients', icon: 'language' },
  ];

  return (
    <>
      <PageHeader
        title="Settings"
        subtitle="Analysis configuration & engines"
        actions={
          <button onClick={handleSave} disabled={saving || loading} className="btn-primary px-4 py-2 text-xs flex items-center gap-1.5 hover:scale-[1.02] active:scale-[0.98] transition-all">
            <span className="material-symbols-outlined text-[15px]">save</span>
            <span>{saving ? 'Saving...' : 'Save Settings'}</span>
          </button>
        }
      />
      
      <div className="p-6 flex flex-col gap-6 max-w-[900px] mx-auto w-full font-sans text-xs">
        {loading ? (
          <div className="flex justify-center items-center py-20">
            <div className="w-10 h-10 border-2 border-primary/20 border-t-primary rounded-full animate-spin" />
          </div>
        ) : error ? (
          <div className="text-signal-rose card-base p-5 border border-signal-rose/30 bg-signal-rose/5 text-xs font-semibold">{error}</div>
        ) : (
          <form onSubmit={handleSave} className="space-y-6">
            {/* Persist Alerts */}
            {saveStatus === 'success' && (
              <div className="flex items-center gap-2 p-3 bg-[#0d2218] border border-signal-emerald/30 text-signal-emerald rounded-xl animate-fade-in shadow-lg">
                <span className="material-symbols-outlined text-[16px] animate-pulse">check_circle</span>
                <span className="font-semibold">Configuration successfully saved and persisted to SQLite storage database.</span>
              </div>
            )}
            
            {saveStatus === 'failed' && (
              <div className="flex items-center gap-2 p-3 bg-signal-rose/10 border border-signal-rose/30 text-signal-rose rounded-xl animate-fade-in shadow-lg">
                <span className="material-symbols-outlined text-[16px]">error</span>
                <span className="font-semibold">Failed to persist configuration settings. Check backend process logs.</span>
              </div>
            )}

            {/* General Settings */}
            <div className="card-base bg-surface-container/30 border border-border-subtle p-5 shadow-xl space-y-4">
              <h3 className="font-bold text-xs text-on-surface uppercase tracking-wider pb-2 border-b border-border-subtle/50 flex items-center gap-1.5">
                <span className="material-symbols-outlined text-primary text-[18px]">tune</span> 
                <span>Engine Parameters</span>
              </h3>
              
              <div className="space-y-4">
                <div className="flex flex-col gap-1.5">
                  <label className="text-[10px] text-text-muted font-bold uppercase tracking-wider">Maximum File Size Limit (MB)</label>
                  <input
                    type="number"
                    min="1"
                    max="100"
                    value={settings.max_file_size_mb}
                    onChange={(e) => handleChange('max_file_size_mb', e.target.value)}
                    className="input-base"
                  />
                  <span className="text-[10px] text-text-muted opacity-85 leading-relaxed">
                    Source modules exceeding this payload size are skipped during compiler cycles to maintain index response speeds.
                  </span>
                </div>

                <div className="flex flex-col gap-1.5">
                  <label className="text-[10px] text-text-muted font-bold uppercase tracking-wider">Logging Verbosity Level</label>
                  <select
                    value={settings.log_level}
                    onChange={(e) => handleChange('log_level', e.target.value)}
                    className="input-base bg-surface-container-low"
                  >
                    <option value="DEBUG">DEBUG (Detailed AST tracing logs)</option>
                    <option value="INFO">INFO (Normal operational messages)</option>
                    <option value="WARNING">WARNING (Issues and recovery warnings)</option>
                    <option value="ERROR">ERROR (Terminal processing failures)</option>
                  </select>
                </div>

                <div className="flex flex-col gap-1.5">
                  <label className="text-[10px] text-text-muted font-bold uppercase tracking-wider">Application Theme</label>
                  <select
                    value={settings.theme}
                    onChange={(e) => handleChange('theme', e.target.value)}
                    className="input-base bg-surface-container-low"
                  >
                    <option value="dark">Dark Theme (Standard)</option>
                    <option value="light">Light Theme (Accessibility)</option>
                  </select>
                </div>
              </div>
            </div>

            {/* Feature Toggles */}
            <div className="card-base bg-surface-container/30 border border-border-subtle p-5 shadow-xl space-y-4">
              <h3 className="font-bold text-xs text-on-surface uppercase tracking-wider pb-2 border-b border-border-subtle/50 flex items-center gap-1.5">
                <span className="material-symbols-outlined text-primary text-[18px]">toggle_on</span> 
                <span>Feature Controls</span>
              </h3>
              
              <div className="space-y-3">
                {TOGGLES.map((t) => (
                  <div 
                    key={t.key} 
                    className="flex items-center justify-between p-3.5 rounded-xl bg-surface-container-low/40 border border-border-subtle/80 hover:border-outline/25 transition-all duration-200"
                  >
                    <div className="flex items-center gap-3">
                      <span className="material-symbols-outlined text-on-surface-variant text-[18px]">{t.icon}</span>
                      <div>
                        <div className="font-semibold text-xs text-on-surface leading-tight">{t.label}</div>
                        <div className="text-[10px] text-text-muted mt-0.5 leading-relaxed">{t.desc}</div>
                      </div>
                    </div>
                    
                    <label className="relative inline-flex items-center cursor-pointer select-none">
                      <input
                        type="checkbox"
                        checked={settings[t.key] === 'true'}
                        onChange={() => handleToggle(t.key)}
                        className="sr-only peer"
                      />
                      <div className="w-10 h-5 bg-surface-container-highest rounded-full peer-checked:bg-primary transition-colors border border-border-subtle peer-checked:border-primary" />
                      <div className="absolute left-0.5 top-0.5 w-4 h-4 bg-on-surface rounded-full transition-transform peer-checked:translate-x-5 shadow" />
                    </label>
                  </div>
                ))}
              </div>
            </div>
          </form>
        )}
      </div>
    </>
  );
}
