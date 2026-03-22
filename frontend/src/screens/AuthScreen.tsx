// frontend/src/screens/AuthScreen.tsx
import React, { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import { vkBridgeService } from '../services/vkBridge';
import { api } from '../services/api';
import {
  setPlayerData,
  setVkBridgeReady,
  addNotification,
  setLoading,
} from '../store/gameSlice';
import { RootState } from '../store';
import './AuthScreen.css';

/**
 * Экран авторизации через VK Mini Apps
 * Обрабатывает вход через VK Bridge и перенаправляет на главный экран
 */
const AuthScreen: React.FC = () => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const [isLoggingIn, setIsLoggingIn] = useState(false);
  
  // Получаем состояние из Redux
  const { vkBridgeReady, loading } = useSelector((state: RootState) => state.game.ui);

  /**
   * Инициализация VK Bridge при монтировании компонента
   */
  useEffect(() => {
    const initVK = async () => {
      try {
        const success = await vkBridgeService.init();
        dispatch(setVkBridgeReady(success));
        
        if (success) {
          // Пробуем получить информацию о пользователе
          const userInfo = await vkBridgeService.getUserInfo();
          if (userInfo && userInfo.id) {
            // Если пользователь уже авторизован, перенаправляем на главный экран
            dispatch(setPlayerData({
              vkId: userInfo.id,
              username: `${userInfo.first_name} ${userInfo.last_name}`.trim(),
              avatar: userInfo.photo_200 || '',
            }));
            navigate('/game');
          }
        }
      } catch (error) {
        dispatch(addNotification({
          message: 'Ошибка инициализации VK Bridge',
          type: 'error',
          duration: 5000,
        }));
      }
    };

    initVK();
  }, [dispatch, navigate]);

  /**
   * Обработчик кнопки входа через VK
   */
  const handleVKLogin = async () => {
    if (!vkBridgeReady) {
      dispatch(addNotification({
        message: 'VK Bridge ещё не готов. Попробуйте позже.',
        type: 'warning',
        duration: 3000,
      }));
      return;
    }

    setIsLoggingIn(true);
    dispatch(setLoading(true));

    try {
      // Получаем данные пользователя через VK Bridge
      const userInfo = await vkBridgeService.getUserInfo();
      
      if (!userInfo || !userInfo.id) {
        throw new Error('Не удалось получить данные пользователя');
      }

      // Отправляем данные на backend для авторизации
      // В реальном приложении здесь будет отправка sign и других параметров
      const response = await api.vkLogin({
        vk_id: userInfo.id,
        first_name: userInfo.first_name || 'Игрок',
        last_name: userInfo.last_name || '',
        sign: 'demo-sign', // В продакшене здесь будет реальная подпись от VK
        auth_date: Math.floor(Date.now() / 1000),
      });

      if (response.data) {
        // Сохраняем данные игрока в Redux
        dispatch(setPlayerData({
          vkId: userInfo.id,
          username: `${userInfo.first_name} ${userInfo.last_name}`.trim(),
          avatar: userInfo.photo_200 || '',
          characterClass: response.data.character_class || 'warrior',
          level: response.data.level || 1,
          gold: response.data.gold || 0,
        }));

        dispatch(addNotification({
          message: `Добро пожаловать, ${userInfo.first_name}!`,
          type: 'success',
          duration: 3000,
        }));

        // Перенаправляем на главный экран
        navigate('/game');
      }
    } catch (error: any) {
      // Обработка ошибок авторизации
      dispatch(addNotification({
        message: error.response?.data?.detail || 'Ошибка авторизации. Попробуйте снова.',
        type: 'error',
        duration: 5000,
      }));
    } finally {
      setIsLoggingIn(false);
      dispatch(setLoading(false));
    }
  };

  return (
    <div className="auth-screen">
      <div className="auth-screen__container">
        {/* Логотип игры */}
        <div className="auth-screen__logo">
          <span className="auth-screen__logo-icon">🏰</span>
          <h1 className="auth-screen__title">Королевства Этерии</h1>
        </div>

        {/* Описание */}
        <p className="auth-screen__description">
          Текстовая RPG с AI-повествованием и PvP боями
        </p>

        {/* Кнопка входа через VK */}
        <div className="auth-screen__actions">
          <button
            className="auth-screen__vk-button"
            onClick={handleVKLogin}
            disabled={isLoggingIn || !vkBridgeReady || loading}
          >
            {isLoggingIn ? (
              <>
                <span className="auth-screen__spinner"></span>
                <span>Вход...</span>
              </>
            ) : (
              <>
                <span className="auth-screen__vk-icon">VK</span>
                <span>Войти через VK</span>
              </>
            )}
          </button>
        </div>

        {/* Статус подключения */}
        <div className="auth-screen__status">
          <span className={`auth-screen__status-dot ${vkBridgeReady ? 'auth-screen__status-dot--ready' : ''}`}></span>
          <span className="auth-screen__status-text">
            {vkBridgeReady ? 'VK Bridge готов' : 'Инициализация...'}
          </span>
        </div>

        {/* Дополнительная информация */}
        <div className="auth-screen__footer">
          <p className="auth-screen__footer-text">
            Авторизуясь, вы принимаете условия игры
          </p>
        </div>
      </div>
    </div>
  );
};

export default AuthScreen;