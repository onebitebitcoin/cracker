/**
 * Input 컴포넌트
 */
import React from 'react';

export const Input = ({
  type = 'text',
  placeholder = '',
  value,
  onChange,
  className = '',
  icon: Icon,
  ...props
}) => {
  return (
    <div className="relative">
      {Icon && (
        <div className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400">
          <Icon size={20} />
        </div>
      )}
      <input
        type={type}
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        className={`w-full px-4 ${Icon ? 'pl-10' : ''} py-3 bg-cream-200 border border-cream-300 rounded-xl
          focus:outline-none focus:ring-2 focus:ring-gold-400 focus:border-transparent
          placeholder-gray-500 text-gray-800 transition-all ${className}`}
        {...props}
      />
    </div>
  );
};
