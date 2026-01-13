/**
 * Button 컴포넌트
 */
import React from 'react';

export const Button = ({
  children,
  variant = 'primary',
  size = 'md',
  disabled = false,
  className = '',
  ...props
}) => {
  const baseStyles = 'rounded-xl font-medium transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-offset-2';

  const variants = {
    primary: 'bg-gold-500 hover:bg-gold-600 text-white focus:ring-gold-400',
    secondary: 'bg-cream-300 hover:bg-cream-400 text-gray-800 focus:ring-cream-400',
    outline: 'border-2 border-gold-500 text-gold-600 hover:bg-gold-50 focus:ring-gold-400',
  };

  const sizes = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2 text-base',
    lg: 'px-6 py-3 text-lg',
  };

  const disabledStyles = disabled
    ? 'opacity-50 cursor-not-allowed'
    : 'cursor-pointer';

  return (
    <button
      className={`${baseStyles} ${variants[variant]} ${sizes[size]} ${disabledStyles} ${className}`}
      disabled={disabled}
      {...props}
    >
      {children}
    </button>
  );
};
