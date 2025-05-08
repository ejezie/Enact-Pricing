'use client';

import React from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Divider,
  List,
  ListItem,
  ListItemText,
} from '@mui/material';

interface MarketAnalysisProps {
  marketAnalysis: {
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
  };
  recommendations: string[];
}

export default function MarketAnalysis({ marketAnalysis, recommendations }: MarketAnalysisProps) {
  if (!marketAnalysis || !recommendations) {
    return null;
  }

  const { market_stats, brand_averages, price_segments } = marketAnalysis;

  return (
    <Box sx={{ mt: 4 }}>
      <Typography variant="h5" gutterBottom>
        Market Analysis
      </Typography>
      <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
        {/* Market Statistics */}
        <Card sx={{ flex: 1, minWidth: 300 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Market Statistics
            </Typography>
            <List dense>
              <ListItem>
                <ListItemText
                  primary="Average Price"
                  secondary={`£${market_stats.average_price.toFixed(2)}`}
                />
              </ListItem>
              <ListItem>
                <ListItemText
                  primary="Median Price"
                  secondary={`£${market_stats.median_price.toFixed(2)}`}
                />
              </ListItem>
              <ListItem>
                <ListItemText
                  primary="Price Range"
                  secondary={`£${market_stats.price_range.min.toFixed(2)} - £${market_stats.price_range.max.toFixed(2)}`}
                />
              </ListItem>
            </List>
          </CardContent>
        </Card>

        {/* Price Segments */}
        <Card sx={{ flex: 1, minWidth: 300 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Price Segments
            </Typography>
            <List dense>
              <ListItem>
                <ListItemText
                  primary="Budget"
                  secondary={`Below £${price_segments.budget.toFixed(2)}`}
                />
              </ListItem>
              <ListItem>
                <ListItemText
                  primary="Mid Range"
                  secondary={`Around £${price_segments.mid_range.toFixed(2)}`}
                />
              </ListItem>
              <ListItem>
                <ListItemText
                  primary="Premium"
                  secondary={`Above £${price_segments.premium.toFixed(2)}`}
                />
              </ListItem>
            </List>
          </CardContent>
        </Card>

        {/* Brand Averages */}
        {Object.keys(brand_averages).length > 0 && (
          <Card sx={{ flex: 1, minWidth: 300 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Brand Averages
              </Typography>
              <List dense>
                {Object.entries(brand_averages).map(([brand, price]) => (
                  <ListItem key={brand}>
                    <ListItemText
                      primary={brand}
                      secondary={`£${price.toFixed(2)}`}
                    />
                  </ListItem>
                ))}
              </List>
            </CardContent>
          </Card>
        )}
      </Box>

      {/* Recommendations */}
      <Card sx={{ mt: 2 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Recommendations
          </Typography>
          <List dense>
            {recommendations.map((recommendation, index) => (
              <ListItem key={index}>
                <ListItemText primary={recommendation} />
              </ListItem>
            ))}
          </List>
        </CardContent>
      </Card>
    </Box>
  );
} 