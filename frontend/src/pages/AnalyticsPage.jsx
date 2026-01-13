/**
 * Analytics 페이지
 */
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, TrendingUp, Package, Wallet, BarChart3 } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
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
import { analyticsApi } from '../api';

const COLORS = ['#E67E22', '#F39C12', '#D68910', '#B8860B', '#8B4513'];

export const AnalyticsPage = () => {
  const navigate = useNavigate();

  const [summary, setSummary] = useState(null);
  const [distribution, setDistribution] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadAnalytics();
  }, []);

  const loadAnalytics = async () => {
    try {
      setLoading(true);
      setError(null);

      const [summaryData, distributionData] = await Promise.all([
        analyticsApi.getSummary(),
        analyticsApi.getClusterDistribution().catch(() => []),
      ]);

      setSummary(summaryData);
      setDistribution(distributionData);
    } catch (err) {
      console.error('Analytics 데이터 로드 실패:', err);
      setError(err);
    } finally {
      setLoading(false);
    }
  };

  // 클러스터 분포 데이터를 차트 형식으로 변환
  const getDistributionChartData = () => {
    if (!distribution || !Array.isArray(distribution)) {
      return [];
    }

    return distribution;
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
          <h1 className="text-3xl font-bold text-gray-900">분석 통계</h1>
          <p className="text-gray-600 mt-1">시스템 전체 통계 및 차트</p>
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

        {/* Analytics 데이터 */}
        {!loading && summary && (
          <div className="space-y-6">
            {/* 전체 통계 */}
            <div>
              <h2 className="text-xl font-bold text-gray-900 mb-4">전체 통계</h2>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                <StatsCard
                  icon={Wallet}
                  label="총 주소"
                  value={summary.total_addresses?.toLocaleString() || '0'}
                />
                <StatsCard
                  icon={Package}
                  label="총 클러스터"
                  value={summary.total_clusters?.toLocaleString() || '0'}
                />
                <StatsCard
                  icon={TrendingUp}
                  label="총 트랜잭션"
                  value={summary.total_transactions?.toLocaleString() || '0'}
                />
                <StatsCard
                  icon={BarChart3}
                  label="평균 클러스터 크기"
                  value={summary.avg_cluster_size?.toFixed(2) || '0'}
                />
              </div>
            </div>

            {/* 총 잔액 */}
            <Card>
              <CardHeader>
                <CardTitle>총 잔액</CardTitle>
                <CardDescription>모든 주소의 잔액 합계</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-center py-8">
                  <p className="text-5xl font-bold text-gold-500">
                    {summary.total_balance?.toFixed(4) || '0'}
                  </p>
                  <p className="text-gray-600 mt-2">BTC</p>
                </div>
              </CardContent>
            </Card>

            {/* 최대 클러스터 */}
            {summary.largest_cluster && (
              <Card>
                <CardHeader>
                  <CardTitle>최대 클러스터</CardTitle>
                  <CardDescription>가장 많은 주소를 포함한 클러스터</CardDescription>
                </CardHeader>
                <CardContent>
                  <div
                    className="bg-cream-100 rounded-xl p-6 cursor-pointer hover:bg-cream-200 transition-colors"
                    onClick={() => navigate(`/cluster/${summary.largest_cluster.id}`)}
                  >
                    <p className="text-2xl font-bold text-gray-900 mb-4">
                      {summary.largest_cluster.label || `클러스터 ${summary.largest_cluster.id.substring(0, 8)}...`}
                    </p>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                      <div>
                        <p className="text-gray-500">주소 수</p>
                        <p className="text-xl font-semibold text-gray-900">
                          {summary.largest_cluster.address_count}
                        </p>
                      </div>
                      <div>
                        <p className="text-gray-500">클러스터 ID</p>
                        <p className="text-xs font-mono text-gray-900 break-all">
                          {summary.largest_cluster.id}
                        </p>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}

            {/* 클러스터 크기 분포 차트 */}
            {distribution && Array.isArray(distribution) && distribution.length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle>클러스터 크기 분포</CardTitle>
                  <CardDescription>주소 수에 따른 클러스터 분포</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="h-80 w-full">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={getDistributionChartData()}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#F0EBE0" />
                        <XAxis dataKey="range" stroke="#5D4037" />
                        <YAxis stroke="#5D4037" />
                        <Tooltip
                          contentStyle={{
                            backgroundColor: '#FFF9ED',
                            border: '1px solid #F0EBE0',
                            borderRadius: '8px',
                          }}
                        />
                        <Legend />
                        <Bar dataKey="count" fill="#E67E22" name="클러스터 수" />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        )}
      </main>
    </div>
  );
};
