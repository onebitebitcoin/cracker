/**
 * 클러스터 대시보드 페이지
 */
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Package, ArrowRight } from 'lucide-react';
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  LoadingSpinner,
  ErrorAlert,
  Button,
} from '../components';
import { clustersApi } from '../api';

export const ClustersPage = () => {
  const navigate = useNavigate();
  const [clusters, setClusters] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [pagination, setPagination] = useState({
    page: 1,
    page_size: 20,
    total: 0,
    total_pages: 0,
  });

  useEffect(() => {
    loadClusters();
  }, []);

  const loadClusters = async (offset = 0) => {
    try {
      setLoading(true);
      setError(null);
      const data = await clustersApi.getClusters({ limit: 20, offset });
      setClusters(data.data || []);
      setPagination({
        page: data.page || 1,
        page_size: data.page_size || 20,
        total: data.total || 0,
        total_pages: data.total_pages || 0,
      });
    } catch (err) {
      console.error('클러스터 로드 실패:', err);
      setError(err);
    } finally {
      setLoading(false);
    }
  };

  const handleClusterClick = (clusterId) => {
    navigate(`/cluster/${clusterId}`);
  };

  const handleNextPage = () => {
    if (pagination.page < pagination.total_pages) {
      loadClusters((pagination.page) * pagination.page_size);
    }
  };

  const handlePrevPage = () => {
    if (pagination.page > 1) {
      loadClusters((pagination.page - 2) * pagination.page_size);
    }
  };

  return (
    <div className="min-h-screen bg-cream-100">
      {/* Header */}
      <header className="bg-white border-b border-cream-300 px-4 py-6">
        <div className="max-w-7xl mx-auto">
          <h1
            className="text-3xl font-bold text-gray-900 cursor-pointer"
            onClick={() => navigate('/')}
          >
            Bitcoin Cracker
          </h1>
          <p className="text-gray-600 mt-1">클러스터 대시보드</p>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-8">
        {/* 에러 표시 */}
        {error && <ErrorAlert error={error} className="mb-6" />}

        {/* 로딩 중 */}
        {loading && (
          <Card>
            <LoadingSpinner size={48} className="py-12" />
          </Card>
        )}

        {/* 클러스터 목록 */}
        {!loading && (
          <Card>
            <CardHeader>
              <CardTitle>모든 클러스터</CardTitle>
              <CardDescription>
                총 {pagination.total}개의 클러스터 (페이지 {pagination.page} / {pagination.total_pages})
              </CardDescription>
            </CardHeader>
            <CardContent>
              {clusters.length === 0 ? (
                <div className="py-12 text-center">
                  <Package size={48} className="mx-auto text-gray-400 mb-4" />
                  <p className="text-gray-600">클러스터가 없습니다</p>
                </div>
              ) : (
                <>
                  <div className="space-y-3">
                    {clusters.map((cluster) => (
                      <div
                        key={cluster.id}
                        className="p-4 bg-cream-100 rounded-xl cursor-pointer hover:bg-cream-200 transition-colors"
                        onClick={() => handleClusterClick(cluster.id)}
                      >
                        <div className="flex items-center justify-between">
                          <div className="flex-1">
                            <p className="font-bold text-gray-900">
                              {cluster.label || `클러스터 ${cluster.id.substring(0, 8)}...`}
                            </p>
                            <div className="flex gap-4 mt-2 text-sm text-gray-600">
                              <span>주소: {cluster.address_count}</span>
                              <span>잔액: {cluster.total_balance?.toFixed(4) || '0'} BTC</span>
                              <span>트랜잭션: {cluster.tx_count || 0}</span>
                            </div>
                          </div>
                          <ArrowRight className="text-gray-400" size={20} />
                        </div>
                      </div>
                    ))}
                  </div>

                  {/* Pagination */}
                  {pagination.total_pages > 1 && (
                    <div className="flex justify-between items-center mt-6 pt-6 border-t border-cream-300">
                      <Button
                        variant="outline"
                        onClick={handlePrevPage}
                        disabled={pagination.page <= 1}
                      >
                        이전
                      </Button>
                      <span className="text-sm text-gray-600">
                        페이지 {pagination.page} / {pagination.total_pages}
                      </span>
                      <Button
                        variant="outline"
                        onClick={handleNextPage}
                        disabled={pagination.page >= pagination.total_pages}
                      >
                        다음
                      </Button>
                    </div>
                  )}
                </>
              )}
            </CardContent>
          </Card>
        )}
      </main>
    </div>
  );
};
