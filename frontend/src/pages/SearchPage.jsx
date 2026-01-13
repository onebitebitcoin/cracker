/**
 * 검색 페이지
 */
import React, { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { Search } from 'lucide-react';
import {
  Card,
  CardHeader,
  CardTitle,
  CardContent,
  SearchBar,
  LoadingSpinner,
  ErrorAlert,
} from '../components';
import { searchApi } from '../api';

export const SearchPage = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const query = searchParams.get('q') || '';

  useEffect(() => {
    if (query) {
      performSearch(query);
    }
  }, [query]);

  const performSearch = async (searchQuery) => {
    try {
      setLoading(true);
      setError(null);

      // Bitcoin 주소 형식 확인 (1, 3, bc1로 시작)
      const isBitcoinAddress = /^(1|3|bc1)[a-zA-HJ-NP-Z0-9]{25,62}$/.test(searchQuery);

      if (isBitcoinAddress) {
        // Bitcoin 주소인 경우 바로 상세 페이지로 이동
        navigate(`/address/${searchQuery}`);
        return;
      }

      // 그 외의 경우 검색 API 호출
      const data = await searchApi.search(searchQuery);
      setResults(data);
    } catch (err) {
      console.error('검색 실패:', err);
      setError(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (newQuery) => {
    navigate(`/search?q=${encodeURIComponent(newQuery)}`);
  };

  const handleAddressClick = (address) => {
    navigate(`/address/${address}`);
  };

  const handleClusterClick = (clusterId) => {
    navigate(`/cluster/${clusterId}`);
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
          <p className="text-gray-600 mt-1">검색 결과</p>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-8">
        {/* 검색 바 */}
        <Card className="mb-6">
          <SearchBar onSearch={handleSearch} placeholder="주소, 트랜잭션 ID, 클러스터 검색..." />
        </Card>

        {/* 에러 표시 */}
        {error && <ErrorAlert error={error} className="mb-6" />}

        {/* 로딩 중 */}
        {loading && (
          <Card>
            <LoadingSpinner size={48} className="py-12" />
          </Card>
        )}

        {/* 검색 결과 */}
        {!loading && results && (
          <div className="space-y-6">
            {/* 주소 결과 */}
            {results.addresses && results.addresses.length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle>주소 ({results.addresses.length})</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {results.addresses.map((addr) => (
                      <div
                        key={addr.address}
                        className="p-4 bg-cream-100 rounded-lg cursor-pointer hover:bg-cream-200 transition-colors"
                        onClick={() => handleAddressClick(addr.address)}
                      >
                        <p className="font-mono text-sm text-gray-800">{addr.address}</p>
                        <p className="text-sm text-gray-600 mt-1">
                          잔액: {addr.balance} BTC | 트랜잭션: {addr.tx_count}
                        </p>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}

            {/* 클러스터 결과 */}
            {results.clusters && results.clusters.length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle>클러스터 ({results.clusters.length})</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {results.clusters.map((cluster) => (
                      <div
                        key={cluster.id}
                        className="p-4 bg-cream-100 rounded-lg cursor-pointer hover:bg-cream-200 transition-colors"
                        onClick={() => handleClusterClick(cluster.id)}
                      >
                        <p className="font-bold text-gray-800">
                          {cluster.label || `클러스터 ${cluster.id.substring(0, 8)}`}
                        </p>
                        <p className="text-sm text-gray-600 mt-1">
                          주소: {cluster.address_count} | 잔액: {cluster.total_balance} BTC
                        </p>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}

            {/* 트랜잭션 결과 */}
            {results.transactions && results.transactions.length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle>트랜잭션 ({results.transactions.length})</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {results.transactions.map((tx) => (
                      <div key={tx.txid} className="p-4 bg-cream-100 rounded-lg">
                        <p className="font-mono text-sm text-gray-800">{tx.txid}</p>
                        <p className="text-sm text-gray-600 mt-1">
                          블록: {tx.block_height} | 수수료: {tx.fee} BTC
                        </p>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}

            {/* 결과 없음 */}
            {results.addresses?.length === 0 &&
              results.clusters?.length === 0 &&
              results.transactions?.length === 0 && (
                <Card>
                  <CardContent className="py-12 text-center">
                    <Search size={48} className="mx-auto text-gray-400 mb-4" />
                    <p className="text-gray-600">
                      '{query}'에 대한 검색 결과가 없습니다
                    </p>
                  </CardContent>
                </Card>
              )}
          </div>
        )}
      </main>
    </div>
  );
};
