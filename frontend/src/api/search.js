/**
 * Search API
 */
import apiClient from './client';

export const searchApi = {
  /**
   * 주소, 트랜잭션 ID, 클러스터 검색
   */
  search: async (query) => {
    const response = await apiClient.get('/search', {
      params: { q: query },
    });
    return response.data;
  },
};
