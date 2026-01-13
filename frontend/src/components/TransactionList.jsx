/**
 * TransactionList 컴포넌트
 */
import React from 'react';
import { ArrowDownLeft, ArrowUpRight, Clock } from 'lucide-react';

export const TransactionList = ({ transactions, currentAddress }) => {
  if (!transactions || transactions.length === 0) {
    return (
      <div className="py-8 text-center text-gray-500">
        트랜잭션이 없습니다
      </div>
    );
  }

  const formatDate = (timestamp) => {
    if (!timestamp) return '-';
    const date = new Date(timestamp);
    return date.toLocaleString('ko-KR', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <div className="space-y-3">
      {transactions.map((tx) => (
        <div
          key={tx.txid}
          className="bg-cream-100 rounded-xl p-4 hover:bg-cream-200 transition-colors"
        >
          {/* 트랜잭션 ID */}
          <div className="flex items-start justify-between mb-3">
            <div className="flex-1">
              <p className="text-xs text-gray-500 uppercase tracking-wide mb-1">
                Transaction ID
              </p>
              <p className="font-mono text-sm text-gray-800 break-all">
                {tx.txid}
              </p>
            </div>
          </div>

          {/* 트랜잭션 정보 */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
            <div>
              <p className="text-gray-500 mb-1">블록 높이</p>
              <p className="font-semibold text-gray-900">
                {tx.block_height || '-'}
              </p>
            </div>
            <div>
              <p className="text-gray-500 mb-1">입력</p>
              <p className="font-semibold text-gray-900">
                {tx.input_count || 0}
              </p>
            </div>
            <div>
              <p className="text-gray-500 mb-1">출력</p>
              <p className="font-semibold text-gray-900">
                {tx.output_count || 0}
              </p>
            </div>
            <div>
              <p className="text-gray-500 mb-1">수수료</p>
              <p className="font-semibold text-gray-900">
                {tx.fee ? `${tx.fee.toFixed(8)} BTC` : '-'}
              </p>
            </div>
          </div>

          {/* 시간 */}
          {tx.timestamp && (
            <div className="mt-3 pt-3 border-t border-cream-300 flex items-center text-sm text-gray-600">
              <Clock size={14} className="mr-1" />
              {formatDate(tx.timestamp)}
            </div>
          )}
        </div>
      ))}
    </div>
  );
};
