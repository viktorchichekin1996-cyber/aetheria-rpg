// frontend/src/components/LoadingOverlay.tsx
import React from 'react';
import './LoadingOverlay.css';

/**
 * Пропсы компонента
 */
interface LoadingOverlayProps {
  visible: boolean;
  message?: string;
}

/**
 * Оверлей загрузки - показывает спиннер во время загрузки
 */
const LoadingOverlay: React.FC<LoadingOverlayProps> = ({
  visible,
  message = 'Загрузка...',
}) => {
  if (!visible) return null;

  return (
    <div className="loading-overlay">
      <div className="loading-overlay__content">
        <div className="loading-overlay__spinner" />
        {message && (
          <p className="loading-overlay__message">{message}</p>
        )}
      </div>
    </div>
  );
};

export default LoadingOverlay;