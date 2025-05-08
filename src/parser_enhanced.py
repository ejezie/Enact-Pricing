from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
import os
from dotenv import load_dotenv
import json
import statistics
from decimal import Decimal
from typing import List, Dict, Union, Optional

# Load environment variables
load_dotenv()

class PriceParser:
    @staticmethod
    def extract_numeric_price(price_str: str) -> Optional[Decimal]:
        """
        Extract numeric price from string, handling various formats.
        
        Args:
            price_str (str): Price string to parse
            
        Returns:
            Optional[Decimal]: Parsed price or None if invalid
        """
        try:
            if not price_str or price_str == 'Not specified' or price_str.strip() == '':
                return None
                
            # Handle price ranges by taking the first price (usually the lower price)
            if ' to ' in price_str:
                price_str = price_str.split(' to ')[0]
            
            # Remove currency symbols and any non-numeric characters except decimal point
            numeric_str = ''.join(c for c in price_str if c.isdigit() or c == '.')
            
            # Handle cases where we might have multiple decimal points
            if numeric_str.count('.') > 1:
                numeric_str = numeric_str.replace('.', '', numeric_str.count('.') - 1)
            
            if numeric_str:
                try:
                    return Decimal(numeric_str)
                except:
                    return None
            return None
        except:
            return None

class MarketAnalyzer:
    @staticmethod
    def analyze_prices(products: List[Dict]) -> Dict:
        """
        Analyze prices and generate market insights.
        
        Args:
            products (List[Dict]): List of product dictionaries
            
        Returns:
            Dict: Market analysis results
        """
        if not products:
            return MarketAnalyzer._get_empty_analysis()

        # Extract valid prices
        prices = []
        for product in products:
            price = PriceParser.extract_numeric_price(product.get('price', ''))
            if price is not None:
                prices.append(float(price))
                product['numeric_price'] = float(price)
            else:
                product['numeric_price'] = 0

        if not prices:
            return MarketAnalyzer._get_empty_analysis()

        # Calculate statistics
        avg_price = statistics.mean(prices)
        median_price = statistics.median(prices)
        
        try:
            price_std = statistics.stdev(prices)
        except:
            price_std = avg_price * 0.2  # Use 20% of average as fallback

        # Calculate brand averages
        brand_averages = MarketAnalyzer._calculate_brand_averages(products)

        # Calculate price segments
        budget_threshold = max(0, avg_price - price_std)
        premium_threshold = avg_price + price_std

        return {
            'market_stats': {
                'average_price': round(avg_price, 2),
                'median_price': round(median_price, 2),
                'price_std': round(price_std, 2),
                'price_range': {
                    'min': round(float(min(prices)), 2),
                    'max': round(float(max(prices)), 2)
                }
            },
            'brand_averages': brand_averages,
            'price_segments': {
                'budget': round(budget_threshold, 2),
                'mid_range': round(avg_price, 2),
                'premium': round(premium_threshold, 2)
            }
        }

    @staticmethod
    def _get_empty_analysis() -> Dict:
        """Return empty analysis structure when no data is available."""
        return {
            'market_stats': {
                'average_price': 0,
                'median_price': 0,
                'price_std': 0,
                'price_range': {
                    'min': 0,
                    'max': 0
                }
            },
            'brand_averages': {},
            'price_segments': {
                'budget': 0,
                'mid_range': 0,
                'premium': 0
            }
        }

    @staticmethod
    def _calculate_brand_averages(products: List[Dict]) -> Dict:
        """Calculate average prices by brand."""
        brand_prices = {}
        for product in products:
            brand = product.get('brand', 'Not specified')
            if brand != 'Not specified' and product.get('numeric_price', 0) > 0:
                if brand not in brand_prices:
                    brand_prices[brand] = []
                brand_prices[brand].append(product['numeric_price'])

        return {
            brand: sum(prices) / len(prices)
            for brand, prices in brand_prices.items()
        }

class RecommendationGenerator:
    @staticmethod
    def generate_price_recommendations(product_data: List[Dict], market_analysis: Dict) -> List[str]:
        """
        Generate pricing recommendations based on market analysis.
        
        Args:
            product_data (List[Dict]): List of product dictionaries
            market_analysis (Dict): Market analysis results
            
        Returns:
            List[str]: List of recommendations
        """
        if not market_analysis:
            return ["Insufficient data for price analysis."]

        stats = market_analysis['market_stats']
        segments = market_analysis['price_segments']
        
        recommendations = [
            "Market Overview:",
            f"• Average market price: £{stats['average_price']}",
            f"• Price range: £{stats['price_range']['min']} - £{stats['price_range']['max']}",
            
            "\nPrice Segments:",
            f"• Budget segment: Below £{segments['budget']}",
            f"• Mid-range segment: Around £{segments['mid_range']}",
            f"• Premium segment: Above £{segments['premium']}"
        ]
        
        # Brand-specific insights
        if market_analysis['brand_averages']:
            recommendations.extend([
                "\nBrand Positioning:",
                *[f"• {brand}: Average price £{round(avg_price, 2)}"
                  for brand, avg_price in market_analysis['brand_averages'].items()]
            ])
        
        # Strategic recommendations
        recommendations.extend([
            "\nStrategic Recommendations:",
            "• For competitive pricing: Set prices slightly below the market average",
            "• For premium positioning: Price 10-15% above the market average",
            "• For market penetration: Consider pricing at the lower segment"
        ])
        
        return recommendations

class ContentParser:
    def __init__(self):
        """Initialize the content parser with OpenAI API key."""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OpenAI API key not found in environment variables")
        
        self.api_key = api_key
        self.model = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0,
            api_key=api_key
        )

    def parse_with_llm(self, dom_chunks: List[str], parse_description: str) -> Dict:
        """
        Parse scraped content using LLM.
        
        Args:
            dom_chunks (List[str]): List of HTML content chunks
            parse_description (str): Description of parsing task
            
        Returns:
            Dict: Parsed results with products, analysis, and recommendations
        """
        template = self._get_parse_template()
        prompt = ChatPromptTemplate.from_template(template)
        chain = prompt | self.model
        
        all_results = []
        
        for i, chunk in enumerate(dom_chunks, start=1):
            try:
                response = chain.invoke({
                    "dom_content": chunk,
                    "parse_description": parse_description
                })
                print(f"Parsed batch: {i} of {len(dom_chunks)}")
                
                products = json.loads(str(response.content))
                all_results.extend(products)
            except json.JSONDecodeError:
                print(f"Warning: Could not parse response as JSON in batch {i}")
                continue
            except Exception as e:
                print(f"Error processing batch {i}: {str(e)}")
                continue

        # Perform market analysis
        market_analysis = MarketAnalyzer.analyze_prices(all_results)
        
        # Generate recommendations
        recommendations = RecommendationGenerator.generate_price_recommendations(
            all_results, market_analysis
        )

        return {
            'products': all_results,
            'market_analysis': market_analysis,
            'recommendations': recommendations
        }

    @staticmethod
    def _get_parse_template() -> str:
        """Get the template for parsing product information."""
        return (
            "You are tasked with extracting specific information from the following text content: {dom_content}. "
            "Please follow these instructions carefully: \n\n"
            "1. Extract product information and format it as a JSON array of objects with these fields: product_name, seller, price, brand, country\n"
            "2. Each object should have all fields, use 'Not specified' if a field is missing\n"
            "3. Return ONLY the JSON array, no other text\n"
            "4. Make sure the JSON is valid and properly formatted\n"
            "5. For prices, include the currency symbol and handle price ranges (e.g., '£99.99' or '£10 to £20')\n"
            "6. For brands:\n"
            "   - Look for brand names in product titles, descriptions, or dedicated brand fields\n"
            "   - Common brand indicators include: 'by [brand]', 'brand:', 'manufacturer:', 'made by'\n"
            "   - If a brand is mentioned multiple times, use the most prominent one\n"
            "   - Do not use seller names as brands unless explicitly stated\n"
            "   - If no clear brand is found, use 'Not specified'\n"
            "7. For sellers:\n"
            "   - Use the actual seller/retailer name\n"
            "   - If the seller is the same as the brand, still list it as the seller\n"
            "Example format:\n"
            '[{{"product_name": "Example Product", "seller": "Example Seller", "price": "£99.99", "brand": "Example Brand", "country": "UK"}}]'
        )

class ChatbotAssistant:
    def __init__(self):
        """Initialize the chatbot assistant with OpenAI API key."""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OpenAI API key not found in environment variables")
        
        self.api_key = api_key
        self.chat_model = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.7,
            api_key=api_key
        )

    def generate_response(self, user_question: str, product_data: List[Dict] = None, market_analysis: Dict = None) -> str:
        """
        Generate AI assistant responses based on market data.
        
        Args:
            user_question (str): User's question
            product_data (List[Dict], optional): Product data
            market_analysis (Dict, optional): Market analysis results
            
        Returns:
            str: Generated response
        """
        if not product_data:
            return "Please analyze some market data first before asking questions."
        
        # Create summaries and prompt
        product_summary = self._create_product_summary(product_data, market_analysis)
        market_summary = self._create_market_summary(market_analysis)
        prompt = self._create_chat_prompt(product_summary, market_summary, user_question)
        
        # Generate response
        chain = prompt | self.chat_model
        response = chain.invoke({
            "product_summary": product_summary,
            "market_summary": market_summary,
            "question": user_question
        })
        
        return response.content

    @staticmethod
    def _create_product_summary(product_data: List[Dict], market_analysis: Dict) -> str:
        """Create a summary of the product data."""
        summary = f"Products analyzed: {len(product_data)}\n"
        if product_data and len(product_data) > 0:
            brands = set([p.get('brand', 'Unknown') for p in product_data if p.get('brand') != 'Not specified'])
            price_range = f"Price range: £{market_analysis['market_stats']['price_range']['min']} - £{market_analysis['market_stats']['price_range']['max']}"
            avg_price = f"Average price: £{market_analysis['market_stats']['average_price']}"
            summary += f"Brands: {', '.join(brands)}\n{price_range}\n{avg_price}"
        return summary

    @staticmethod
    def _create_market_summary(market_analysis: Dict) -> str:
        """Create a summary of the market analysis."""
        if not market_analysis:
            return ""
            
        return f"""
        Average Price: £{market_analysis['market_stats']['average_price']}
        Median Price: £{market_analysis['market_stats']['median_price']}
        Price Range: £{market_analysis['market_stats']['price_range']['min']} - £{market_analysis['market_stats']['price_range']['max']}
        Budget Segment: Below £{market_analysis['price_segments']['budget']}
        Mid-Range: £{market_analysis['price_segments']['mid_range']}
        Premium Segment: Above £{market_analysis['price_segments']['premium']}
        """

    @staticmethod
    def _create_chat_prompt(product_summary: str, market_summary: str, question: str) -> ChatPromptTemplate:
        """Create the chat prompt template."""
        template = """
        You are a helpful e-commerce market analysis assistant. You have access to the following product data:
        
        {product_summary}
        
        Market Analysis Summary:
        {market_summary}
        
        User Question: {question}
        
        Please provide a helpful, concise, and accurate response based on this data.
        """
        return ChatPromptTemplate.from_template(template) 