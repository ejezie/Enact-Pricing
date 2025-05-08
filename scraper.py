import requests
from bs4 import BeautifulSoup
from urllib.parse import urlencode, quote_plus
import re
from typing import List, Dict, Optional, Union
from dotenv import load_dotenv
import os
import time
import random
import json
import logging
from fake_useragent import UserAgent
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EbayScraper:
    def __init__(self):
        self.session = self._create_session()
        self.user_agent = UserAgent()
        self.base_url = "https://www.ebay.co.uk/sch/i.html"
        self.rate_limit_delay = float(os.getenv("RATE_LIMIT_DELAY", "2"))
        self.max_retries = int(os.getenv("MAX_RETRIES", "3"))
        self.timeout = int(os.getenv("REQUEST_TIMEOUT", "30"))
        
    def _create_session(self) -> requests.Session:
        """Create a session with retry mechanism."""
        session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session
    
    def _get_random_headers(self) -> Dict[str, str]:
        """Generate random headers to avoid detection."""
        return {
            "User-Agent": self.user_agent.random,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Connection": "keep-alive",
        }
    
    def construct_ebay_search_url(self, search_query: str, sort_by: str = "Best Match") -> str:
        """Construct eBay search URL with parameters."""
        sort_map = {
            "Best Match": "12",
            "Price + Shipping: Lowest First": "15",
            "Price + Shipping: Highest First": "16",
            "Time: Newly Listed": "10",
        }
        
        params = {
            "_nkw": search_query,
            "_sop": sort_map.get(sort_by, "12")
        }
        
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"{self.base_url}?{query_string}"
    
    def scrape(self, search_query: str, sort_by: str = "Best Match", results_limit: int = 10) -> List[Dict]:
        """
        Scrape eBay search results with error handling and rate limiting.
        """
        url = self.construct_ebay_search_url(search_query, sort_by)
        logger.info(f"Scraping URL: {url}")
        
        try:
            # Add random delay to avoid detection
            time.sleep(random.uniform(self.rate_limit_delay, self.rate_limit_delay + 1))
            
            response = self.session.get(
                url,
                headers=self._get_random_headers(),
                timeout=self.timeout
            )
            response.raise_for_status()
            
            # Parse the response
            soup = BeautifulSoup(response.text, "lxml")
            items = self._parse_items(soup, results_limit)
            
            if not items:
                logger.warning("No items found in the search results")
                return []
            
            return items
            
        except requests.RequestException as e:
            logger.error(f"Request failed: {str(e)}")
            raise Exception(f"Failed to scrape website: {str(e)}")
        except Exception as e:
            logger.error(f"Scraping error: {str(e)}")
            raise Exception(f"Failed to scrape data: {str(e)}")
    
    def _parse_items(self, soup: BeautifulSoup, limit: int) -> List[Dict]:
        """Parse product items from the search results."""
        items = []
        results = soup.select('li.s-item')
        
        for item in results[:limit]:
            try:
                # Get basic item information
                title_elem = item.select_one('.s-item__title')
                price_elem = item.select_one('.s-item__price')
                link_elem = item.select_one('.s-item__link')
                condition_elem = item.select_one('.SECONDARY_INFO')
                
                if not all([title_elem, price_elem, link_elem]):
                    continue
                
                # Clean up the data
                title = title_elem.text.strip()
                if title.lower() == 'shop on ebay':
                    continue
                    
                price = price_elem.text.strip()
                link = link_elem.get('href', '')
                condition = condition_elem.text.strip() if condition_elem else "Not specified"
                
                items.append({
                    'title': title,
                    'price': price,
                    'condition': condition,
                    'link': link
                })
                
            except Exception as e:
                logger.warning(f"Failed to parse item: {str(e)}")
                continue
        
        return items
    
    def _extract_price(self, price_text: str) -> float:
        """Extract numeric price from price text."""
        try:
            # Remove currency symbol and convert to float
            price = price_text.replace("£", "").replace(",", "")
            return float(price.split(" to ")[0])  # Handle price ranges
        except (ValueError, IndexError):
            return 0.0
    
    def _get_total_results(self, soup: BeautifulSoup) -> int:
        """Extract total number of results."""
        try:
            total_text = soup.select_one(".srp-controls__count-heading").get_text(strip=True)
            return int(''.join(filter(str.isdigit, total_text)))
        except (AttributeError, ValueError):
            return 0

# Initialize scraper
scraper = EbayScraper()

def scrape_website(url: str) -> str:
    """Scrape website content."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        raise Exception(f"Failed to scrape website: {str(e)}")

def extract_body_content(html_content: str) -> str:
    """Extract main content from HTML."""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Remove script and style elements
    for script in soup(['script', 'style']):
        script.decompose()
    
    # Find the main content area (adjust selectors based on eBay's structure)
    main_content = soup.find('div', {'id': 'mainContent'})
    if not main_content:
        main_content = soup.find('div', {'id': 'srp-river-results'})  # Backup selector
    
    return str(main_content) if main_content else str(soup.body)

def clean_body_content(content: str) -> str:
    """Clean and normalize HTML content."""
    # Remove HTML comments
    content = re.sub(r'<!--.*?-->', '', content, flags=re.DOTALL)
    
    # Remove excessive whitespace
    content = re.sub(r'\s+', ' ', content)
    
    # Remove inline styles and scripts
    content = re.sub(r'style="[^"]*"', '', content)
    content = re.sub(r'onclick="[^"]*"', '', content)
    
    return content.strip()

def split_dom_content(content: str, max_chunk_size: int = 8000) -> List[str]:
    """Split content into manageable chunks for LLM processing."""
    # Use BeautifulSoup to parse the content
    soup = BeautifulSoup(content, 'html.parser')
    
    chunks = []
    current_chunk = []
    current_size = 0
    
    for element in soup.find_all(['div', 'li', 'section']):
        element_text = element.get_text(strip=True)
        element_size = len(element_text)
        
        if current_size + element_size > max_chunk_size:
            if current_chunk:
                chunks.append(' '.join(current_chunk))
            current_chunk = [element_text]
            current_size = element_size
        else:
            current_chunk.append(element_text)
            current_size += element_size
    
    if current_chunk:
        chunks.append(' '.join(current_chunk))
    
    return chunks 