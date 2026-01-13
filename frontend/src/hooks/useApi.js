/**
 * useApi Custom Hook
 * API 호출 시 loading, error 상태를 자동으로 관리
 */
import { useState } from 'react';

export const useApi = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const execute = async (apiFunction) => {
    try {
      setLoading(true);
      setError(null);
      const result = await apiFunction();
      return result;
    } catch (err) {
      console.error('API 호출 실패:', err);
      setError(err);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return { loading, error, execute, setError };
};
