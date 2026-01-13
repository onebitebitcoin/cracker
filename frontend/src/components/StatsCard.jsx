/**
 * StatsCard 컴포넌트 - 통계 정보 표시
 */
import React from 'react';

export const StatsCard = ({ icon: Icon, label, value, trend, className = '' }) => {
  return (
    <div className={`bg-cream-200 rounded-xl p-4 ${className}`}>
      <div className="flex items-start justify-between">
        {Icon && (
          <div className="bg-gold-400 rounded-lg p-2">
            <Icon className="text-white" size={20} />
          </div>
        )}
        {trend && (
          <span className={`text-sm ${trend > 0 ? 'text-green-600' : 'text-red-600'}`}>
            {trend > 0 ? '↑' : '↓'} {Math.abs(trend)}%
          </span>
        )}
      </div>
      <div className="mt-3">
        <p className="text-xs uppercase text-gray-600 tracking-wide">{label}</p>
        <p className="text-2xl font-bold text-gray-900 mt-1">{value}</p>
      </div>
    </div>
  );
};
