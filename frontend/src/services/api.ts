// frontend/src/services/api.ts
import axios, {
  AxiosInstance,
  AxiosRequestConfig,
  AxiosResponse,
  InternalAxiosRequestConfig,
} from 'axios';
import { store } from '../store';
import { addNotification, setLoading, setError } from '../store/gameSlice';

// Базовый URL API
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

/**
 * API клиент для взаимодействия с backend
 * Настраивает interceptors для авторизации и обработки ошибок
 */
class ApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
      timeout: 10000,
    });

    this.setupInterceptors();
  }

  /**
   * Настройка interceptors для запросов и ответов
   */
  private setupInterceptors(): void {
    // Request interceptor - добавляем auth токены
    this.client.interceptors.request.use(
      (config: InternalAxiosRequestConfig) => {
        const state = store.getState();
        const vkId = state.game.player.vkId;

        if (vkId) {
          config.headers = config.headers || {};
          config.headers['Authorization'] = `Bearer ${vkId}`;
        }
        return config;
      },
      (error) => {
        store.dispatch(setError(error.message));
        return Promise.reject(error);
      }
    );

    // Response interceptor - обработка ошибок
    this.client.interceptors.response.use(
      (response: AxiosResponse) => response,
      (error) => {
        store.dispatch(setLoading(false));

        const message = error.response?.data?.detail || 
                       error.response?.data?.error?.message || 
                       error.message || 
                       'Произошла ошибка';

        store.dispatch(addNotification({
          message,
          type: 'error',
          duration: 5000,
        }));

        if (error.response?.status === 401) {
          console.warn('Unauthorized, redirect to auth...');
        }

        return Promise.reject(error);
      }
    );
  }

  // === AUTH ===
  /**
   * Авторизация через VK
   * Отправляет данные пользователя на backend для создания/обновления аккаунта
   */
  async vkLogin(params: {
    vk_id: number;
    first_name: string;
    last_name: string;
    sign: string;
    auth_date: number;
    [key: string]: any;
  }) {
    const formData = new FormData();
    Object.entries(params).forEach(([key, value]) => {
      formData.append(key, String(value));
    });

    return this.client.post('/auth/login', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  }

  // === PLAYER ===
  async getPlayer(vkId: number) {
    return this.client.get(`/player/${vkId}`);
  }

  async getPlayerStats(vkId: number) {
    return this.client.get(`/player/${vkId}/stats`);
  }

  async updateLocation(vkId: number, location: string) {
    return this.client.post(`/player/${vkId}/location`, null, {
      params: { location },
    });
  }

  // === CLASSES ===
  async getClasses() {
    return this.client.get('/classes');
  }

  async getClassInfo(classId: string) {
    return this.client.get(`/classes/${classId}`);
  }

  async selectClass(classId: string) {
    return this.client.post('/classes/select', { class_id: classId });
  }

  // === Утилиты ===
  async request<T = any>(
    config: AxiosRequestConfig
  ): Promise<AxiosResponse<T>> {
    store.dispatch(setLoading(true));
    try {
      const response = await this.client.request<T>(config);
      store.dispatch(setLoading(false));
      return response;
    } catch (error) {
      store.dispatch(setLoading(false));
      throw error;
    }
  }

  get axios(): AxiosInstance {
    return this.client;
  }
}

export const api = new ApiClient();
export default api;