/**
 * 주소 상세 페이지
 */
import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Wallet, Package, TrendingUp, TrendingDown, ExternalLink } from 'lucide-react';
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
import { TransactionList } from '../components/TransactionList';
import { addressesApi } from '../api';

export const AddressDetailPage = () => {
  const { address } = useParams();
  const navigate = useNavigate();

  const [addressData, setAddressData] = useState(null);
  const [clusterData, setClusterData] = useState(null);
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [txPagination, setTxPagination] = useState({
    page: 1,
    page_size: 10,
    total: 0,
    total_pages: 0,
  });

  useEffect(() => {
    if (address) {
      loadAddressData();
    }
  }, [address]);

  const loadAddressData = async () => {
    try {
      setLoading(true);
      setError(null);

      // 주소 정보, 클러스터 정보, 트랜잭션 병렬로 로드
      const [addrData, clusterInfo, txData] = await Promise.all([
        addressesApi.getAddress(address),
        addressesApi.getAddressCluster(address).catch(() => null),
        addressesApi.getAddressTransactions(address, { limit: 10, offset: 0 }),
      ]);

      setAddressData(addrData);
      setClusterData(clusterInfo);
      setTransactions(txData.data || []);
      setTxPagination({
        page: txData.page || 1,
        page_size: txData.page_size || 10,
        total: txData.total || 0,
        total_pages: txData.total_pages || 0,
      });
    } catch (err) {
      console.error('주소 데이터 로드 실패:', err);
      setError(err);
    } finally {
      setLoading(false);
    }
  };

  const loadMoreTransactions = async (offset) => {
    try {
      const txData = await addressesApi.getAddressTransactions(address, {
        limit: 10,
        offset,
      });
      setTransactions(txData.data || []);
      setTxPagination({
        page: txData.page || 1,
        page_size: txData.page_size || 10,
        total: txData.total || 0,
        total_pages: txData.total_pages || 0,
      });
    } catch (err) {
      console.error('트랜잭션 로드 실패:', err);
    }
  };

  const handleNextPage = () => {
    if (txPagination.page < txPagination.total_pages) {
      loadMoreTransactions(txPagination.page * txPagination.page_size);
    }
  };

  const handlePrevPage = () => {
    if (txPagination.page > 1) {
      loadMoreTransactions((txPagination.page - 2) * txPagination.page_size);
    }
  };

  const handleClusterClick = () => {
    if (clusterData?.cluster_id) {
      navigate(`/cluster/${clusterData.cluster_id}`);
    }
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
          <h1 className="text-3xl font-bold text-gray-900">주소 상세</h1>
          <p className="text-gray-600 mt-1 font-mono text-sm break-all">
            {address}
          </p>
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

        {/* 주소 데이터 표시 */}
        {!loading && addressData && (
          <div className="space-y-6">
            {/* 통계 카드 */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              <StatsCard
                icon={Wallet}
                label="잔액"
                value={`${addressData.balance?.toFixed(4) || '0'} BTC`}
              />
              <StatsCard
                icon={TrendingDown}
                label="총 수신"
                value={`${addressData.total_received?.toFixed(4) || '0'} BTC`}
              />
              <StatsCard
                icon={TrendingUp}
                label="총 송신"
                value={`${addressData.total_sent?.toFixed(4) || '0'} BTC`}
              />
              <StatsCard
                icon={Package}
                label="트랜잭션 수"
                value={addressData.tx_count || 0}
              />
            </div>

            {/* 클러스터 정보 */}
            {clusterData && clusterData.cluster_id && (
              <Card>
                <CardHeader>
                  <CardTitle>클러스터 정보</CardTitle>
                  <CardDescription>이 주소가 속한 클러스터</CardDescription>
                </CardHeader>
                <CardContent>
                  <div
                    className="bg-cream-100 rounded-xl p-4 cursor-pointer hover:bg-cream-200 transition-colors"
                    onClick={handleClusterClick}
                  >
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="font-bold text-gray-900 mb-2">
                          {clusterData.cluster_label || `클러스터 ${clusterData.cluster_id.substring(0, 8)}...`}
                        </p>
                        <div className="flex gap-4 text-sm text-gray-600">
                          <span>주소: {clusterData.cluster_address_count}</span>
                          <span>잔액: {clusterData.cluster_balance?.toFixed(4) || '0'} BTC</span>
                        </div>
                      </div>
                      <ExternalLink className="text-gray-400" size={20} />
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}

            {/* 트랜잭션 히스토리 */}
            <Card>
              <CardHeader>
                <CardTitle>트랜잭션 히스토리</CardTitle>
                <CardDescription>
                  총 {txPagination.total}개 (페이지 {txPagination.page} / {txPagination.total_pages})
                </CardDescription>
              </CardHeader>
              <CardContent>
                <TransactionList transactions={transactions} currentAddress={address} />

                {/* Pagination */}
                {txPagination.total_pages > 1 && (
                  <div className="flex justify-between items-center mt-6 pt-6 border-t border-cream-300">
                    <Button
                      variant="outline"
                      onClick={handlePrevPage}
                      disabled={txPagination.page <= 1}
                    >
                      이전
                    </Button>
                    <span className="text-sm text-gray-600">
                      페이지 {txPagination.page} / {txPagination.total_pages}
                    </span>
                    <Button
                      variant="outline"
                      onClick={handleNextPage}
                      disabled={txPagination.page >= txPagination.total_pages}
                    >
                      다음
                    </Button>
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
