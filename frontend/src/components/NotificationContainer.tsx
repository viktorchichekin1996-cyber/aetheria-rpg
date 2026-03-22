// frontend/src/components/NotificationContainer.tsx
import React from 'react';
import { useDispatch } from 'react-redux';
import { removeNotification } from '../store/gameSlice';
import './NotificationContainer.css';

/**
 * Интерфейс уведомления
 */
export interface Notification {
  id: string;
  message: string;
  type: 'success' | 'error' | 'warning' | 'info';
  duration?: number;
}

/**
 * Пропсы компонента
 */
interface NotificationContainerProps {
  notifications: Notification[];
}

/**
 * Контейнер для отображения уведомлений
 * Показывает уведомления в правом верхнем углу экрана
 */
const NotificationContainer: React.FC<NotificationContainerProps> = ({
  notifications,
}) => {
  const dispatch = useDispatch();

  /**
   * Получение CSS класса для типа уведомления
   */
  const getNotificationClass = (type: string): string => {
    const classes: Record<string, string> = {
      success: 'notification--success',
      error: 'notification--error',
      warning: 'notification--warning',
      info: 'notification--info',
    };
    return classes[type] || '';
  };

  /**
   * Получение иконки для типа уведомления
   */
  const getNotificationIcon = (type: string): string => {
    const icons: Record<string, string> = {
      success: '✓',
      error: '✕',
      warning: '⚠',
      info: 'ℹ',
    };
    return icons[type] || 'ℹ';
  };

  return (
    <div className="notification-container">
      {notifications.map((notification) => (
        <div
          key={notification.id}
          className={`notification ${getNotificationClass(notification.type)}`}
          role="alert"
        >
          <div className="notification__content">
            <span className="notification__icon">
              {getNotificationIcon(notification.type)}
            </span>
            <p className="notification__message">{notification.message}</p>
          </div>
          <button
            className="notification__close"
            onClick={() => dispatch(removeNotification(notification.id))}
            aria-label="Закрыть уведомление"
          >
            ×
          </button>
        </div>
      ))}
    </div>
  );
};

export default NotificationContainer;