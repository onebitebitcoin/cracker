/**
 * Address API
 */
import apiClient from './client';

export const addressesApi = {
  /**
   * 주소 상세 정보 조회
   */
  getAddress: async (address) => {
    const response = await apiClient.get(`/addresses/${address}`);
    return response.data;
  },

  /**
   * 주소의 트랜잭션 히스토리 조회
   */
  getAddressTransactions: async (address, params = {}) => {
    const { limit = 50, offset = 0 } = params;
    const response = await apiClient.get(`/addresses/${address}/transactions`, {
      params: { limit, offset },
    });
    return response.data;
  },

  /**
   * 주소가 속한 클러스터 정보 조회
   */
  getAddressCluster: async (address) => {
    const response = await apiClient.get(`/addresses/${address}/cluster`);
    return response.data;
  },
};
