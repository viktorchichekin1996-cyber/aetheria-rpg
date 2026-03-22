// frontend/src/routes/index.tsx
import React from 'react';
import {
  createBrowserRouter,
  Navigate,
} from 'react-router-dom';
import { useSelector } from 'react-redux';
import { RootState } from '../store';

// Lazy load components для оптимизации загрузки
const AuthScreen = React.lazy(() => import('../screens/AuthScreen'));
const ClassSelectionScreen = React.lazy(() => import('../screens/ClassSelectionScreen'));
const GameScreen = React.lazy(() => import('../screens/GameScreen'));
const InventoryScreen = React.lazy(() => import('../screens/InventoryScreen'));
const CombatScreen = React.lazy(() => import('../screens/CombatScreen'));
const ShopScreen = React.lazy(() => import('../screens/ShopScreen'));
const ProfileScreen = React.lazy(() => import('../screens/ProfileScreen'));

/**
 * Компонент загрузки для lazy-loaded компонентов
 */
const LoadingFallback = () => (
  <div className="loading-fallback">
    <div className="spinner" />
    <p>Загрузка...</p>
  </div>
);

/**
 * Пропсы для защищённого роута
 */
interface ProtectedRouteProps {
  children: React.ReactNode;
  requireClass?: boolean;
}

/**
 * Защищённый роут - проверяет авторизацию пользователя
 */
const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
  children,
  requireClass = false,
}) => {
  const { player } = useSelector((state: RootState) => state.game);

  // Если пользователь не авторизован - redirect на auth
  if (!player.vkId) {
    return <Navigate to="/auth" replace />;
  }

  // Если требуется выбор класса и класс не выбран - redirect на class-selection
  if (requireClass && !player.characterClass) {
    return <Navigate to="/class-selection" replace />;
  }

  return <>{children}</>;
};

/**
 * Конфигурация роутера приложения
 */
export const router = createBrowserRouter([
  {
    path: '/',
    element: <Navigate to="/auth" replace />,
  },
  {
    path: '/auth',
    element: (
      <React.Suspense fallback={<LoadingFallback />}>
        <AuthScreen />
      </React.Suspense>
    ),
  },
  {
    path: '/class-selection',
    element: (
      <ProtectedRoute requireClass={false}>
        <React.Suspense fallback={<LoadingFallback />}>
          <ClassSelectionScreen />
        </React.Suspense>
      </ProtectedRoute>
    ),
  },
  {
    path: '/game',
    element: (
      <ProtectedRoute requireClass={true}>
        <React.Suspense fallback={<LoadingFallback />}>
          <GameScreen />
        </React.Suspense>
      </ProtectedRoute>
    ),
    children: [
      {
        path: 'inventory',
        element: (
          <React.Suspense fallback={<LoadingFallback />}>
            <InventoryScreen />
          </React.Suspense>
        ),
      },
      {
        path: 'combat',
        element: (
          <React.Suspense fallback={<LoadingFallback />}>
            <CombatScreen />
          </React.Suspense>
        ),
      },
      {
        path: 'shop',
        element: (
          <React.Suspense fallback={<LoadingFallback />}>
            <ShopScreen />
          </React.Suspense>
        ),
      },
      {
        path: 'profile',
        element: (
          <React.Suspense fallback={<LoadingFallback />}>
            <ProfileScreen />
          </React.Suspense>
        ),
      },
    ],
  },
  {
    path: '*',
    element: <Navigate to="/auth" replace />,
  },
]);

export default router;