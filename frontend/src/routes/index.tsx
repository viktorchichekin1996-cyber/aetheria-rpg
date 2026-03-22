// frontend/src/routes/index.tsx
import React from 'react';
import {
  createBrowserRouter,
  RouterProvider,
  Navigate,
} from 'react-router-dom';
import { useSelector } from 'react-redux';
import { RootState } from '../store';

// Lazy load components for better performance
const AuthScreen = React.lazy(() => import('../screens/AuthScreen'));
const ClassSelectionScreen = React.lazy(() => import('../screens/ClassSelectionScreen'));
const GameScreen = React.lazy(() => import('../screens/GameScreen'));
const InventoryScreen = React.lazy(() => import('../screens/InventoryScreen'));
const CombatScreen = React.lazy(() => import('../screens/CombatScreen'));
const ShopScreen = React.lazy(() => import('../screens/ShopScreen'));
const ProfileScreen = React.lazy(() => import('../screens/ProfileScreen'));

// Loading fallback
const LoadingFallback = () => (
  <div className="loading-fallback">
    <div className="spinner" />
    <p>Загрузка...</p>
  </div>
);

// Protected route wrapper
interface ProtectedRouteProps {
  children: React.ReactNode;
  requireClass?: boolean;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
  children,
  requireClass = false,
}) => {
  const { player } = useSelector((state: RootState) => state.game);

  if (!player.vkId) {
    return <Navigate to="/auth" replace />;
  }

  if (requireClass && !player.characterClass) {
    return <Navigate to="/class-selection" replace />;
  }

  return <>{children}</>;
};

// Router configuration
export const router = createBrowserRouter([
  {
    path: '/',
    element: <Navigate to="/game" replace />,
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
    element: <Navigate to="/game" replace />,
  },
]);

export default router;