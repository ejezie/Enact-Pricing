import asyncio
import json
from scraper_enhanced import scraper
import logging

# Set logging level to DEBUG
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

async def test_scraper():
    try:
        # Test with a simple search query
        print("Testing AI-enhanced scraper...")
        results = await scraper.scrape(
            search_query="iphone 13",
            sort_by="Best Match",
            results_limit=2  # Limiting to 2 results for testing
        )
        
        # Pretty print the results
        print("\nScraping Results:")
        print(json.dumps(results, indent=2, ensure_ascii=False))
        
        if results:
            print("\n✅ Scraper test successful!")
            print(f"Found {len(results)} items")
            
            # Check if AI features are working
            first_item = results[0]
            if first_item.get('features') and any(first_item['features'].values()):
                print("✅ AI feature extraction is working")
            else:
                print("⚠️ AI feature extraction might not be enabled (check OPENAI_API_KEY)")
                
            if isinstance(first_item.get('price'), dict) and 'normalized_price' in first_item['price']:
                print("✅ AI price normalization is working")
            else:
                print("⚠️ AI price normalization might not be enabled")
                
            if isinstance(first_item.get('condition'), dict) and 'standardized_condition' in first_item['condition']:
                print("✅ AI condition analysis is working")
            else:
                print("⚠️ AI condition analysis might not be enabled")
        else:
            print("\n⚠️ No results found")
            
    except Exception as e:
        print(f"\n❌ Error during testing: {str(e)}")
        logger.exception("Detailed error information:")

if __name__ == "__main__":
    asyncio.run(test_scraper()) 