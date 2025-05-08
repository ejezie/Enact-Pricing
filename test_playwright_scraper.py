from playwright_scraper import EbayPlaywrightScraper
import json

def main():
    print("Starting eBay scraper test...")
    
    # Initialize scraper in headless mode
    scraper = EbayPlaywrightScraper(headless=True)
    
    # Test search for iPhone 13
    search_query = "iphone 13"
    print(f"\nSearching for: {search_query}")
    
    # Limit to 5 items for testing
    results = scraper.scrape(search_query, max_items=5)
    
    # Print results
    print(f"\nFound {len(results)} items:")
    for idx, item in enumerate(results, 1):
        print(f"\nItem {idx}:")
        print(f"Title: {item['title']}")
        print(f"Price: {item['price']}")
        print(f"Condition: {item['condition']}")
        print(f"Shipping: {item['shipping']}")
        print(f"Link: {item['link']}")
    
    # Save results to JSON
    with open("test_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print("\nTest results have been saved to test_results.json")

if __name__ == "__main__":
    main() 