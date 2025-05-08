'use client';

import React, { useState } from 'react';
import {
  Box,
  Button,
  Grid,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Alert,
  CircularProgress,
} from '@mui/material';

interface SearchFormProps {
  onSearch: (results: any) => void;
}

export default function SearchForm({ onSearch }: SearchFormProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const [sortBy, setSortBy] = useState('Best Match');
  const [resultsLimit, setResultsLimit] = useState(10);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/scrape', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          search_query: searchQuery,
          sort_by: sortBy,
          results_limit: resultsLimit,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      onSearch(data); // Pass the entire response object to handle market analysis
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred while searching');
      onSearch({ items: [], market_analysis: null, recommendations: [] });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Box component="form" onSubmit={handleSubmit} sx={{ width: '100%', mt: 3 }}>
      <Grid container spacing={2} alignItems="center">
        <Grid item xs={12} sm={4}>
          <TextField
            fullWidth
            label="Search Query *"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            required
            variant="outlined"
            disabled={isLoading}
          />
        </Grid>
        <Grid item xs={12} sm={4}>
          <FormControl fullWidth variant="outlined">
            <InputLabel>Sort By</InputLabel>
            <Select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              label="Sort By"
              disabled={isLoading}
            >
              <MenuItem value="Best Match">Best Match</MenuItem>
              <MenuItem value="Price + Shipping: Lowest First">Price: Low to High</MenuItem>
              <MenuItem value="Price + Shipping: Highest First">Price: High to Low</MenuItem>
              <MenuItem value="Time: Newly Listed">Newly Listed</MenuItem>
            </Select>
          </FormControl>
        </Grid>
        <Grid item xs={12} sm={2}>
          <TextField
            fullWidth
            label="Results Limit"
            type="number"
            value={resultsLimit}
            onChange={(e) => setResultsLimit(Number(e.target.value))}
            InputProps={{ inputProps: { min: 1, max: 100 } }}
            variant="outlined"
            disabled={isLoading}
          />
        </Grid>
        <Grid item xs={12} sm={2}>
          <Button
            type="submit"
            variant="contained"
            color="primary"
            fullWidth
            disabled={isLoading}
            sx={{ height: '56px' }}
          >
            {isLoading ? (
              <CircularProgress size={24} color="inherit" />
            ) : (
              'SEARCH'
            )}
          </Button>
        </Grid>
      </Grid>

      {error && (
        <Box mt={2}>
          <Alert severity="error">{error}</Alert>
        </Box>
      )}
    </Box>
  );
} 