import React, { useState, useEffect } from 'react';
import axios from 'axios';
import {
  Container,
  Box,
  Typography,
  TextField,
  Button,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Grid,
  Card,
  CardContent,
  CardHeader,
  Tabs,
  Tab,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  CircularProgress,
  Slider,
  Divider,
  Alert,
  IconButton,
  Snackbar,
} from '@mui/material';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Cell,
} from 'recharts';
import { 
  Search as SearchIcon, 
  Send as SendIcon,
  Delete as DeleteIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';

const API_URL = 'http://localhost:8000';

// Website options
const WEBSITE_OPTIONS = [
  { value: 'eBay', label: 'eBay' },
  { value: 'Amazon', label: 'Amazon' },
  { value: 'Custom URL', label: 'Custom URL' }
];

// Sorting options
const SORT_OPTIONS = [
  { value: 'Best Match', label: 'Best Match' },
  { value: 'Lowest Price', label: 'Lowest Price' },
  { value: 'Highest Price', label: 'Highest Price' },
  { value: 'Most Recent', label: 'Most Recent' },
  { value: 'Most Relevant', label: 'Most Relevant' }
];

function App() {
  // State management
  const [websiteChoice, setWebsiteChoice] = useState('eBay');
  const [baseUrl, setBaseUrl] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [sortBy, setSortBy] = useState('Best Match');
  const [resultsLimit, setResultsLimit] = useState(50);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [analysisResults, setAnalysisResults] = useState(null);
  const [tabValue, setTabValue] = useState(0);
  const [chatInput, setChatInput] = useState('');
  const [chatHistory, setChatHistory] = useState([]);
  const [notification, setNotification] = useState({ open: false, message: '', severity: 'info' });

  // Handle tab change
  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };

  // Clear chat history
  const clearChat = () => {
    setChatHistory([]);
    showNotification('Chat history cleared', 'info');
  };

  // Handle submit of scraping form
  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    // Validate input
    if (websiteChoice === 'Custom URL' && !baseUrl) {
      setError('Please enter a valid URL');
      setLoading(false);
      return;
    }

    if (websiteChoice !== 'Custom URL' && !searchQuery) {
      setError('Please enter a search query');
      setLoading(false);
      return;
    }

    try {
      const response = await axios.post(`${API_URL}/api/scrape`, {
        website_choice: websiteChoice,
        base_url: baseUrl,
        search_query: searchQuery,
        sort_by: sortBy,
        results_limit: resultsLimit,
      });

      setAnalysisResults(response.data);
      showNotification('Analysis completed successfully', 'success');
      // Auto-switch to the Market Overview tab
      setTabValue(0);
    } catch (err) {
      console.error('Error during scraping:', err);
      setError(err.response?.data?.detail || 'An error occurred during scraping');
      showNotification('Error during scraping', 'error');
    } finally {
      setLoading(false);
    }
  };

  // Show notification
  const showNotification = (message, severity = 'info') => {
    setNotification({
      open: true,
      message,
      severity,
    });
  };

  // Close notification
  const handleCloseNotification = () => {
    setNotification({
      ...notification,
      open: false,
    });
  };

  // Send chat message
  const sendChatMessage = async () => {
    if (!chatInput.trim() || !analysisResults) return;

    // Add user message to chat history
    const userMessage = { role: 'user', content: chatInput };
    setChatHistory([...chatHistory, userMessage]);
    
    // Clear input
    setChatInput('');

    try {
      const response = await axios.post(`${API_URL}/api/chat`, {
        question: chatInput,
        product_data: analysisResults.products,
        market_analysis: analysisResults.market_analysis,
      });

      // Add AI response to chat history
      const aiMessage = { role: 'assistant', content: response.data.response };
      setChatHistory(prevChat => [...prevChat, aiMessage]);
    } catch (err) {
      console.error('Error sending chat message:', err);
      // Add error message to chat
      const errorMessage = { 
        role: 'system', 
        content: 'Sorry, there was an error processing your question. Please try again.' 
      };
      setChatHistory(prevChat => [...prevChat, errorMessage]);
    }
  };

  // Prepare data for brand price chart
  const getBrandChartData = () => {
    if (!analysisResults?.market_analysis?.brand_averages) return [];
    
    return Object.entries(analysisResults.market_analysis.brand_averages)
      .map(([brand, price]) => ({
        brand,
        price: parseFloat(price.toFixed(2))
      }))
      .sort((a, b) => a.price - b.price);
  };

  // Format price for display
  const formatPrice = (price) => {
    return `£${parseFloat(price).toFixed(2)}`;
  };

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      {/* Header */}
      <Box sx={{ mb: 4, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
        <Typography variant="h3" component="h1" gutterBottom>
          Price Intelligence Tool
        </Typography>
        <Typography variant="subtitle1" color="text.secondary" align="center" sx={{ mb: 2 }}>
          Monitor prices, analyze market data, and optimize your pricing strategy
        </Typography>
      </Box>

      {/* Search Form */}
      <Paper 
        component="form" 
        onSubmit={handleSubmit}
        elevation={3}
        sx={{ p: 3, mb: 4 }}
      >
        <Typography variant="h6" gutterBottom>
          Search Parameters
        </Typography>
        
        <Grid container spacing={3}>
          {/* Website Choice */}
          <Grid item xs={12} md={6}>
            <FormControl fullWidth variant="outlined">
              <InputLabel id="website-choice-label">Website</InputLabel>
              <Select
                labelId="website-choice-label"
                id="website-choice"
                value={websiteChoice}
                onChange={(e) => setWebsiteChoice(e.target.value)}
                label="Website"
              >
                {WEBSITE_OPTIONS.map((option) => (
                  <MenuItem key={option.value} value={option.value}>
                    {option.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>

          {/* Custom URL Input */}
          {websiteChoice === 'Custom URL' && (
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Website URL"
                variant="outlined"
                value={baseUrl}
                onChange={(e) => setBaseUrl(e.target.value)}
                placeholder="Enter website URL"
                required
              />
            </Grid>
          )}

          {/* Search Query */}
          {websiteChoice !== 'Custom URL' && (
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Search Query"
                variant="outlined"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Enter product name or keywords"
                required
                InputProps={{
                  startAdornment: <SearchIcon color="action" sx={{ mr: 1 }} />,
                }}
              />
            </Grid>
          )}
          
          {/* Sort By */}
          <Grid item xs={12} md={6}>
            <FormControl fullWidth variant="outlined">
              <InputLabel id="sort-label">Sort By</InputLabel>
              <Select
                labelId="sort-label"
                id="sort"
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                label="Sort By"
              >
                {SORT_OPTIONS.map((option) => (
                  <MenuItem key={option.value} value={option.value}>
                    {option.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          
          {/* Results Limit */}
          <Grid item xs={12}>
            <Typography id="results-limit-label" gutterBottom>
              Maximum Results: {resultsLimit}
            </Typography>
            <Slider
              value={resultsLimit}
              onChange={(e, newValue) => setResultsLimit(newValue)}
              aria-labelledby="results-limit-label"
              valueLabelDisplay="auto"
              step={10}
              marks
              min={10}
              max={100}
            />
          </Grid>
          
          {/* Submit Button */}
          <Grid item xs={12}>
            <Button
              type="submit"
              variant="contained"
              color="primary"
              size="large"
              fullWidth
              disabled={loading}
              startIcon={loading ? <CircularProgress size={24} /> : <SearchIcon />}
            >
              {loading ? 'Analyzing Prices...' : 'Analyze Prices'}
            </Button>
          </Grid>
        </Grid>
      </Paper>

      {/* Error Message */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {/* Results */}
      {analysisResults && (
        <Box sx={{ mb: 4 }}>
          <Paper elevation={3} sx={{ mb: 2 }}>
            <Tabs
              value={tabValue}
              onChange={handleTabChange}
              indicatorColor="primary"
              textColor="primary"
              variant="fullWidth"
            >
              <Tab label="Market Overview" />
              <Tab label="Price Analysis" />
              <Tab label="Recommendations" />
              <Tab label="AI Assistant" />
            </Tabs>
          </Paper>

          {/* Tab Content */}
          <Paper elevation={3} sx={{ p: 3 }}>
            {/* Market Overview Tab */}
            {tabValue === 0 && (
              <>
                <Typography variant="h6" gutterBottom>
                  Products Found: {analysisResults.products.length}
                </Typography>
                <TableContainer component={Paper} elevation={0} sx={{ mb: 3 }}>
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>Product Name</TableCell>
                        <TableCell>Price</TableCell>
                        <TableCell>Brand</TableCell>
                        <TableCell>Seller</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {analysisResults.products.map((product, index) => (
                        <TableRow key={index}>
                          <TableCell>{product.product_name}</TableCell>
                          <TableCell>{product.price}</TableCell>
                          <TableCell>{product.brand}</TableCell>
                          <TableCell>{product.seller}</TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              </>
            )}

            {/* Price Analysis Tab */}
            {tabValue === 1 && (
              <>
                <Grid container spacing={3}>
                  {/* Market Statistics */}
                  <Grid item xs={12}>
                    <Card elevation={2} sx={{ mb: 3 }}>
                      <CardHeader title="Market Statistics" />
                      <CardContent>
                        <Grid container spacing={3}>
                          <Grid item xs={12} md={4}>
                            <Typography variant="subtitle2" color="text.secondary">Average Price</Typography>
                            <Typography variant="h5">{formatPrice(analysisResults.market_analysis.market_stats.average_price)}</Typography>
                          </Grid>
                          <Grid item xs={12} md={4}>
                            <Typography variant="subtitle2" color="text.secondary">Median Price</Typography>
                            <Typography variant="h5">{formatPrice(analysisResults.market_analysis.market_stats.median_price)}</Typography>
                          </Grid>
                          <Grid item xs={12} md={4}>
                            <Typography variant="subtitle2" color="text.secondary">Price Range</Typography>
                            <Typography variant="h5">
                              {formatPrice(analysisResults.market_analysis.market_stats.price_range.min)} - {formatPrice(analysisResults.market_analysis.market_stats.price_range.max)}
                            </Typography>
                          </Grid>
                        </Grid>
                      </CardContent>
                    </Card>
                  </Grid>

                  {/* Price Distribution */}
                  <Grid item xs={12} md={6}>
                    <Card elevation={2}>
                      <CardHeader title="Price Distribution" />
                      <CardContent>
                        <ResponsiveContainer width="100%" height={300}>
                          <PieChart>
                            <Pie
                              data={[
                                { name: 'Budget', value: analysisResults.market_analysis.price_segments.budget },
                                { name: 'Mid-Range', value: analysisResults.market_analysis.price_segments.mid_range },
                                { name: 'Premium', value: analysisResults.market_analysis.price_segments.premium }
                              ]}
                              cx="50%"
                              cy="50%"
                              labelLine={false}
                              label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                              outerRadius={80}
                              fill="#8884d8"
                              dataKey="value"
                            >
                              <Cell fill="#4CAF50" />
                              <Cell fill="#FFC107" />
                              <Cell fill="#F44336" />
                            </Pie>
                            <Tooltip formatter={(value) => formatPrice(value)} />
                            <Legend />
                          </PieChart>
                        </ResponsiveContainer>
                      </CardContent>
                    </Card>
                  </Grid>

                  {/* Brand Comparison */}
                  <Grid item xs={12} md={6}>
                    <Card elevation={2}>
                      <CardHeader title="Brand Price Comparison" />
                      <CardContent>
                        <ResponsiveContainer width="100%" height={300}>
                          <BarChart
                            data={getBrandChartData()}
                            margin={{ top: 20, right: 30, left: 20, bottom: 70 }}
                          >
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis
                              dataKey="brand"
                              angle={-45}
                              textAnchor="end"
                              height={70}
                            />
                            <YAxis
                              label={{ value: 'Average Price (£)', angle: -90, position: 'insideLeft' }}
                            />
                            <Tooltip formatter={(value) => formatPrice(value)} />
                            <Legend />
                            <Bar dataKey="price" name="Average Price" fill="#2196F3" />
                          </BarChart>
                        </ResponsiveContainer>
                      </CardContent>
                    </Card>
                  </Grid>
                </Grid>
              </>
            )}

            {/* Recommendations Tab */}
            {tabValue === 2 && (
              <Box>
                <Typography variant="h6" gutterBottom>
                  Market Recommendations
                </Typography>
                {analysisResults.recommendations.map((rec, index) => (
                  <Box key={index} sx={{ mb: 2 }}>
                    {rec.startsWith('\n') ? (
                      <>
                        <Divider sx={{ my: 2 }} />
                        <Typography variant="subtitle1" fontWeight="bold">
                          {rec.trim()}
                        </Typography>
                      </>
                    ) : rec.startsWith('•') ? (
                      <Typography variant="body1" sx={{ ml: 2 }}>
                        {rec}
                      </Typography>
                    ) : (
                      <Typography variant="body1">
                        {rec}
                      </Typography>
                    )}
                  </Box>
                ))}
              </Box>
            )}

            {/* AI Assistant Tab */}
            {tabValue === 3 && (
              <Box>
                <Typography variant="h6" gutterBottom>
                  AI Market Analysis Assistant
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  Ask questions about the market data and get AI-powered insights.
                </Typography>

                {/* Chat History */}
                <Paper 
                  elevation={0} 
                  variant="outlined" 
                  sx={{ 
                    p: 2, 
                    mb: 2, 
                    height: '350px', 
                    overflowY: 'auto',
                    backgroundColor: '#f5f5f5'
                  }}
                >
                  {chatHistory.length === 0 ? (
                    <Box sx={{ 
                      height: '100%', 
                      display: 'flex', 
                      alignItems: 'center', 
                      justifyContent: 'center',
                      flexDirection: 'column',
                      color: 'text.secondary'
                    }}>
                      <Typography variant="body2" align="center">
                        No messages yet. Ask a question about your market analysis.
                      </Typography>
                      <Typography variant="body2" align="center" sx={{ mt: 1 }}>
                        Examples: "What's the best price point?", "How do I compare to competitors?"
                      </Typography>
                    </Box>
                  ) : (
                    chatHistory.map((message, index) => (
                      <Box 
                        key={index} 
                        sx={{ 
                          display: 'flex', 
                          justifyContent: message.role === 'user' ? 'flex-end' : 'flex-start',
                          mb: 2
                        }}
                      >
                        <Paper 
                          elevation={1} 
                          sx={{ 
                            p: 2, 
                            maxWidth: '70%', 
                            backgroundColor: message.role === 'user' ? '#e3f2fd' : '#fff',
                            borderRadius: '10px',
                          }}
                        >
                          <Typography variant="body2">
                            {message.content}
                          </Typography>
                        </Paper>
                      </Box>
                    ))
                  )}
                </Paper>

                {/* Chat Input */}
                <Box sx={{ display: 'flex', gap: 2 }}>
                  <TextField
                    fullWidth
                    variant="outlined"
                    placeholder="Ask a question about the market analysis..."
                    value={chatInput}
                    onChange={(e) => setChatInput(e.target.value)}
                    onKeyPress={(e) => {
                      if (e.key === 'Enter' && !e.shiftKey) {
                        e.preventDefault();
                        sendChatMessage();
                      }
                    }}
                  />
                  <Button
                    variant="contained"
                    color="primary"
                    onClick={sendChatMessage}
                    disabled={!chatInput.trim() || !analysisResults}
                    startIcon={<SendIcon />}
                  >
                    Send
                  </Button>
                  <IconButton
                    color="error"
                    onClick={clearChat}
                    disabled={chatHistory.length === 0}
                  >
                    <DeleteIcon />
                  </IconButton>
                </Box>
              </Box>
            )}
          </Paper>
        </Box>
      )}

      {/* Notification Snackbar */}
      <Snackbar
        open={notification.open}
        autoHideDuration={6000}
        onClose={handleCloseNotification}
      >
        <Alert 
          onClose={handleCloseNotification} 
          severity={notification.severity}
          sx={{ width: '100%' }}
        >
          {notification.message}
        </Alert>
      </Snackbar>
    </Container>
  );
}

export default App; 