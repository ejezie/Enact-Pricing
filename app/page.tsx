'use client';

import React, { useState } from 'react';
import { Container, Typography, Box } from '@mui/material';
import SearchForm from './components/SearchForm';
import ResultsList from './components/ResultsList';
import MarketAnalysis from './components/MarketAnalysis';

interface SearchResult {
  title: string;
  price: string;
  condition: string;
  shipping: string;
  link: string;
}

interface MarketStats {
  market_stats: {
    average_price: number;
    median_price: number;
    price_std: number;
    price_range: {
      min: number;
      max: number;
    };
  };
  brand_averages: Record<string, number>;
  price_segments: {
    budget: number;
    mid_range: number;
    premium: number;
  };
}

export default function Home() {
  const [results, setResults] = useState<SearchResult[]>([]);
  const [marketAnalysis, setMarketAnalysis] = useState<MarketStats | null>(null);
  const [recommendations, setRecommendations] = useState<string[]>([]);
  const [error, setError] = useState<string | null>(null);

  const handleSearch = async (searchResults: any) => {
    if (searchResults.items) {
      setResults(searchResults.items);
      setMarketAnalysis(searchResults.market_analysis);
      setRecommendations(searchResults.recommendations || []);
      setError(null);
    } else {
      setResults([]);
      setMarketAnalysis(null);
      setRecommendations([]);
      setError('No results found');
    }
  };

  return (
    <Container maxWidth="lg">
      <Box sx={{ my: 4 }}>
        <Typography variant="h3" component="h1" gutterBottom align="center">
          eBay Price Scraper
        </Typography>
        <SearchForm onSearch={handleSearch} />
        {error && (
          <Typography color="error" sx={{ mt: 2 }}>
            {error}
          </Typography>
        )}
        {results.length > 0 && (
          <>
            <ResultsList results={results} />
            {marketAnalysis && recommendations && (
              <MarketAnalysis
                marketAnalysis={marketAnalysis}
                recommendations={recommendations}
              />
            )}
          </>
        )}
      </Box>
    </Container>
  );
} 