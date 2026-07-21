import { useState, useEffect } from 'react';
import PageHeader from '../components/PageHeader';
import { getNotifications, readNotification, readAllNotifications, deleteNotification } from '../services/api';
import { useNotification } from '../components/NotificationContext';

export default function TaskMonitor() {
  const [notifications, setNotifications] = useState([]);
  const [filter, setFilter] = useState('all'); // all, unread
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const { toast } = useNotification();

  const loadNotifications = async () => {
    try {
      const res = await getNotifications();
      setNotifications(res.notifications || []);
    } catch (err) {
      setError(err.message || String(err));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadNotifications();
  }, []);

  const handleRead = async (nid) => {
    try {
      await readNotification(nid);
      await loadNotifications();
    } catch (err) {
      toast('Failed to mark read: ' + err.message, 'error');
    }
  };

  const handleReadAll = async () => {
    try {
      await readAllNotifications();
      await loadNotifications();
    } catch (err) {
      toast('Failed to mark all read: ' + err.message, 'error');
    }
  };

  const handleDelete = async (nid) => {
    try {
      await deleteNotification(nid);
      await loadNotifications();
    } catch (err) {
      toast('Failed to dismiss alert: ' + err.message, 'error');
    }
  };

  const filtered = filter === 'all' 
    ? notifications 
    : notifications.filter((n) => !n.read);

  const getAlertStyle = (type) => {
    switch (type) {
      case 'warning': return 'bg-[#1b1913]/30 border-signal-amber/30 text-signal-amber';
      case 'error': return 'bg-[#220d0d]/30 border-signal-rose/30 text-signal-rose';
      default: return 'bg-primary/5 border-primary/20 text-primary';
    }
  };

  const getIndicatorColor = (type) => {
    switch (type) {
      case 'warning': return 'bg-signal-amber';
      case 'error': return 'bg-signal-rose';
      default: return 'bg-primary';
    }
  };

  return (
    <>
      <PageHeader
        title="Notifications & Tasks"
        subtitle="Background jobs execution history and system warnings"
        actions={
          <button onClick={handleReadAll} className="btn-secondary px-4 py-2 text-xs flex items-center gap-1.5 hover:scale-[1.02] active:scale-[0.98] transition-all">
            <span className="material-symbols-outlined text-[15px]">done_all</span> Mark All Read
          </button>
        }
      />
      
      <div className="p-6 flex flex-col gap-6 max-w-[900px] mx-auto w-full font-sans text-xs">
        {/* Toggle tabs */}
        <div className="flex gap-2.5 bg-surface-container/20 border border-border-subtle/50 p-1.5 rounded-xl w-max">
          <button
            onClick={() => setFilter('all')}
            className={`px-4 py-1.5 rounded-lg font-semibold transition-all text-xs ${
              filter === 'all' ? 'bg-primary text-on-primary shadow-lg' : 'text-text-muted hover:text-on-surface'
            }`}
          >
            All Messages
          </button>
          <button
            onClick={() => setFilter('unread')}
            className={`px-4 py-1.5 rounded-lg font-semibold transition-all text-xs flex items-center gap-1.5 ${
              filter === 'unread' ? 'bg-primary text-on-primary shadow-lg' : 'text-text-muted hover:text-on-surface'
            }`}
          >
            <span>Unread</span>
            <span className="bg-surface-container-high text-on-surface font-extrabold text-[9px] px-1.5 py-0.5 rounded-full border border-border-subtle">
              {notifications.filter(n => !n.read).length}
            </span>
          </button>
        </div>

        {loading ? (
          <div className="flex justify-center items-center py-20">
            <div className="w-10 h-10 border-2 border-primary/20 border-t-primary rounded-full animate-spin" />
          </div>
        ) : error ? (
          <div className="text-signal-rose card-base p-5 border border-signal-rose/30 bg-signal-rose/5 text-xs font-semibold">{error}</div>
        ) : (
          <div className="space-y-3.5">
            {filtered.map((noti) => (
              <div
                key={noti.id}
                className={`p-4 rounded-xl border flex items-start gap-4 justify-between transition-all duration-200 relative overflow-hidden group ${
                  noti.read ? 'opacity-55 hover:opacity-85' : 'opacity-100'
                } ${getAlertStyle(noti.type)}`}
              >
                {/* Notice vertical ribbon */}
                <div className={`absolute left-0 top-0 bottom-0 w-1 ${getIndicatorColor(noti.type)}`} />
                
                <div className="flex-1 min-w-0 pl-2">
                  <div className="flex items-center gap-2.5 mb-1.5 flex-wrap">
                    <span className="font-extrabold text-xs text-on-surface truncate">{noti.title}</span>
                    {!noti.read && (
                      <span className="badge badge-high text-[9px] scale-90">New</span>
                    )}
                    <span className="text-[10px] text-text-muted opacity-80">{new Date(noti.timestamp).toLocaleString()}</span>
                  </div>
                  <p className="text-xs text-on-surface-variant leading-relaxed">{noti.message}</p>
                </div>
                
                <div className="flex items-center gap-1.5 flex-shrink-0">
                  {!noti.read && (
                    <button
                      onClick={() => handleRead(noti.id)}
                      className="p-1.5 rounded-lg bg-surface-container hover:bg-surface-container-high border border-border-subtle text-primary transition-all flex items-center justify-center"
                      title="Mark Read"
                    >
                      <span className="material-symbols-outlined text-[14px]">done</span>
                    </button>
                  )}
                  <button
                    onClick={() => handleDelete(noti.id)}
                    className="p-1.5 rounded-lg bg-surface-container hover:bg-surface-container-high border border-border-subtle text-signal-rose transition-all flex items-center justify-center"
                    title="Dismiss notification"
                  >
                    <span className="material-symbols-outlined text-[14px]">delete</span>
                  </button>
                </div>
              </div>
            ))}
            {filtered.length === 0 && (
              <div className="text-center text-text-muted py-16 card-base bg-surface-container/20 border border-border-subtle/50 rounded-2xl flex flex-col items-center justify-center gap-2">
                <span className="material-symbols-outlined text-[36px] text-text-muted/60">notifications_paused</span>
                <span className="text-xs">No active notices or warnings matching this logging query.</span>
              </div>
            )}
          </div>
        )}
      </div>
    </>
  );
}
