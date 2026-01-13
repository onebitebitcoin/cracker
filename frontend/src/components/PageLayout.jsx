/**
 * PageLayout 공통 컴포넌트
 */
import React from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import { Button } from './Button';

export const PageLayout = ({
  title,
  subtitle,
  showBackButton = true,
  children,
}) => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-cream-100">
      {/* Header */}
      <header className="bg-white border-b border-cream-300 px-4 py-6">
        <div className="max-w-7xl mx-auto">
          {showBackButton && (
            <Button
              variant="outline"
              size="sm"
              onClick={() => navigate(-1)}
              className="mb-4"
            >
              <ArrowLeft size={16} className="mr-2" />
              뒤로 가기
            </Button>
          )}
          <h1 className="text-3xl font-bold text-gray-900">{title}</h1>
          {subtitle && (
            <p className="text-gray-600 mt-1 break-all">{subtitle}</p>
          )}
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-8">
        {children}
      </main>
    </div>
  );
};
