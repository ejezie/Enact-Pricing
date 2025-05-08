export interface Product {
  title: string;
  price: string;
  url: string;
  condition?: string;
  location?: string;
  brand?: string;
  seller?: string;
}

export interface SearchForm {
  search_query: string;
  sort_by: string;
  category: number;
  location: string;
  condition: string;
  results_limit: number;
}

export interface MarketAnalysis {
  average_price: number;
  median_price: number;
  price_range: {
    min: number;
    max: number;
  };
  price_segments: {
    budget: { min: number; max: number };
    mid_range: { min: number; max: number };
    premium: { min: number; max: number };
  };
  brand_prices: {
    brand: string;
    average_price: number;
  }[];
  price_distribution: {
    range: string;
    count: number;
  }[];
}

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

export interface Recommendation {
  type: 'pricing' | 'strategy' | 'competitor';
  title: string;
  description: string;
  impact: 'high' | 'medium' | 'low';
} 