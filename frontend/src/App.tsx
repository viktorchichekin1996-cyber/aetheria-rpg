// frontend/src/App.tsx
import React, { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Provider } from 'react-redux';
import { store, RootState } from './store';
import { RouterProvider } from 'react-router-dom';
import { router } from './routes';
import { vkBridgeService } from './services/vkBridge';
import {
  setVkBridgeReady,
  setPlayerData,
  addNotification,
  removeNotification,
} from './store/gameSlice';

// Components
import NotificationContainer from './components/NotificationContainer';
import LoadingOverlay from './components/LoadingOverlay';

/**
 * Основной контент приложения с роутингом
 */
const AppContent: React.FC = () => {
  const dispatch = useDispatch();
  const { vkBridgeReady, notifications, loading } = useSelector(
    (state: RootState) => state.game.ui
  );
  const player = useSelector((state: RootState) => state.game.player);

  /**
   * Инициализация VK Bridge при монтировании
   */
  useEffect(() => {
    const initVK = async () => {
      const success = await vkBridgeService.init();
      dispatch(setVkBridgeReady(success));

      if (success) {
        // Пробуем получить информацию о пользователе
        const userInfo = await vkBridgeService.getUserInfo();
        if (userInfo) {
          dispatch(setPlayerData({
            vkId: userInfo.id,
            username: `${userInfo.first_name} ${userInfo.last_name}`.trim(),
            avatar: userInfo.photo_200 || '',
          }));
        }
      }
    };

    initVK();
  }, [dispatch]);

  /**
   * Авто-скрытие уведомлений по таймеру
   */
  useEffect(() => {
    const timers = notifications.map(notification => {
      if (notification.duration) {
        return setTimeout(() => {
          dispatch(removeNotification(notification.id));
        }, notification.duration);
      }
      return null;
    });

    return () => {
      timers.forEach(timer => timer && clearTimeout(timer));
    };
  }, [notifications, dispatch]);

  /**
   * Синхронизация данных игрока при изменении vkId
   */
  useEffect(() => {
    if (player.vkId && vkBridgeReady) {
      // Здесь можно добавить загрузку данных игрока с backend
      console.log('Player vkId:', player.vkId);
    }
  }, [player.vkId, vkBridgeReady, dispatch]);

  return (
    <div className="app">
      <RouterProvider router={router} />
      <NotificationContainer notifications={notifications} />
      <LoadingOverlay visible={loading} />
    </div>
  );
};

/**
 * Корневой компонент приложения с Redux Provider
 */
const App: React.FC = () => {
  return (
    <Provider store={store}>
      <AppContent />
    </Provider>
  );
};

export default App;