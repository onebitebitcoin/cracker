/**
 * Card 컴포넌트
 *
 * CRITICAL: Card 내부에 Card를 중첩하지 말 것
 */
import React from 'react';

export const Card = ({ children, className = '', ...props }) => {
  return (
    <div
      className={`bg-white rounded-2xl shadow-sm border border-cream-300 p-6 ${className}`}
      {...props}
    >
      {children}
    </div>
  );
};

export const CardHeader = ({ children, className = '', ...props }) => {
  return (
    <div className={`mb-4 ${className}`} {...props}>
      {children}
    </div>
  );
};

export const CardTitle = ({ children, className = '', ...props }) => {
  return (
    <h2 className={`text-2xl font-bold text-gray-900 ${className}`} {...props}>
      {children}
    </h2>
  );
};

export const CardDescription = ({ children, className = '', ...props }) => {
  return (
    <p className={`text-sm text-gray-600 mt-1 ${className}`} {...props}>
      {children}
    </p>
  );
};

export const CardContent = ({ children, className = '', ...props }) => {
  return (
    <div className={className} {...props}>
      {children}
    </div>
  );
};
