import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAnalysis } from '../../store/analysis';

export default function ConfigureAnalysis() {
  const [ruleset, setRuleset] = useState('clean');
  const [includePatterns, setIncludePatterns] = useState(['src/**/*.ts', 'src/**/*.tsx', 'lib/internal/core/**/*']);
  const [excludePatterns, setExcludePatterns] = useState(['**/node_modules/**', '**/*.test.ts', '**/*.spec.ts', 'dist/**']);
  const navigate = useNavigate();
  const { repoPath } = useAnalysis();

  const RULESETS = [
    { id: 'clean', name: 'Clean Architecture', desc: 'Strict layer separation (Domain, App, Infrastructure).' },
    { id: 'micro', name: 'Microservices', desc: 'High-density boundary validation for service decoupling.' },
    { id: 'mono', name: 'Modular Monolith', desc: 'Internal module encapsulation and public API enforcement.' },
  ];

  return (
    <div className="min-h-screen bg-background text-on-surface font-body-md text-body-md">
      <header className="bg-background border-b border-border-subtle flex justify-between items-center px-gutter w-full h-row-height-standard fixed top-0 z-50">
        <div className="flex items-center gap-4">
          <span className="font-headline-md text-headline-md font-bold text-on-surface">Project DNA</span>
        </div>
        <div className="flex items-center gap-3">
          <span className="material-symbols-outlined text-on-surface-variant cursor-pointer hover:bg-surface-container p-1">notifications</span>
          <span className="material-symbols-outlined text-on-surface-variant cursor-pointer hover:bg-surface-container p-1">help</span>
          <span className="material-symbols-outlined text-on-surface-variant cursor-pointer hover:bg-surface-container p-1">settings</span>
        </div>
      </header>

      <main className="pt-row-height-standard flex min-h-screen">
        <section className="flex-grow p-8 flex flex-col items-center">
          <div className="max-w-5xl w-full">
            <div className="mb-10 text-center">
              <h1 className="font-headline-lg text-headline-lg mb-2">Configure Analysis Pipeline</h1>
              <p className="text-on-surface-variant max-w-2xl mx-auto">
                Fine-tune how Project DNA interprets your codebase. Define your architectural boundaries and scanning rules for{' '}
                <code className="bg-surface-container-highest px-1.5 py-0.5 rounded text-primary font-code-sm">{repoPath || 'your repository'}</code>.
              </p>
            </div>

            <div className="flex justify-center mb-12">
              <div className="flex items-center w-full max-w-md">
                {['Connect', 'Configure', 'Analyze'].map((s, i) => (
                  <div key={s} className="relative flex flex-col items-center flex-1">
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center font-bold mb-2 ${i < 1 ? 'bg-signal-emerald text-background' : i === 1 ? 'bg-primary text-on-primary ring-4 ring-primary/20' : 'bg-surface-container-highest text-on-surface-variant'}`}>
                      {i < 1 ? <span className="material-symbols-outlined text-[18px]">check</span> : i + 1}
                    </div>
                    <span className={`text-[11px] font-bold uppercase tracking-widest ${i === 1 ? 'text-primary' : 'text-on-surface-variant'}`}>{s}</span>
                    {i < 2 && <div className={`flex-grow h-[2px] ${i < 1 ? 'bg-primary' : 'bg-surface-container-highest'} mb-6`} />}
                  </div>
                ))}
              </div>
            </div>

            <div className="grid grid-cols-12 gap-6">
              <div className="col-span-12 lg:col-span-4 flex flex-col gap-6">
                <div className="bg-surface-container-low border border-border-subtle p-5 rounded-lg">
                  <div className="flex items-center gap-2 mb-4">
                    <span className="material-symbols-outlined text-primary">source</span>
                    <h3 className="font-headline-md text-headline-md">Source Context</h3>
                  </div>
                  <div className="space-y-4">
                    <div>
                      <label className="block font-label-caps text-label-caps text-text-muted mb-2">Target Branch</label>
                      <select className="input-base cursor-pointer">
                        <option>main</option><option>develop</option><option>staging</option><option>release/v2.4</option>
                      </select>
                    </div>
                    <div className="p-3 bg-surface-container rounded border border-border-subtle">
                      <div className="flex items-center justify-between mb-1">
                        <span className="font-label-caps text-label-caps text-text-muted">Repository Stats</span>
                        <span className="material-symbols-outlined text-signal-cyan text-[16px]">info</span>
                      </div>
                      <div className="flex justify-between items-end">
                        <span className="text-headline-md font-code-md">—</span>
                        <span className="text-[10px] text-on-surface-variant">LOC Scan Est.</span>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="bg-surface-container-low border border-border-subtle p-5 rounded-lg">
                  <div className="flex items-center gap-2 mb-4">
                    <span className="material-symbols-outlined text-primary">gavel</span>
                    <h3 className="font-headline-md text-headline-md">Architecture Model</h3>
                  </div>
                  <div className="space-y-2">
                    {RULESETS.map((r) => (
                      <label
                        key={r.id}
                        className={`flex items-start gap-3 p-3 cursor-pointer rounded transition-all border ${ruleset === r.id ? 'bg-surface-container-highest border-l-2 border-primary' : 'hover:bg-surface-container border-transparent'}`}
                      >
                        <input type="radio" name="ruleset" checked={ruleset === r.id} onChange={() => setRuleset(r.id)} className="mt-1 text-primary focus:ring-0 bg-transparent border-border-subtle" />
                        <span>
                          <span className="font-body-sm font-bold text-on-surface">{r.name}</span>
                          <span className="block text-[11px] text-on-surface-variant">{r.desc}</span>
                        </span>
                      </label>
                    ))}
                  </div>
                </div>
              </div>

              <div className="col-span-12 lg:col-span-8">
                <div className="bg-surface-container-low border border-border-subtle rounded-lg flex flex-col h-full overflow-hidden">
                  <div className="flex items-center justify-between px-5 py-4 border-b border-border-subtle">
                    <div className="flex items-center gap-2">
                      <span className="material-symbols-outlined text-primary">filter_alt</span>
                      <h3 className="font-headline-md text-headline-md">Filter Configuration</h3>
                    </div>
                  </div>
                  <div className="flex-grow grid grid-cols-1 md:grid-cols-2 min-h-[400px]">
                    <div className="border-b md:border-b-0 md:border-r border-border-subtle flex flex-col">
                      <div className="p-4 border-b border-border-subtle flex justify-between items-center">
                        <span className="font-label-caps text-label-caps text-signal-emerald flex items-center gap-1">
                          <span className="material-symbols-outlined text-[14px]">add_circle</span> Include Patterns
                        </span>
                      </div>
                      <div className="flex-grow bg-[#050505] p-4 font-code-sm text-code-sm leading-6">
                        {includePatterns.map((p, i) => (
                          <div key={i} className="flex gap-4">
                            <div className="text-text-muted/40 select-none text-right w-6">{i + 1}</div>
                            <div className="text-signal-emerald">{p}</div>
                          </div>
                        ))}
                      </div>
                    </div>
                    <div className="flex flex-col">
                      <div className="p-4 border-b border-border-subtle flex justify-between items-center">
                        <span className="font-label-caps text-label-caps text-signal-rose flex items-center gap-1">
                          <span className="material-symbols-outlined text-[14px]">remove_circle</span> Exclude Patterns
                        </span>
                      </div>
                      <div className="flex-grow bg-[#050505] p-4 font-code-sm text-code-sm leading-6">
                        {excludePatterns.map((p, i) => (
                          <div key={i} className="flex gap-4">
                            <div className="text-text-muted/40 select-none text-right w-6">{i + 1}</div>
                            <div className="text-signal-rose">{p}</div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                  <div className="bg-surface-container px-4 py-2 border-t border-border-subtle flex justify-between items-center text-[11px] text-on-surface-variant font-code-sm">
                    <div className="flex gap-4"><span>UTF-8</span><span>Glob Syntax</span></div>
                    <div className="flex gap-4 opacity-50"><span>Configure via .dnaignore</span></div>
                  </div>
                </div>
              </div>
            </div>

            <div className="mt-12 flex justify-between items-center pt-6 border-t border-border-subtle">
              <button onClick={() => navigate('/onboarding')} className="flex items-center gap-2 px-6 py-2.5 rounded border border-border-subtle hover:bg-surface-container transition-colors text-on-surface font-bold">
                <span className="material-symbols-outlined">arrow_back</span> Back
              </button>
              <div className="flex gap-4">
                <button
                  onClick={() => navigate('/onboarding/analyze')}
                  className="bg-primary text-on-primary px-10 py-2.5 rounded font-bold hover:opacity-90 transition-all flex items-center gap-2"
                >
                  Start Analysis <span className="material-symbols-outlined">arrow_forward</span>
                </button>
              </div>
            </div>
          </div>
        </section>

        <aside className="hidden xl:flex flex-col h-[calc(100vh-36px)] w-inspector-width bg-surface-container-low border-l border-border-subtle fixed right-0 top-row-height-standard overflow-y-auto">
          <div className="p-gutter border-b border-border-subtle">
            <h4 className="font-label-caps text-label-caps text-text-muted mb-4 uppercase tracking-widest">Selected Ruleset Details</h4>
            <div className="p-4 bg-surface-container-highest rounded border border-border-subtle">
              <div className="text-primary font-bold mb-1">{RULESETS.find((r) => r.id === ruleset)?.name}</div>
              <p className="text-body-sm text-body-sm text-on-surface-variant mb-4">{RULESETS.find((r) => r.id === ruleset)?.desc}</p>
            </div>
          </div>
        </aside>
      </main>
    </div>
  );
}
