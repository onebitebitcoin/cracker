/**
 * ErrorAlert 컴포넌트
 */
import React from 'react';
import { AlertCircle } from 'lucide-react';

export const ErrorAlert = ({ error, className = '' }) => {
  if (!error) return null;

  const message = typeof error === 'string' ? error : error.message;
  const detail = typeof error === 'object' ? error.detail : null;

  return (
    <div className={`bg-red-50 border-l-4 border-red-500 p-4 rounded ${className}`}>
      <div className="flex items-start">
        <AlertCircle className="text-red-500 mt-0.5 flex-shrink-0" size={20} />
        <div className="ml-3">
          <p className="font-bold text-red-800">{message}</p>
          {detail && import.meta.env.DEV && (
            <p className="text-sm text-red-700 mt-1">{detail}</p>
          )}
        </div>
      </div>
    </div>
  );
};
