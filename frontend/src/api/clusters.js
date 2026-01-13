/**
 * Cluster API
 */
import apiClient from './client';

export const clustersApi = {
  /**
   * 모든 클러스터 목록 조회
   */
  getClusters: async (params = {}) => {
    const { limit = 20, offset = 0, min_size } = params;
    const response = await apiClient.get('/clusters', {
      params: { limit, offset, min_size },
    });
    return response.data;
  },

  /**
   * 특정 클러스터 상세 정보 조회
   */
  getCluster: async (clusterId) => {
    const response = await apiClient.get(`/clusters/${clusterId}`);
    return response.data;
  },

  /**
   * 클러스터 내 주소 간 관계 그래프 데이터
   */
  getClusterGraph: async (clusterId) => {
    const response = await apiClient.get(`/clusters/${clusterId}/graph`);
    return response.data;
  },
};
