/**
 * API 클라이언트 설정
 */
import axios from 'axios';

// API Base URL
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

// Axios 인스턴스 생성
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30초
});

// 요청 인터셉터
apiClient.interceptors.request.use(
  (config) => {
    console.log(`[API Request] ${config.method.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('[API Request Error]', error);
    return Promise.reject(error);
  }
);

// 응답 인터셉터
apiClient.interceptors.response.use(
  (response) => {
    console.log(`[API Response] ${response.config.url}`, response.data);
    return response;
  },
  (error) => {
    console.error('[API Response Error]', error.response?.data || error.message);

    // 에러 메시지 포맷팅
    const errorMessage = error.response?.data?.message || error.message || '알 수 없는 오류가 발생했습니다';
    const errorDetail = error.response?.data?.detail || error.response?.data?.error;

    return Promise.reject({
      message: errorMessage,
      detail: errorDetail,
      status: error.response?.status,
      originalError: error,
    });
  }
);

export default apiClient;
