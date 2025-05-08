'use client';

import React, { createContext, useContext, useState } from 'react';

interface Product {
  title: string;
  price: string;
  condition: string;
  link: string;
}

interface SearchContextType {
  results: Product[] | null;
  isLoading: boolean;
  error: string | null;
  setResults: (results: Product[] | null) => void;
  setIsLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
}

const SearchContext = createContext<SearchContextType | undefined>(undefined);

export function SearchProvider({ children }: { children: React.ReactNode }) {
  const [results, setResults] = useState<Product[] | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  return (
    <SearchContext.Provider
      value={{
        results,
        isLoading,
        error,
        setResults,
        setIsLoading,
        setError,
      }}
    >
      {children}
    </SearchContext.Provider>
  );
}

export function useSearch() {
  const context = useContext(SearchContext);
  if (context === undefined) {
    throw new Error('useSearch must be used within a SearchProvider');
  }
  return context;
} 