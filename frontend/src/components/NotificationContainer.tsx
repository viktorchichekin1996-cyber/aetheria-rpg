import React from 'react';

export interface Notification {
  id: string;
  message: string;
  type: 'success' | 'error' | 'info' | 'warning';
  duration?: number;
}

interface NotificationContainerProps {
  notifications: Notification[];
  onDismiss: (id: string) => void;
}

export const NotificationContainer: React.FC<NotificationContainerProps> = ({ 
  notifications, 
  onDismiss 
}) => {
  return (
    <div className="notification-container" style={{
      position: 'fixed',
      top: '16px',
      right: '16px',
      zIndex: 1000,
      display: 'flex',
      flexDirection: 'column',
      gap: '8px',
      maxWidth: '320px'
    }}>
      {notifications.map((notification) => (
        <div
          key={notification.id}
          className={`notification notification--${notification.type}`}
          style={{
            padding: '12px 16px',
            borderRadius: '8px',
            background: notification.type === 'error' ? '#e74c3c' : 
                       notification.type === 'success' ? '#2ecc71' : 
                       notification.type === 'warning' ? '#f39c12' : '#3498db',
            color: '#fff',
            fontSize: '14px',
            boxShadow: '0 2px 8px rgba(0,0,0,0.15)'
          }}
        >
          {notification.message}
        </div>
      ))}
    </div>
  );
};

export default NotificationContainer;