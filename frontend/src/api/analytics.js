/**
 * Analytics API
 */
import apiClient from './client';

export const analyticsApi = {
  /**
   * 전체 시스템 통계
   */
  getSummary: async () => {
    const response = await apiClient.get('/analytics/summary');
    return response.data;
  },

  /**
   * 클러스터 크기 분포
   */
  getClusterDistribution: async () => {
    const response = await apiClient.get('/analytics/cluster-distribution');
    return response.data;
  },
};
