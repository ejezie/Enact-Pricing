import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random
import json
import logging
import os

class EbaySeleniumScraper:
    def __init__(self, headless=True):
        self.setup_logging()
        self.setup_driver(headless)

    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def setup_driver(self, headless):
        try:
            options = uc.ChromeOptions()
            options.add_argument('--start-maximized')
            
            if headless:
                options.add_argument('--headless')
            
            # Create an instance of Chrome with undetected-chromedriver
            self.driver = uc.Chrome(
                options=options,
                driver_executable_path=None,  # Let it auto-detect
                browser_executable_path=None,  # Let it auto-detect
                suppress_welcome=True
            )
            
            self.wait = WebDriverWait(self.driver, 15)  # Increased wait time
            self.logger.info("Chrome driver setup successful")
            
        except Exception as e:
            self.logger.error(f"Error creating undetected Chrome driver: {str(e)}")
            raise

    def scrape(self, search_query, max_items=None):
        try:
            url = f"https://www.ebay.co.uk/sch/i.html?_nkw={'+'.join(search_query.split())}&_sop=12"
            self.logger.info(f"Scraping URL: {url}")
            
            self.driver.get(url)
            time.sleep(random.uniform(3, 5))  # Increased delay
            
            # Wait for the main container of items to load
            self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "ul.srp-results")))
            
            # Save the page source for debugging
            with open("debug_response.html", "w", encoding="utf-8") as f:
                f.write(self.driver.page_source)
            
            # Wait a bit more after the page loads
            time.sleep(random.uniform(2, 3))
            
            items = []
            item_elements = self.driver.find_elements(By.CSS_SELECTOR, "li.s-item")
            
            self.logger.info(f"Found {len(item_elements)} items")
            
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
                time.sleep(random.uniform(0.2, 0.5))  # Increased delay
            
            self.logger.info(f"Successfully scraped {len(items)} items")
            return items
            
        except Exception as e:
            self.logger.error(f"Error during scraping: {str(e)}")
            return []
        finally:
            try:
                self.driver.quit()
            except:
                pass

    def _extract_item_data(self, item):
        try:
            # Extract title
            title_element = item.find_element(By.CSS_SELECTOR, "div.s-item__title span")
            title = title_element.text.strip()
            if title.lower() == "shop on ebay":
                return None

            # Extract price
            price_element = item.find_element(By.CSS_SELECTOR, "span.s-item__price")
            price = price_element.text.strip()

            # Extract link
            link_element = item.find_element(By.CSS_SELECTOR, "a.s-item__link")
            link = link_element.get_attribute("href")

            # Extract condition
            try:
                condition_element = item.find_element(By.CSS_SELECTOR, "span.SECONDARY_INFO")
                condition = condition_element.text.strip()
            except:
                condition = "Not specified"

            # Extract shipping
            try:
                shipping_element = item.find_element(By.CSS_SELECTOR, "span.s-item__shipping")
                shipping = shipping_element.text.strip()
            except:
                shipping = "Not specified"

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
    scraper = EbaySeleniumScraper(headless=True)
    results = scraper.scrape("iphone 13", max_items=10)
    
    # Save results to a JSON file
    with open("scraping_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"Found {len(results)} items. Results saved to scraping_results.json") 