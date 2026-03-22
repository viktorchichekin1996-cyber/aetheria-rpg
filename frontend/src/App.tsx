// frontend/src/App.tsx
import React, { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Provider } from 'react-redux';
import { store, RootState } from './store';
import { vkBridgeService } from './services/vkBridge';
import { setVkBridgeReady, setPlayerData, addNotification, removeNotification } from './store/gameSlice';

// Components - заглушки для текущего блока
const LoadingOverlay = ({ visible }: { visible: boolean }) => {
  if (!visible) return null;
  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      background: 'rgba(0, 0, 0, 0.7)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 9999
    }}>
      <div style={{ color: '#fff', fontSize: '16px' }}>Загрузка...</div>
    </div>
  );
};

const NotificationContainer = ({ notifications }: { notifications: any[] }) => {
  return (
    <div style={{
      position: 'fixed',
      top: '16px',
      right: '16px',
      zIndex: 1000
    }}>
      {notifications.map((n) => (
        <div key={n.id} style={{
          padding: '12px 16px',
          marginBottom: '8px',
          borderRadius: '8px',
          background: n.type === 'error' ? '#e74c3c' : '#3498db',
          color: '#fff'
        }}>
          {n.message}
        </div>
      ))}
    </div>
  );
};

const AppContent: React.FC = () => {
  const dispatch = useDispatch();
  const { vkBridgeReady, loading, notifications } = useSelector(
    (state: RootState) => state.game.ui
  );

  useEffect(() => {
    const initVK = async () => {
      const success = await vkBridgeService.init();
      dispatch(setVkBridgeReady(success));
    };
    initVK();
  }, [dispatch]);

  return (
    <div className="app">
      <div style={{ padding: '20px', fontFamily: 'sans-serif' }}>
        <h1>🏰 Королевства Этерии</h1>
        <p>Статус: {vkBridgeReady ? 'VK Bridge готов' : 'Инициализация...'}</p>
        <p>Backend: <code>http://localhost:8000</code></p>
      </div>
      <NotificationContainer notifications={notifications} />
      <LoadingOverlay visible={loading} />
    </div>
  );
};

const App: React.FC = () => {
  return (
    <Provider store={store}>
      <AppContent />
    </Provider>
  );
};

export default App;