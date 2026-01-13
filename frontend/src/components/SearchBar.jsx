/**
 * SearchBar 컴포넌트
 */
import React, { useState } from 'react';
import { Search } from 'lucide-react';
import { Input } from './Input';
import { Button } from './Button';

export const SearchBar = ({ onSearch, placeholder = '주소, 트랜잭션 ID, 클러스터 검색...' }) => {
  const [query, setQuery] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (query.trim()) {
      onSearch(query.trim());
    }
  };

  return (
    <form onSubmit={handleSubmit} className="flex gap-2">
      <div className="flex-1">
        <Input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder={placeholder}
          icon={Search}
        />
      </div>
      <Button type="submit" variant="primary" size="md">
        검색
      </Button>
    </form>
  );
};
