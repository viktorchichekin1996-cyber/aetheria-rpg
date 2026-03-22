// frontend/src/services/vkBridge.ts
import vkBridge from '@vkontakte/vk-bridge';

/**
 * Интерфейс для данных пользователя VK
 */
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

/**
 * Сервис для работы с VK Bridge
 * Реализует паттерн Singleton для единственного инстанса
 */
export class VKBridgeService {
  private static instance: VKBridgeService;
  private initialized = false;
  private userInfo: VKUserInfo | null = null;

  private constructor() {}

  /**
   * Получение единственного инстанса сервиса
   */
  static getInstance(): VKBridgeService {
    if (!VKBridgeService.instance) {
      VKBridgeService.instance = new VKBridgeService();
    }
    return VKBridgeService.instance;
  }

  /**
   * Инициализация VK Bridge
   * Должна вызываться один раз при старте приложения
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
   * Получение информации о пользователе VK
   * Кэширует данные после первого получения
   */
  async getUserInfo(): Promise<VKUserInfo | null> {
    if (!this.initialized) {
      await this.init();
    }

    // Возвращаем кэшированные данные если есть
    if (this.userInfo) {
      return this.userInfo;
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
   * Показ системного уведомления VK
   */
  async showSnackbar(message: string): Promise<void> {
    try {
      await (vkBridge as any).send('VKWebAppShowSnackbar', {
        message,
        duration: 3,
      });
    } catch (error) {
      console.warn('showSnackbar not supported:', error);
    }
  }

  /**
   * Проверка поддержки метода VK Bridge
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
   * Отправка произвольного запроса к VK Bridge
   */
  async send<T = any>(method: string, params?: Record<string, any>): Promise<T> {
    if (!this.initialized) {
      await this.init();
    }
    return vkBridge.send(method as any, params) as Promise<T>;
  }

  /**
   * Проверка статуса инициализации
   */
  isInitialized(): boolean {
    return this.initialized;
  }

  /**
   * Получение кэшированной информации о пользователе
   */
  getUserInfoCached(): VKUserInfo | null {
    return this.userInfo;
  }

  /**
   * Сброс кэша пользователя (для logout)
   */
  clearUserInfo(): void {
    this.userInfo = null;
  }
}

// Экспорт единственного инстанса
export const vkBridgeService = VKBridgeService.getInstance();

export default vkBridgeService;