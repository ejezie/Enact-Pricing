import os
from typing import List, Dict, Any
import openai
from statistics import mean, median

# Initialize OpenAI client
openai.api_key = os.getenv("OPENAI_API_KEY")

def parse_with_llm(content_chunks: List[str], instruction: str) -> Dict[str, Any]:
    """Parse content using LLM and extract structured data."""
    all_products = []
    
    for chunk in content_chunks:
        # Create prompt for product extraction
        prompt = f"""
        {instruction}
        Extract the following information from the eBay product listings:
        - Product name
        - Price (in GBP)
        - Brand (if available)
        - Seller name
        - Condition
        - Shipping cost
        
        Format the data as a list of JSON objects.
        
        Content:
        {chunk}
        """
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that extracts structured data from eBay product listings."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1500
            )
            
            # Parse the response and add to products list
            products = parse_llm_response(response.choices[0].message.content)
            all_products.extend(products)
            
        except Exception as e:
            print(f"Error processing chunk: {str(e)}")
            continue
    
    # Generate market analysis
    market_analysis = analyze_market_data(all_products)
    
    # Generate recommendations
    recommendations = generate_recommendations(market_analysis)
    
    return {
        "products": all_products,
        "market_analysis": market_analysis,
        "recommendations": recommendations
    }

def parse_llm_response(response_text: str) -> List[Dict[str, Any]]:
    """Parse LLM response and convert to structured data."""
    try:
        # Use another LLM call to ensure proper JSON formatting
        formatting_prompt = f"""
        Convert this text into a valid JSON array of product objects:
        {response_text}
        """
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that formats text as valid JSON."},
                {"role": "user", "content": formatting_prompt}
            ],
            temperature=0.1
        )
        
        # Evaluate the response as Python code (safe since we're using GPT to format it)
        products = eval(response.choices[0].message.content)
        return products
        
    except Exception as e:
        print(f"Error parsing LLM response: {str(e)}")
        return []

def analyze_market_data(products: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze product data and generate market insights."""
    if not products:
        return {
            "market_stats": {
                "average_price": 0,
                "median_price": 0,
                "price_range": {"min": 0, "max": 0}
            },
            "price_segments": {
                "budget": 0,
                "mid_range": 0,
                "premium": 0
            },
            "brand_averages": {}
        }
    
    # Extract prices
    prices = [float(str(p['price']).replace('£', '').replace(',', '')) for p in products if 'price' in p]
    
    if not prices:
        return {
            "market_stats": {
                "average_price": 0,
                "median_price": 0,
                "price_range": {"min": 0, "max": 0}
            },
            "price_segments": {
                "budget": 0,
                "mid_range": 0,
                "premium": 0
            },
            "brand_averages": {}
        }
    
    # Calculate basic statistics
    avg_price = mean(prices)
    med_price = median(prices)
    min_price = min(prices)
    max_price = max(prices)
    
    # Calculate price segments
    price_range = max_price - min_price
    budget_threshold = min_price + (price_range * 0.3)
    premium_threshold = max_price - (price_range * 0.3)
    
    # Calculate brand averages
    brand_prices = {}
    for product in products:
        if 'brand' in product and product['brand']:
            brand = product['brand']
            price = float(str(product['price']).replace('£', '').replace(',', ''))
            
            if brand not in brand_prices:
                brand_prices[brand] = []
            brand_prices[brand].append(price)
    
    brand_averages = {
        brand: mean(prices)
        for brand, prices in brand_prices.items()
    }
    
    return {
        "market_stats": {
            "average_price": avg_price,
            "median_price": med_price,
            "price_range": {
                "min": min_price,
                "max": max_price
            }
        },
        "price_segments": {
            "budget": budget_threshold,
            "mid_range": (budget_threshold + premium_threshold) / 2,
            "premium": premium_threshold
        },
        "brand_averages": brand_averages
    }

def generate_recommendations(market_analysis: Dict[str, Any]) -> List[str]:
    """Generate pricing and market recommendations."""
    recommendations = []
    
    # Add market overview
    recommendations.append("\nMarket Overview")
    recommendations.append(f"• The average price in the market is £{market_analysis['market_stats']['average_price']:.2f}")
    recommendations.append(f"• The median price is £{market_analysis['market_stats']['median_price']:.2f}")
    recommendations.append(f"• Prices range from £{market_analysis['market_stats']['price_range']['min']:.2f} to £{market_analysis['market_stats']['price_range']['max']:.2f}")
    
    # Add price segment recommendations
    recommendations.append("\nPrice Segments")
    recommendations.append(f"• Budget segment: Below £{market_analysis['price_segments']['budget']:.2f}")
    recommendations.append(f"• Mid-range segment: Around £{market_analysis['price_segments']['mid_range']:.2f}")
    recommendations.append(f"• Premium segment: Above £{market_analysis['price_segments']['premium']:.2f}")
    
    # Add brand insights
    if market_analysis['brand_averages']:
        recommendations.append("\nBrand Insights")
        sorted_brands = sorted(
            market_analysis['brand_averages'].items(),
            key=lambda x: x[1],
            reverse=True
        )
        for brand, price in sorted_brands[:5]:
            recommendations.append(f"• {brand}: Average price £{price:.2f}")
    
    # Add strategic recommendations
    recommendations.append("\nStrategic Recommendations")
    
    # Price positioning
    if market_analysis['market_stats']['median_price'] > market_analysis['market_stats']['average_price']:
        recommendations.append("• The market shows premium pricing opportunities, consider positioning in the upper segments")
    else:
        recommendations.append("• The market is price-sensitive, consider competitive pricing strategies")
    
    # Competition
    price_range = market_analysis['market_stats']['price_range']['max'] - market_analysis['market_stats']['price_range']['min']
    if price_range > market_analysis['market_stats']['average_price']:
        recommendations.append("• Wide price range indicates diverse market segments, consider multi-tier pricing")
    else:
        recommendations.append("• Narrow price range suggests standardized pricing, focus on value-added features")
    
    return recommendations

def generate_chatbot_response(question: str, product_data: List[Dict[str, Any]], market_analysis: Dict[str, Any]) -> str:
    """Generate AI response to user questions about market data."""
    # Create context for the AI
    context = f"""
    You are a market analysis expert. Use this data to answer the user's question:
    
    Market Statistics:
    - Average Price: £{market_analysis['market_stats']['average_price']:.2f}
    - Median Price: £{market_analysis['market_stats']['median_price']:.2f}
    - Price Range: £{market_analysis['market_stats']['price_range']['min']:.2f} to £{market_analysis['market_stats']['price_range']['max']:.2f}
    
    Price Segments:
    - Budget: Below £{market_analysis['price_segments']['budget']:.2f}
    - Mid-Range: Around £{market_analysis['price_segments']['mid_range']:.2f}
    - Premium: Above £{market_analysis['price_segments']['premium']:.2f}
    
    Number of Products Analyzed: {len(product_data)}
    
    User Question: {question}
    """
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful market analysis expert providing insights about eBay product data."},
                {"role": "user", "content": context}
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        return f"I apologize, but I encountered an error while analyzing the data: {str(e)}" 