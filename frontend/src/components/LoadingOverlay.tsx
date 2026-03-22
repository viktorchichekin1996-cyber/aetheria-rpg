import React from 'react';

interface LoadingOverlayProps {
  visible: boolean;
  message?: string;
}

export const LoadingOverlay: React.FC<LoadingOverlayProps> = ({ 
  visible, 
  message = 'Загрузка...' 
}) => {
  if (!visible) return null;

  return (
    <div className="loading-overlay" style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      background: 'rgba(0, 0, 0, 0.7)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 9999,
      flexDirection: 'column',
      gap: '16px'
    }}>
      <div className="spinner" style={{
        width: '48px',
        height: '48px',
        border: '4px solid rgba(255,255,255,0.3)',
        borderTop: '4px solid #fff',
        borderRadius: '50%',
        animation: 'spin 1s linear infinite'
      }} />
      {message && (
        <span style={{ color: '#fff', fontSize: '16px' }}>{message}</span>
      )}
      <style>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
};

export default LoadingOverlay;