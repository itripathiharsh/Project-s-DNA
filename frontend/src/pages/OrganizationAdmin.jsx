import { useState, useEffect } from 'react';
import PageHeader from '../components/PageHeader';
import { getTeams, updateTeam, deleteTeam } from '../services/api';

export default function OrganizationAdmin() {
  const [teams, setTeams] = useState([]);
  const [showModal, setShowModal] = useState(false);
  const [teamId, setTeamId] = useState('');
  const [name, setName] = useState('');
  const [role, setRole] = useState('');
  const [membersStr, setMembersStr] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadTeams = async () => {
    try {
      const res = await getTeams();
      setTeams(res.teams || []);
    } catch (err) {
      setError(err.message || String(err));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadTeams();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!name || !role) return;

    try {
      const parsedMembers = membersStr
        .split('\n')
        .map((m) => {
          const parts = m.split(',');
          return {
            name: parts[0]?.trim() || 'New Member',
            role: parts[1]?.trim() || 'Contributor',
            email: parts[2]?.trim() || 'member@company.com'
          };
        })
        .filter((m) => m.name);

      const payload = {
        id: teamId || 'team-' + Math.floor(Math.random() * 10000),
        name,
        role,
        members: parsedMembers.length > 0 ? parsedMembers : [
          { name: 'Alice Johnson', role: 'Lead Architect', email: 'alice@company.com' }
        ]
      };

      await updateTeam(payload);
      setShowModal(false);
      setName('');
      setRole('');
      setMembersStr('');
      setTeamId('');
      await loadTeams();
    } catch (err) {
      alert('Failed to save team: ' + err.message);
    }
  };

  const handleEdit = (team) => {
    setTeamId(team.id);
    setName(team.name);
    setRole(team.role);
    setMembersStr(
      team.members.map((m) => `${m.name}, ${m.role}, ${m.email}`).join('\n')
    );
    setShowModal(true);
  };

  const handleDelete = async (id) => {
    if (!confirm('Are you sure you want to delete this team?')) return;
    try {
      await deleteTeam(id);
      await loadTeams();
    } catch (err) {
      alert('Failed to delete team: ' + err.message);
    }
  };

  const getAvatarColor = (name) => {
    const colors = [
      'bg-primary/20 text-primary border-primary/30',
      'bg-signal-cyan/20 text-signal-cyan border-signal-cyan/30',
      'bg-signal-emerald/20 text-signal-emerald border-signal-emerald/30',
      'bg-signal-amber/20 text-signal-amber border-signal-amber/30',
      'bg-purple-500/20 text-purple-300 border-purple-500/30'
    ];
    let sum = 0;
    for (let i = 0; i < name.length; i++) {
      sum += name.charCodeAt(i);
    }
    return colors[sum % colors.length];
  };

  const getInitials = (name) => {
    return name.split(/[\s_-]/).map(p => p[0]).join('').substring(0, 2).toUpperCase();
  };

  return (
    <>
      <PageHeader
        title="Organization Control"
        subtitle="Manage collaborative engineering teams, roles, and architectural governance permissions"
        actions={
          <button onClick={() => { setTeamId(''); setName(''); setRole(''); setMembersStr(''); setShowModal(true); }} className="btn-primary px-4 py-2 text-xs flex items-center gap-1.5 hover:scale-[1.02] active:scale-[0.98] transition-all">
            <span className="material-symbols-outlined text-[15px]">add</span> Add Team
          </button>
        }
      />
      
      <div className="p-6 flex flex-col gap-6 max-w-[1200px] mx-auto w-full font-sans text-xs">
        {loading ? (
          <div className="flex justify-center items-center py-20">
            <div className="w-10 h-10 border-2 border-primary/20 border-t-primary rounded-full animate-spin" />
          </div>
        ) : error ? (
          <div className="text-signal-rose card-base p-5 border border-signal-rose/30 bg-signal-rose/5 text-xs font-semibold">{error}</div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {teams.map((team) => (
              <div key={team.id} className="card-base flex flex-col justify-between p-5 bg-[#09090e]/60 border border-border-subtle hover:border-primary/30 relative overflow-hidden group">
                <div className="absolute left-0 top-0 bottom-0 w-1 bg-primary" />
                
                <div>
                  <div className="flex items-center justify-between border-b border-border-subtle/50 pb-3 gap-2">
                    <div className="flex flex-col min-w-0">
                      <span className="font-extrabold text-sm text-on-surface truncate group-hover:text-primary transition-colors">{team.name}</span>
                      <span className="text-[10px] text-text-muted mt-0.5 font-medium leading-relaxed truncate">{team.role}</span>
                    </div>
                    
                    <div className="flex items-center gap-1.5 flex-shrink-0">
                      <button onClick={() => handleEdit(team)} className="p-1.5 rounded-lg bg-surface-container hover:bg-surface-container-high border border-border-subtle hover:border-primary/30 text-primary transition-all flex items-center justify-center" title="Edit team">
                        <span className="material-symbols-outlined text-[14px]">edit</span>
                      </button>
                      <button onClick={() => handleDelete(team.id)} className="p-1.5 rounded-lg bg-surface-container hover:bg-surface-container-high border border-border-subtle hover:border-signal-rose/35 text-signal-rose transition-all flex items-center justify-center" title="Delete team">
                        <span className="material-symbols-outlined text-[14px]">delete</span>
                      </button>
                    </div>
                  </div>

                  <div className="space-y-2.5 mt-4">
                    <span className="text-[9px] text-text-muted font-bold uppercase tracking-wider block">Members ({team.members.length})</span>
                    {team.members.map((mem, i) => (
                      <div key={i} className="flex justify-between items-center p-2 rounded-xl bg-surface-container-low/40 border border-border-subtle/60 text-xs hover:border-outline/20 transition-all">
                        <div className="flex items-center gap-2.5 min-w-0">
                          <div className={`w-7 h-7 rounded-lg border flex items-center justify-center font-extrabold text-[8px] ${getAvatarColor(mem.name)} flex-shrink-0`}>
                            {getInitials(mem.name)}
                          </div>
                          <div className="min-w-0">
                            <div className="font-semibold text-on-surface truncate">{mem.name}</div>
                            <div className="text-text-muted text-[10px] truncate">{mem.email}</div>
                          </div>
                        </div>
                        <span className="badge badge-info text-[9px] flex-shrink-0">{mem.role}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Modal Dialog */}
      {showModal && (
        <div className="fixed inset-0 bg-black/85 flex items-center justify-center p-4 z-50 backdrop-blur-md">
          <div className="bg-[#09090e] border border-border-subtle rounded-2xl max-w-lg w-full p-6 flex flex-col gap-4 shadow-2xl animate-fade-in relative">
            <div className="flex justify-between items-center border-b border-border-subtle/50 pb-3">
              <div className="flex items-center gap-2">
                <span className="material-symbols-outlined text-primary">groups</span>
                <h3 className="font-extrabold text-sm text-on-surface uppercase tracking-wider">{teamId ? 'Edit Team Details' : 'Add Engineering Team'}</h3>
              </div>
              <button onClick={() => setShowModal(false)} className="text-on-surface-variant hover:text-on-surface p-1 rounded-lg hover:bg-surface-container-high/40 transition-all">
                <span className="material-symbols-outlined">close</span>
              </button>
            </div>
            
            <form onSubmit={handleSubmit} className="flex flex-col gap-4 font-sans text-xs">
              <div className="flex flex-col gap-1.5">
                <label className="text-[10px] text-text-muted font-bold uppercase tracking-wider">Team Name</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Platform Engineering"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="input-base"
                />
              </div>
              
              <div className="flex flex-col gap-1.5">
                <label className="text-[10px] text-text-muted font-bold uppercase tracking-wider">Role & Governance Focus</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Infrastructure, caching, database boundaries"
                  value={role}
                  onChange={(e) => setRole(e.target.value)}
                  className="input-base"
                />
              </div>

              <div className="flex flex-col gap-1.5">
                <label className="text-[10px] text-text-muted font-bold uppercase tracking-wider">Members (Name, Role, Email - one per line)</label>
                <textarea
                  rows="4"
                  placeholder="Alice Johnson, Tech Lead, alice@company.com&#10;Bob Smith, Dev, bob@company.com"
                  value={membersStr}
                  onChange={(e) => setMembersStr(e.target.value)}
                  className="input-base font-code-sm resize-none"
                />
              </div>
              
              <div className="flex justify-end gap-3 mt-3 pt-3 border-t border-border-subtle/50">
                <button type="button" onClick={() => setShowModal(false)} className="btn-secondary px-5 py-2 text-xs">
                  Cancel
                </button>
                <button type="submit" className="btn-primary px-5 py-2 text-xs hover:scale-[1.02] active:scale-[0.98] transition-all">
                  Save Team
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </>
  );
}
