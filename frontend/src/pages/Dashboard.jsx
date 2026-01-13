/**
 * Dashboard 메인 화면
 */
import React, { useState, useEffect } from 'react';
import { Database, Network, Package, TrendingUp } from 'lucide-react';
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  SearchBar,
  StatsCard,
  LoadingSpinner,
  ErrorAlert,
} from '../components';
import { analyticsApi } from '../api';
import { useNavigate } from 'react-router-dom';

export const Dashboard = () => {
  const navigate = useNavigate();
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // 통계 데이터 로드
  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await analyticsApi.getSummary();
      setStats(data);
    } catch (err) {
      console.error('통계 로드 실패:', err);
      setError(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (query) => {
    console.log('검색:', query);
    // 검색 페이지로 이동
    navigate(`/search?q=${encodeURIComponent(query)}`);
  };

  return (
    <div className="min-h-screen bg-cream-100">
      {/* Header */}
      <header className="bg-white border-b border-cream-300 px-4 py-6">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-3xl font-bold text-gray-900">Bitcoin Cracker</h1>
          <p className="text-gray-600 mt-1">블록체인 분석 및 추적 서비스</p>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-8">
        {/* 검색 섹션 */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle>주소 검색</CardTitle>
            <CardDescription>Bitcoin 주소, 트랜잭션 ID, 또는 클러스터를 검색하세요</CardDescription>
          </CardHeader>
          <CardContent>
            <SearchBar onSearch={handleSearch} />
          </CardContent>
        </Card>

        {/* 에러 표시 */}
        {error && (
          <ErrorAlert error={error} className="mb-6" />
        )}

        {/* 로딩 중 */}
        {loading && (
          <Card>
            <LoadingSpinner size={48} className="py-12" />
          </Card>
        )}

        {/* 통계 섹션 */}
        {!loading && stats && (
          <>
            <div className="mb-6">
              <h2 className="text-xl font-bold text-gray-900 mb-4">시스템 통계</h2>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                <StatsCard
                  icon={Database}
                  label="총 주소"
                  value={stats.total_addresses?.toLocaleString() || '0'}
                />
                <StatsCard
                  icon={Package}
                  label="클러스터"
                  value={stats.total_clusters?.toLocaleString() || '0'}
                />
                <StatsCard
                  icon={TrendingUp}
                  label="트랜잭션"
                  value={stats.total_transactions?.toLocaleString() || '0'}
                />
                <StatsCard
                  icon={Network}
                  label="평균 클러스터 크기"
                  value={stats.avg_cluster_size?.toFixed(1) || '0'}
                />
              </div>
            </div>

            {/* The Golden Trail 섹션 */}
            <Card className="mb-6">
              <CardHeader>
                <CardTitle>The Golden Trail</CardTitle>
                <CardDescription>Bitcoin 네트워크 흐름 시각화</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="bg-cream-200 rounded-xl p-8 text-center">
                  <Network size={64} className="mx-auto text-gold-500 mb-4" />
                  <p className="text-gray-600">
                    네트워크 그래프는 주소를 검색하면 표시됩니다
                  </p>
                </div>
              </CardContent>
            </Card>

            {/* Quick Links */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <Card
                className="cursor-pointer hover:shadow-md transition-shadow"
                onClick={() => navigate('/clusters')}
              >
                <CardHeader>
                  <CardTitle className="text-lg">클러스터 대시보드</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-gray-600">모든 클러스터 보기 및 분석</p>
                </CardContent>
              </Card>

              <Card
                className="cursor-pointer hover:shadow-md transition-shadow"
                onClick={() => navigate('/analytics')}
              >
                <CardHeader>
                  <CardTitle className="text-lg">분석 통계</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-gray-600">상세 분석 및 차트</p>
                </CardContent>
              </Card>
            </div>
          </>
        )}
      </main>
    </div>
  );
};
