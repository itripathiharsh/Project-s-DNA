import React, { createContext, useContext, useState, useCallback } from 'react';

const NotificationContext = createContext();

export const useNotification = () => useContext(NotificationContext);

export const NotificationProvider = ({ children }) => {
  const [toasts, setToasts] = useState([]);
  const [confirmDialog, setConfirmDialog] = useState(null);

  const toast = useCallback((message, type = 'info') => {
    const id = Date.now().toString(36) + Math.random().toString(36).substr(2);
    setToasts(prev => [...prev, { id, message, type }]);
    setTimeout(() => {
      setToasts(prev => prev.filter(t => t.id !== id));
    }, 5000);
  }, []);

  const confirm = useCallback((message, onConfirm) => {
    setConfirmDialog({ message, onConfirm });
  }, []);

  const handleConfirm = () => {
    if (confirmDialog && confirmDialog.onConfirm) {
      confirmDialog.onConfirm();
    }
    setConfirmDialog(null);
  };

  const handleCancel = () => {
    setConfirmDialog(null);
  };

  return (
    <NotificationContext.Provider value={{ toast, confirm }}>
      {children}
      {/* Toasts */}
      <div className="fixed bottom-4 right-4 z-50 flex flex-col gap-2">
        {toasts.map(t => (
          <div key={t.id} className={`p-4 rounded shadow-lg text-white max-w-sm animate-fade-in-up ${t.type === 'error' ? 'bg-red-500' : t.type === 'success' ? 'bg-green-500' : 'bg-blue-500'}`}>
            {t.message}
          </div>
        ))}
      </div>

      {/* Confirm Dialog */}
      {confirmDialog && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
          <div className="bg-surface p-6 rounded shadow-lg max-w-sm w-full border border-border/50">
            <h3 className="text-lg font-bold text-text-light mb-4">Confirm Action</h3>
            <p className="text-text-muted mb-6">{confirmDialog.message}</p>
            <div className="flex justify-end gap-3">
              <button onClick={handleCancel} className="px-4 py-2 text-text-muted hover:text-text-light transition-colors">
                Cancel
              </button>
              <button onClick={handleConfirm} className="px-4 py-2 bg-accent text-white rounded hover:bg-accent/90 transition-colors">
                Confirm
              </button>
            </div>
          </div>
        </div>
      )}
    </NotificationContext.Provider>
  );
};
