// frontend/src/services/vkBridge.ts
import vkBridge from '@vkontakte/vk-bridge';

// Типы для данных пользователя (упрощённые для совместимости)
export interface VKUserInfo {
  id: number;
  first_name: string;
  last_name: string;
  photo_200?: string;
  photo_max_orig?: string;
  city?: {
    title: string;
  };
}

// Тип для результата инициализации
export interface VKInitResult {
  result: true;
}

export class VKBridgeService {
  private static instance: VKBridgeService;
  private initialized = false;
  private userInfo: VKUserInfo | null = null;

  private constructor() {}

  static getInstance(): VKBridgeService {
    if (!VKBridgeService.instance) {
      VKBridgeService.instance = new VKBridgeService();
    }
    return VKBridgeService.instance;
  }

  /**
   * Инициализация VK Bridge
   */
  async init(): Promise<boolean> {
    try {
      await vkBridge.send('VKWebAppInit');
      this.initialized = true;
      console.log('✅ VK Bridge initialized');
      return true;
    } catch (error) {
      console.error('❌ VK Bridge init failed:', error);
      return false;
    }
  }

  /**
   * Получение информации о пользователе
   */
  async getUserInfo(): Promise<VKUserInfo | null> {
    if (!this.initialized) {
      await this.init();
    }

    try {
      const result = await vkBridge.send('VKWebAppGetUserInfo');
      this.userInfo = result as VKUserInfo;
      return this.userInfo;
    } catch (error) {
      console.error('Failed to get user info:', error);
      return null;
    }
  }

  /**
   * Показ системного уведомления (упрощённая версия)
   */
  async showSnackbar(message: string): Promise<void> {
    try {
      // Используем любой для обхода строгой типизации VK Bridge
      await (vkBridge as any).send('VKWebAppShowSnackbar', {
        message,
        duration: 3,
      });
    } catch (error) {
      console.warn('showSnackbar not supported:', error);
    }
  }

  /**
   * Проверка доступности метода
   */
  supports(method: string): boolean {
    const supportedMethods = [
      'VKWebAppInit',
      'VKWebAppGetUserInfo',
      'VKWebAppShowSnackbar',
      'VKWebAppSetLocation',
      'VKWebAppAddToFavorites'
    ];
    return supportedMethods.includes(method);
  }

  /**
   * Отправка произвольного запроса
   */
  async send<T = any>(method: string, params?: Record<string, any>): Promise<T> {
    if (!this.initialized) {
      await this.init();
    }
    return vkBridge.send(method as any, params) as Promise<T>;
  }

  isInitialized(): boolean {
    return this.initialized;
  }

  getUserInfoCached(): VKUserInfo | null {
    return this.userInfo;
  }
}

// Экспорт единственного инстанса
export const vkBridgeService = VKBridgeService.getInstance();

export default vkBridgeService;