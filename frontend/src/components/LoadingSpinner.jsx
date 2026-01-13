/**
 * LoadingSpinner 컴포넌트
 */
import React from 'react';
import { Loader2 } from 'lucide-react';

export const LoadingSpinner = ({ size = 24, className = '' }) => {
  return (
    <div className={`flex items-center justify-center ${className}`}>
      <Loader2 size={size} className="animate-spin text-gold-500" />
    </div>
  );
};
