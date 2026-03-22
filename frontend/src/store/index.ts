// frontend/src/store/index.ts
import { configureStore } from '@reduxjs/toolkit';
import gameReducer from './gameSlice';

/**
 * Настройка Redux Store
 * Используем combineReducers для модульности, даже если пока один слайс
 */
export const store = configureStore({
  reducer: {
    game: gameReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        // Игнорируем проверки для действий с датами и функциями из VK Bridge
        ignoredActions: ['game/setVkBridgeReady'],
        ignoredPaths: ['game.ui.notifications'],
      },
    }),
  devTools: process.env.NODE_ENV !== 'production',
});

/**
 * Тип для состояния всего приложения
 * Выводится автоматически из структуры store
 */
export type RootState = ReturnType<typeof store.getState>;

/**
 * Тип для dispatch функций
 * Нужен для типизации thunk и действий в компонентах
 */
export type AppDispatch = typeof store.dispatch;

export default store;