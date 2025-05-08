import {
  Grid,
  Paper,
  Typography,
  Box,
  Card,
  CardContent,
  Divider,
} from '@mui/material';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';
import { MarketAnalysis } from '../types';

interface PriceAnalysisProps {
  data: MarketAnalysis;
}

function StatCard({ title, value, subtitle }: { title: string; value: string; subtitle?: string }) {
  return (
    <Card elevation={0} sx={{ height: '100%' }}>
      <CardContent>
        <Typography color="text.secondary" gutterBottom>
          {title}
        </Typography>
        <Typography variant="h4" component="div" color="primary">
          {value}
        </Typography>
        {subtitle && (
          <Typography variant="body2" color="text.secondary">
            {subtitle}
          </Typography>
        )}
      </CardContent>
    </Card>
  );
}

function formatPrice(price: number): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
  }).format(price);
}

export default function PriceAnalysis({ data }: PriceAnalysisProps) {
  if (!data) {
    return (
      <Typography variant="body1" color="text.secondary" align="center">
        No analysis data available
      </Typography>
    );
  }

  return (
    <Box>
      <Grid container spacing={3}>
        {/* Key Metrics */}
        <Grid item xs={12} md={4}>
          <StatCard
            title="Average Price"
            value={formatPrice(data.average_price)}
          />
        </Grid>
        <Grid item xs={12} md={4}>
          <StatCard
            title="Median Price"
            value={formatPrice(data.median_price)}
          />
        </Grid>
        <Grid item xs={12} md={4}>
          <StatCard
            title="Price Range"
            value={`${formatPrice(data.price_range.min)} - ${formatPrice(data.price_range.max)}`}
          />
        </Grid>

        {/* Price Segments */}
        <Grid item xs={12}>
          <Paper elevation={0} sx={{ p: 3, mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              Price Segments
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} md={4}>
                <Typography variant="subtitle2" color="text.secondary">
                  Budget
                </Typography>
                <Typography variant="body1">
                  {formatPrice(data.price_segments.budget.min)} - {formatPrice(data.price_segments.budget.max)}
                </Typography>
              </Grid>
              <Grid item xs={12} md={4}>
                <Typography variant="subtitle2" color="text.secondary">
                  Mid-Range
                </Typography>
                <Typography variant="body1">
                  {formatPrice(data.price_segments.mid_range.min)} - {formatPrice(data.price_segments.mid_range.max)}
                </Typography>
              </Grid>
              <Grid item xs={12} md={4}>
                <Typography variant="subtitle2" color="text.secondary">
                  Premium
                </Typography>
                <Typography variant="body1">
                  {formatPrice(data.price_segments.premium.min)} - {formatPrice(data.price_segments.premium.max)}
                </Typography>
              </Grid>
            </Grid>
          </Paper>
        </Grid>

        {/* Brand Price Comparison */}
        <Grid item xs={12}>
          <Paper elevation={0} sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Average Price by Brand
            </Typography>
            <Box sx={{ height: 400 }}>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={data.brand_prices}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="brand" />
                  <YAxis />
                  <Tooltip
                    formatter={(value: number) => formatPrice(value)}
                    labelStyle={{ color: 'black' }}
                  />
                  <Bar dataKey="average_price" fill="#1976d2" />
                </BarChart>
              </ResponsiveContainer>
            </Box>
          </Paper>
        </Grid>

        {/* Price Distribution */}
        <Grid item xs={12}>
          <Paper elevation={0} sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Price Distribution
            </Typography>
            <Box sx={{ height: 300 }}>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={data.price_distribution}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="range" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="count" fill="#4caf50" />
                </BarChart>
              </ResponsiveContainer>
            </Box>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
} 