import { useState, useEffect } from 'react';
import { getSecurityHeatmap } from '../services/api';
import PageHeader from '../components/PageHeader';

export default function SecurityHeatmap() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [severityFilter, setSeverityFilter] = useState('all'); // all, critical, high, medium, low
  const [selectedFinding, setSelectedFinding] = useState(null);

  useEffect(() => {
    async function fetchData() {
      try {
        setLoading(true);
        const result = await getSecurityHeatmap();
        setData(result);
        if (result.findings && result.findings.length > 0) {
          setSelectedFinding(result.findings[0]);
        }
      } catch (err) {
        console.error('Error fetching security heatmap:', err);
        setError(err.message || 'Failed to fetch security metrics.');
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  const getSeverityBadgeClass = (severity) => {
    const sev = severity.toLowerCase();
    if (sev === 'critical') return 'badge-high border border-signal-rose/30 text-signal-rose bg-signal-rose/10 animate-pulse';
    if (sev === 'high') return 'badge-high text-signal-rose bg-signal-rose/10';
    if (sev === 'medium') return 'badge-warn text-signal-amber bg-signal-amber/10';
    return 'badge-low text-signal-cyan bg-signal-cyan/10';
  };

  const getSeverityColor = (severity) => {
    const sev = severity.toLowerCase();
    if (sev === 'critical' || sev === 'high') return '#ff007f';
    if (sev === 'medium') return '#eab308';
    return '#00bbf9';
  };

  if (loading) {
    return (
      <div className="flex-1 flex items-center justify-center p-12">
        <div className="flex flex-col items-center gap-3">
          <span className="material-symbols-outlined text-[36px] text-primary animate-spin">sync</span>
          <span className="text-xs text-text-muted">Scanning repository file context for security threats...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center p-12 text-center max-w-md mx-auto">
        <span className="material-symbols-outlined text-[48px] text-signal-rose mb-3">error</span>
        <h3 className="font-bold text-base text-on-surface">Analysis Error</h3>
        <p className="text-xs text-text-muted mt-2">{error}</p>
      </div>
    );
  }

  const findings = data?.findings || [];
  const criticalCount = findings.filter(f => f.severity.toLowerCase() === 'critical').length;
  const highCount = findings.filter(f => f.severity.toLowerCase() === 'high').length;
  const mediumCount = findings.filter(f => f.severity.toLowerCase() === 'medium').length;
  const lowCount = findings.filter(f => f.severity.toLowerCase() === 'low').length;

  const filteredFindings = findings.filter(f => 
    severityFilter === 'all' || f.severity.toLowerCase() === severityFilter.toLowerCase()
  );

  // Group findings by file for the matrix
  const fileGroups = {};
  findings.forEach(f => {
    if (!fileGroups[f.file_path]) {
      fileGroups[f.file_path] = {
        file_path: f.file_path,
        max_severity: f.severity,
        count: 0
      };
    }
    fileGroups[f.file_path].count++;
    
    // Upgrade max severity if needed
    const levels = { 'critical': 4, 'high': 3, 'medium': 2, 'low': 1 };
    const currentMax = levels[fileGroups[f.file_path].max_severity.toLowerCase()] || 0;
    const itemSev = levels[f.severity.toLowerCase()] || 0;
    if (itemSev > currentMax) {
      fileGroups[f.file_path].max_severity = f.severity;
    }
  });

  const fileVulnerabilityList = Object.values(fileGroups);

  return (
    <>
      <PageHeader 
        title="Security & Risk Heatmap" 
        subtitle="Static vulnerability detection, dependency scanning, and secret leak assessment" 
      />
      <div className="p-6 flex flex-col gap-6 max-w-[1600px] mx-auto w-full flex-1">
        
        {/* Severity Metrics Row */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
          <div className="card-base border-l-4 border-l-signal-rose flex items-center justify-between py-4">
            <div>
              <span className="text-[9px] text-text-muted uppercase tracking-wider font-bold">Critical severity</span>
              <span className="text-xl font-extrabold text-on-surface block mt-1">{criticalCount}</span>
            </div>
            <span className="material-symbols-outlined text-signal-rose/70 text-[28px]">gpp_maybe</span>
          </div>

          <div className="card-base border-l-4 border-l-signal-rose flex items-center justify-between py-4">
            <div>
              <span className="text-[9px] text-text-muted uppercase tracking-wider font-bold">High severity</span>
              <span className="text-xl font-extrabold text-on-surface block mt-1">{highCount}</span>
            </div>
            <span className="material-symbols-outlined text-signal-rose/70 text-[28px]">warning</span>
          </div>

          <div className="card-base border-l-4 border-l-signal-amber flex items-center justify-between py-4">
            <div>
              <span className="text-[9px] text-text-muted uppercase tracking-wider font-bold">Medium severity</span>
              <span className="text-xl font-extrabold text-on-surface block mt-1">{mediumCount}</span>
            </div>
            <span className="material-symbols-outlined text-signal-amber/70 text-[28px]">security_update_warning</span>
          </div>

          <div className="card-base border-l-4 border-l-signal-cyan flex items-center justify-between py-4">
            <div>
              <span className="text-[9px] text-text-muted uppercase tracking-wider font-bold">Low severity</span>
              <span className="text-xl font-extrabold text-on-surface block mt-1">{lowCount}</span>
            </div>
            <span className="material-symbols-outlined text-signal-cyan/70 text-[28px]">info</span>
          </div>
        </div>

        {/* Lower Workspaces Layout */}
        <div className="flex flex-col lg:flex-row gap-6 w-full flex-1">
          {/* Main Visual Matrix & Findings List */}
          <div className="flex-1 flex flex-col gap-6 min-w-0">
            {/* Heatmap Matrix */}
            <div className="card-base flex flex-col min-h-[220px]">
              <div className="border-b border-border-subtle/50 pb-3 mb-4">
                <h3 className="font-bold text-xs uppercase text-text-muted tracking-wider">Vulnerable Files Grid ({fileVulnerabilityList.length})</h3>
                <p className="text-[10px] text-text-muted mt-0.5">Files containing security alerts. Color mapped to maximum severity.</p>
              </div>

              <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 xl:grid-cols-5 gap-3 overflow-y-auto max-h-[220px] pr-1">
                {fileVulnerabilityList.map((file, i) => {
                  const severityColor = getSeverityColor(file.max_severity);
                  return (
                    <div
                      key={i}
                      style={{ 
                        backgroundColor: `${severityColor}15`,
                        borderColor: severityColor,
                        color: severityColor
                      }}
                      className="p-3.5 rounded-lg border flex flex-col justify-between h-20 relative overflow-hidden"
                    >
                      <div className="absolute left-0 top-0 bottom-0 w-1" style={{ backgroundColor: severityColor }} />

                      <div className="text-[10px] font-mono truncate leading-none pl-1 text-on-surface font-semibold" title={file.file_path}>
                        {file.file_path.split('/').pop()}
                      </div>
                      <div className="flex justify-between items-end mt-2 pl-1">
                        <span className="text-[9px] font-extrabold uppercase tracking-wider text-text-muted">
                          {file.max_severity}
                        </span>
                        <span className="font-extrabold text-xs text-on-surface">
                          {file.count} {file.count > 1 ? 'findings' : 'finding'}
                        </span>
                      </div>
                    </div>
                  );
                })}
                {fileVulnerabilityList.length === 0 && (
                  <div className="col-span-full py-10 text-center text-signal-emerald text-xs font-semibold flex items-center justify-center gap-2">
                    <span className="material-symbols-outlined text-[18px]">verified</span>
                    No security threats or vulnerable files identified in repository.
                  </div>
                )}
              </div>
            </div>

            {/* Findings List */}
            <div className="card-base flex-1 flex flex-col min-h-[300px]">
              <div className="border-b border-border-subtle/50 pb-3 mb-4 flex items-center justify-between flex-wrap gap-3">
                <div>
                  <h3 className="font-bold text-xs uppercase text-text-muted tracking-wider">Identified Security Alerts</h3>
                  <p className="text-[10px] text-text-muted mt-0.5">Filter alerts by target severity level below.</p>
                </div>

                <div className="flex items-center gap-1.5 bg-[#12121e] border border-border-subtle rounded-lg p-1">
                  {[
                    { id: 'all', label: 'All Alerts' },
                    { id: 'critical', label: 'Critical' },
                    { id: 'high', label: 'High' },
                    { id: 'medium', label: 'Medium' },
                    { id: 'low', label: 'Low' },
                  ].map((s) => (
                    <button
                      key={s.id}
                      onClick={() => setSeverityFilter(s.id)}
                      className={`px-3 py-1 rounded-md text-[10px] font-bold uppercase transition-all duration-200 ${severityFilter === s.id ? 'bg-primary text-white shadow-md' : 'text-text-muted hover:text-on-surface'}`}
                    >
                      {s.label}
                    </button>
                  ))}
                </div>
              </div>

              <div className="space-y-2 overflow-y-auto max-h-[350px] pr-1">
                {filteredFindings.map((finding, i) => {
                  const active = selectedFinding?.file_path === finding.file_path && selectedFinding?.line === finding.line && selectedFinding?.evidence === finding.evidence;
                  return (
                    <div
                      key={i}
                      onClick={() => setSelectedFinding(finding)}
                      className={`p-3 rounded-lg border transition-all duration-200 cursor-pointer flex items-start gap-3 hover:bg-surface-container-high/20 ${active ? 'bg-primary/10 border-primary/30' : 'bg-surface-container-low/40 border-border-subtle/40'}`}
                    >
                      <span className={`flex-shrink-0 badge mt-0.5 ${getSeverityBadgeClass(finding.severity)}`}>
                        {finding.severity}
                      </span>

                      <div className="min-w-0 flex-1">
                        <div className="font-bold text-xs text-on-surface capitalize">
                          {finding.finding_type?.replace(/_/g, ' ')}
                        </div>
                        <div className="text-[10px] text-text-muted mt-1 truncate" title={finding.file_path}>
                          in: <span className="font-mono text-primary/80">{finding.file_path}:{finding.line}</span>
                        </div>
                        <div className="text-[11px] text-on-surface-variant leading-relaxed mt-1.5 line-clamp-2">
                          {finding.description}
                        </div>
                      </div>

                      <span className="material-symbols-outlined text-text-muted select-none text-[16px] shrink-0 mt-0.5">
                        {active ? 'keyboard_arrow_right' : 'chevron_right'}
                      </span>
                    </div>
                  );
                })}
                {filteredFindings.length === 0 && (
                  <div className="py-16 text-center text-text-muted text-xs">No alerts matching your severity filter.</div>
                )}
              </div>
            </div>
          </div>

          {/* Drill-down Right Sidebar Panel */}
          <div className="w-full lg:w-[400px] shrink-0">
            <div className="card-base sticky top-24 flex flex-col gap-5">
              <div className="border-b border-border-subtle/50 pb-3 flex items-center gap-2">
                <span className="material-symbols-outlined text-primary text-[20px]">policy</span>
                <div>
                  <h3 className="font-bold text-xs uppercase tracking-wider text-on-surface">Vulnerability Details</h3>
                  <p className="text-[10px] text-text-muted">Security advisory profile</p>
                </div>
              </div>

              {selectedFinding ? (
                <div className="flex flex-col gap-4 text-xs">
                  {/* Alert summary block */}
                  <div className="bg-[#12121e] border border-border-subtle rounded-lg p-3">
                    <div className="flex justify-between items-center mb-1.5">
                      <span className="text-[9px] font-bold text-primary uppercase tracking-widest">Finding Type</span>
                      <span className={`badge ${getSeverityBadgeClass(selectedFinding.severity)}`}>
                        {selectedFinding.severity}
                      </span>
                    </div>
                    <div className="font-bold text-xs text-on-surface capitalize">
                      {selectedFinding.finding_type?.replace(/_/g, ' ')}
                    </div>
                    <div className="font-mono text-[10px] text-text-muted break-all mt-2.5">
                      File: {selectedFinding.file_path}:{selectedFinding.line}
                    </div>
                  </div>

                  {/* Impact and Description */}
                  <div className="flex flex-col gap-1.5">
                    <span className="text-[9px] font-bold text-text-muted uppercase tracking-widest block">Threat Description</span>
                    <p className="text-on-surface-variant leading-relaxed text-[11px]">
                      {selectedFinding.description}
                    </p>
                  </div>

                  {/* Code Evidence snippet */}
                  <div className="flex flex-col gap-1.5">
                    <span className="text-[9px] font-bold text-text-muted uppercase tracking-widest block">Code Evidence Match</span>
                    <div className="p-3 bg-[#07070c] border border-border-subtle rounded-lg">
                      <code className="font-mono text-[10px] text-[#f8961e] block break-all font-semibold whitespace-pre-wrap">
                        {selectedFinding.evidence}
                      </code>
                    </div>
                  </div>

                  {/* Remediation Plan */}
                  <div className="flex flex-col gap-1.5 border-t border-border-subtle/50 pt-3.5">
                    <span className="text-[9px] font-bold text-primary uppercase tracking-widest block">Remediation Action</span>
                    <p className="text-on-surface-variant leading-relaxed text-[11px]">
                      {selectedFinding.finding_type === 'hardcoded_secret' && 'Immediately revoke the credentials, remove them from the source code history using git-filter-repo, and inject them at runtime using environment variables.'}
                      {selectedFinding.finding_type === 'dangerous_api' && 'Avoid dynamic execution strings. Refactor execution targets to use parameterized inputs, safe API interfaces, or sandboxed environments.'}
                      {selectedFinding.finding_type === 'insecure_config' && 'Update the configurations file to use minimum required permissions. Avoid running containers as root and do not commit active credentials in environment files.'}
                      {selectedFinding.finding_type === 'vulnerability' && 'Upgrade the package dependency to a secure patched version as detailed in public vulnerability advisories.'}
                      {!['hardcoded_secret', 'dangerous_api', 'insecure_config', 'vulnerability'].includes(selectedFinding.finding_type) && 'Review the variable definition and logic to prevent potential security leaks or insecure configuration states.'}
                    </p>
                  </div>
                </div>
              ) : (
                <p className="text-xs text-text-muted text-center py-10">Select a security finding to inspect advisory details.</p>
              )}
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
