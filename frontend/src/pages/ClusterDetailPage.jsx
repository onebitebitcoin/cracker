/**
 * 클러스터 상세 페이지
 */
import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Package, Wallet, TrendingUp, Hash, ExternalLink } from 'lucide-react';
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  Button,
  LoadingSpinner,
  ErrorAlert,
  StatsCard,
} from '../components';
import { clustersApi } from '../api';

export const ClusterDetailPage = () => {
  const { clusterId } = useParams();
  const navigate = useNavigate();

  const [clusterData, setClusterData] = useState(null);
  const [addresses, setAddresses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (clusterId) {
      loadClusterData();
    }
  }, [clusterId]);

  const loadClusterData = async () => {
    try {
      setLoading(true);
      setError(null);

      const data = await clustersApi.getCluster(clusterId);
      setClusterData(data);
      setAddresses(data.addresses || []);
    } catch (err) {
      console.error('클러스터 데이터 로드 실패:', err);
      setError(err);
    } finally {
      setLoading(false);
    }
  };

  const handleAddressClick = (address) => {
    navigate(`/address/${address}`);
  };

  return (
    <div className="min-h-screen bg-cream-100">
      {/* Header */}
      <header className="bg-white border-b border-cream-300 px-4 py-6">
        <div className="max-w-7xl mx-auto">
          <Button
            variant="outline"
            size="sm"
            onClick={() => navigate(-1)}
            className="mb-4"
          >
            <ArrowLeft size={16} className="mr-2" />
            뒤로 가기
          </Button>
          <h1 className="text-3xl font-bold text-gray-900">클러스터 상세</h1>
          {clusterData && (
            <p className="text-gray-600 mt-1">
              {clusterData.label || `클러스터 ${clusterId.substring(0, 8)}...`}
            </p>
          )}
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

        {/* 클러스터 데이터 표시 */}
        {!loading && clusterData && (
          <div className="space-y-6">
            {/* 통계 카드 */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              <StatsCard
                icon={Package}
                label="주소 수"
                value={clusterData.address_count || 0}
              />
              <StatsCard
                icon={Wallet}
                label="총 잔액"
                value={`${clusterData.total_balance?.toFixed(4) || '0'} BTC`}
              />
              <StatsCard
                icon={TrendingUp}
                label="총 수신"
                value={`${clusterData.total_received?.toFixed(4) || '0'} BTC`}
              />
              <StatsCard
                icon={Hash}
                label="트랜잭션 수"
                value={clusterData.tx_count || 0}
              />
            </div>

            {/* 클러스터 정보 */}
            <Card>
              <CardHeader>
                <CardTitle>클러스터 정보</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                  <div>
                    <p className="text-gray-500 mb-1">클러스터 ID</p>
                    <p className="font-mono text-gray-900 break-all">{clusterId}</p>
                  </div>
                  <div>
                    <p className="text-gray-500 mb-1">라벨</p>
                    <p className="font-semibold text-gray-900">
                      {clusterData.label || '-'}
                    </p>
                  </div>
                  {clusterData.first_seen && (
                    <div>
                      <p className="text-gray-500 mb-1">첫 활동</p>
                      <p className="text-gray-900">
                        {new Date(clusterData.first_seen).toLocaleString('ko-KR')}
                      </p>
                    </div>
                  )}
                  {clusterData.last_seen && (
                    <div>
                      <p className="text-gray-500 mb-1">마지막 활동</p>
                      <p className="text-gray-900">
                        {new Date(clusterData.last_seen).toLocaleString('ko-KR')}
                      </p>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>

            {/* 주소 목록 */}
            <Card>
              <CardHeader>
                <CardTitle>클러스터 주소 ({addresses.length})</CardTitle>
                <CardDescription>이 클러스터에 속한 모든 주소</CardDescription>
              </CardHeader>
              <CardContent>
                {addresses.length === 0 ? (
                  <div className="py-8 text-center text-gray-500">
                    주소가 없습니다
                  </div>
                ) : (
                  <div className="space-y-2">
                    {addresses.map((addr) => (
                      <div
                        key={addr.address}
                        className="p-4 bg-cream-100 rounded-xl cursor-pointer hover:bg-cream-200 transition-colors"
                        onClick={() => handleAddressClick(addr.address)}
                      >
                        <div className="flex items-center justify-between">
                          <div className="flex-1">
                            <p className="font-mono text-sm text-gray-800 break-all mb-2">
                              {addr.address}
                            </p>
                            <div className="flex gap-4 text-sm text-gray-600">
                              <span>잔액: {addr.balance?.toFixed(4) || '0'} BTC</span>
                              <span>트랜잭션: {addr.tx_count || 0}</span>
                            </div>
                          </div>
                          <ExternalLink className="text-gray-400 flex-shrink-0 ml-4" size={20} />
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        )}
      </main>
    </div>
  );
};
