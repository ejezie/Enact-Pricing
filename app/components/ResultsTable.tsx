'use client';

import React from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Link,
  Typography,
  Box
} from '@mui/material';
import { useSearch } from '../contexts/SearchContext';

interface Product {
  title: string;
  price: string;
  condition: string;
  link: string;
  country: string;
}

export default function ResultsTable() {
  const { results, isLoading, error } = useSearch();

  if (isLoading) {
    return (
      <Box sx={{ mt: 4, textAlign: 'center' }}>
        <Typography>Loading results...</Typography>
      </Box>
    );
  }

  if (error) {
    return (
      <Box sx={{ mt: 4, textAlign: 'center' }}>
        <Typography color="error">{error}</Typography>
      </Box>
    );
  }

  if (!Array.isArray(results) || results.length === 0) {
    return (
      <Box sx={{ mt: 4, textAlign: 'center' }}>
        <Typography>No results found. Try searching for something!</Typography>
      </Box>
    );
  }

  // Map of country codes to full names
  const countryNames: { [key: string]: string } = {
    'UK': 'United Kingdom',
    'US': 'United States',
    'AU': 'Australia',
    'CA': 'Canada',
    'DE': 'Germany',
    'FR': 'France',
    'IT': 'Italy',
    'ES': 'Spain'
  };

  return (
    <TableContainer component={Paper} sx={{ mt: 4 }}>
      <Table aria-label="product results">
        <TableHead>
          <TableRow>
            <TableCell>Title</TableCell>
            <TableCell>Price</TableCell>
            <TableCell>Condition</TableCell>
            <TableCell>Country</TableCell>
            <TableCell>Action</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {results.map((product: Product, index: number) => (
            <TableRow key={index}>
              <TableCell>{product.title}</TableCell>
              <TableCell>{product.price}</TableCell>
              <TableCell>{product.condition}</TableCell>
              <TableCell>{countryNames[product.country] || product.country}</TableCell>
              <TableCell>
                <Link href={product.link} target="_blank" rel="noopener noreferrer">
                  View on eBay
                </Link>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
} 