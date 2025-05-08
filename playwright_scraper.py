from playwright.sync_api import sync_playwright
import time
import random
import json
import logging
from typing import Optional, List, Dict

class EbayPlaywrightScraper:
    def __init__(self, headless: bool = True):
        self.setup_logging()
        self.headless = headless
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def setup_browser(self):
        try:
            self.playwright = sync_playwright().start()
            self.browser = self.playwright.chromium.launch(
                headless=self.headless,
                args=['--disable-blink-features=AutomationControlled']
            )
            
            # Create a new context with specific viewport and user agent
            self.context = self.browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            )
            
            # Create a new page
            self.page = self.context.new_page()
            
            # Add custom scripts to make the page look more human-like
            self.page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
            """)
            
            self.logger.info("Browser setup successful")
            
        except Exception as e:
            self.logger.error(f"Error setting up browser: {str(e)}")
            self.cleanup()
            raise

    def cleanup(self):
        try:
            if self.page:
                self.page.close()
            if self.context:
                self.context.close()
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()
        except Exception as e:
            self.logger.error(f"Error during cleanup: {str(e)}")

    def scrape(self, search_query: str, max_items: Optional[int] = None) -> List[Dict]:
        try:
            self.setup_browser()
            
            url = f"https://www.ebay.co.uk/sch/i.html?_nkw={'+'.join(search_query.split())}&_sop=12"
            self.logger.info(f"Scraping URL: {url}")
            
            # Navigate to the page
            self.page.goto(url, wait_until="networkidle")
            
            # Add a random delay to appear more human-like
            time.sleep(random.uniform(2, 4))
            
            # Save the page content for debugging
            with open("debug_response.html", "w", encoding="utf-8") as f:
                f.write(self.page.content())
            
            # Wait for the items to load
            self.page.wait_for_selector("ul.srp-results li.s-item", state="visible")
            
            # Get all items
            items = []
            item_elements = self.page.query_selector_all("li.s-item")
            
            self.logger.info(f"Found {len(item_elements)} items")
            
            # Process items
            for item in item_elements[:max_items if max_items else None]:
                try:
                    item_data = self._extract_item_data(item)
                    if item_data:
                        items.append(item_data)
                        self.logger.info(f"Successfully extracted item: {item_data['title'][:50]}...")
                except Exception as e:
                    self.logger.error(f"Error extracting item data: {str(e)}")
                    continue
                
                # Random delay between processing items
                time.sleep(random.uniform(0.1, 0.3))
            
            self.logger.info(f"Successfully scraped {len(items)} items")
            return items
            
        except Exception as e:
            self.logger.error(f"Error during scraping: {str(e)}")
            return []
        finally:
            self.cleanup()

    def _extract_item_data(self, item) -> Optional[Dict]:
        try:
            # Extract title
            title_element = item.query_selector("div.s-item__title span")
            if not title_element:
                return None
            
            title = title_element.text_content().strip()
            if title.lower() == "shop on ebay":
                return None

            # Extract price
            price_element = item.query_selector("span.s-item__price")
            price = price_element.text_content().strip() if price_element else "Not specified"

            # Extract link
            link_element = item.query_selector("a.s-item__link")
            link = link_element.get_attribute("href") if link_element else None
            if not link:
                return None

            # Extract condition
            condition_element = item.query_selector("span.SECONDARY_INFO")
            condition = condition_element.text_content().strip() if condition_element else "Not specified"

            # Extract shipping
            shipping_element = item.query_selector("span.s-item__shipping")
            shipping = shipping_element.text_content().strip() if shipping_element else "Not specified"

            return {
                "title": title,
                "price": price,
                "condition": condition,
                "shipping": shipping,
                "link": link
            }
        except Exception as e:
            self.logger.error(f"Error extracting item data: {str(e)}")
            return None

if __name__ == "__main__":
    # Example usage
    scraper = EbayPlaywrightScraper(headless=True)
    results = scraper.scrape("iphone 13", max_items=10)
    
    # Save results to a JSON file
    with open("scraping_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"Found {len(results)} items. Results saved to scraping_results.json") 