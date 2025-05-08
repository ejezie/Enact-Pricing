from bs4 import BeautifulSoup
import requests
from dotenv import load_dotenv
import os
import time
import random
from urllib.parse import urlparse, urljoin, quote_plus
import openai
from typing import List, Dict, Optional, Union
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from fake_useragent import UserAgent
import json
from dataclasses import dataclass
from price_parser import Price
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ProductFeatures:
    brand: Optional[str] = None
    model: Optional[str] = None
    color: Optional[str] = None
    size: Optional[str] = None
    material: Optional[str] = None
    specifications: Dict[str, str] = None

class AIEnhancedScraper:
    def __init__(self):
        self.session = self._create_session()
        self.user_agent = UserAgent()
        self.base_url = "https://www.ebay.co.uk/sch/i.html"
        self.rate_limit_delay = float(os.getenv("RATE_LIMIT_DELAY", "2"))
        self.max_retries = int(os.getenv("MAX_RETRIES", "3"))
        self.timeout = int(os.getenv("REQUEST_TIMEOUT", "30"))
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        
        if not self.openai_api_key:
            logger.warning("OpenAI API key not found. AI features will be disabled.")
        else:
            openai.api_key = self.openai_api_key

    def _create_session(self) -> requests.Session:
        """Create a session with retry mechanism."""
        session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session

    async def extract_product_features(self, title: str, description: str) -> ProductFeatures:
        """Use AI to extract structured product features from title and description."""
        if not self.openai_api_key:
            return ProductFeatures()

        try:
            prompt = f"""
            Extract product features from the following eBay listing:
            Title: {title}
            Description: {description}

            Please extract the following information in JSON format:
            - brand
            - model
            - color
            - size
            - material
            - specifications (key-value pairs of other important details)
            """

            response = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a product information extraction expert."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=300
            )

            features = json.loads(response.choices[0].message.content)
            return ProductFeatures(**features)

        except Exception as e:
            logger.error(f"Error extracting product features: {str(e)}")
            return ProductFeatures()

    async def normalize_price(self, price_text: str, title: str) -> Dict[str, Union[float, str]]:
        """Use AI to normalize price and identify special offers."""
        if not self.openai_api_key:
            return {"amount": self._extract_basic_price(price_text), "currency": "GBP"}

        try:
            prompt = f"""
            Analyze the following price and title from an eBay listing:
            Price: {price_text}
            Title: {title}

            Please extract in JSON format:
            - normalized_price (numeric value)
            - currency
            - has_discount (boolean)
            - original_price (if discounted)
            - shipping_cost (if mentioned)
            """

            response = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a price analysis expert."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=150
            )

            return json.loads(response.choices[0].message.content)

        except Exception as e:
            logger.error(f"Error normalizing price: {str(e)}")
            return {"amount": self._extract_basic_price(price_text), "currency": "GBP"}

    def _extract_basic_price(self, price_text: str) -> float:
        """Basic price extraction without AI."""
        price = Price.fromstring(price_text)
        return float(price.amount) if price.amount else 0.0

    async def categorize_condition(self, condition_text: str, title: str, description: str) -> Dict[str, str]:
        """Use AI to analyze and categorize item condition more accurately."""
        if not self.openai_api_key:
            return {"condition": condition_text}

        try:
            prompt = f"""
            Analyze the following eBay item condition:
            Condition: {condition_text}
            Title: {title}
            Description: {description}

            Please provide in JSON format:
            - standardized_condition (New/Like New/Very Good/Good/Acceptable/For Parts)
            - condition_details (specific details about the condition)
            - signs_of_wear (if applicable)
            - defects (if any)
            """

            response = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a product condition assessment expert."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=200
            )

            return json.loads(response.choices[0].message.content)

        except Exception as e:
            logger.error(f"Error categorizing condition: {str(e)}")
            return {"condition": condition_text}

    async def scrape(self, search_query: str, sort_by: str = "Best Match", results_limit: int = 10) -> List[Dict]:
        """Enhanced scraping with AI-powered feature extraction."""
        url = self.construct_ebay_search_url(search_query, sort_by)
        logger.info(f"Scraping URL: {url}")

        try:
            # Add random delay between requests
            time.sleep(random.uniform(self.rate_limit_delay, self.rate_limit_delay + 2))
            
            session = self._create_session()
            
            # First request to get cookies
            response = session.get(
                "https://www.ebay.co.uk",
                headers=self._get_random_headers(),
                timeout=self.timeout
            )
            response.raise_for_status()
            
            # Small delay between requests
            time.sleep(random.uniform(1, 2))
            
            # Main request with cookies
            response = session.get(
                url,
                headers=self._get_random_headers(),
                timeout=self.timeout
            )
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "lxml")
            logger.debug(f"Response status code: {response.status_code}")
            logger.debug(f"Page title: {soup.title.string if soup.title else 'No title found'}")
            
            # Save HTML for debugging
            with open("debug_response.html", "w", encoding="utf-8") as f:
                f.write(response.text)
            logger.info("Saved response HTML to debug_response.html")
            
            items = await self._parse_items_enhanced(soup, results_limit)
            
            if not items:
                logger.warning("No items found in the search results")
                logger.debug(f"Number of item wrappers found: {len(soup.select('.s-item__wrapper, .s-item'))}")
                return []
            
            return items
            
        except Exception as e:
            logger.error(f"Scraping error: {str(e)}")
            raise Exception(f"Failed to scrape data: {str(e)}")

    async def _parse_items_enhanced(self, soup: BeautifulSoup, limit: int) -> List[Dict]:
        """Enhanced parsing with AI-powered feature extraction."""
        items = []
        # Update selector for items container
        results = soup.select('.s-item__wrapper, .s-item')
        logger.debug(f"Found {len(results)} items in the search results")
        
        for item in results[:limit]:
            try:
                # Update selectors for item elements
                title_elem = item.select_one('.s-item__title, .s-item__title--has-tags')
                price_elem = item.select_one('.s-item__price, .s-item__detail--primary')
                link_elem = item.select_one('.s-item__link, a[href*="itm"]')
                condition_elem = item.select_one('.s-item__condition, .s-item__subtitle, .SECONDARY_INFO')
                description_elem = item.select_one('.s-item__subtitle, .s-item__details, .s-item__detail--secondary')
                
                if not all([title_elem, price_elem, link_elem]):
                    logger.debug(f"Missing required elements: title={bool(title_elem)}, price={bool(price_elem)}, link={bool(link_elem)}")
                    continue
                
                title = title_elem.text.strip()
                if title.lower() == 'shop on ebay':
                    continue
                
                price_text = price_elem.text.strip()
                link = link_elem.get('href', '')
                condition_text = condition_elem.text.strip() if condition_elem else "Not specified"
                description = description_elem.text.strip() if description_elem else ""

                logger.debug(f"Processing item: {title} - {price_text}")

                # AI-enhanced data extraction
                features = await self.extract_product_features(title, description)
                normalized_price = await self.normalize_price(price_text, title)
                condition_analysis = await self.categorize_condition(condition_text, title, description)

                items.append({
                    'title': title,
                    'price': normalized_price,
                    'condition': condition_analysis,
                    'features': features.__dict__,
                    'link': link,
                    'raw_price': price_text,
                    'description': description
                })
                
            except Exception as e:
                logger.warning(f"Failed to parse item: {str(e)}")
                continue
        
        return items

    def _get_random_headers(self) -> Dict[str, str]:
        """Generate random headers to avoid detection."""
        return {
            "User-Agent": self.user_agent.random,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Cache-Control": "max-age=0"
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
            "_nkw": quote_plus(search_query),
            "_sop": sort_map.get(sort_by, "12")
        }
        
        return f"{self.base_url}?{'&'.join([f'{k}={v}' for k, v in params.items()])}"

# Initialize enhanced scraper
scraper = AIEnhancedScraper()

def get_random_user_agent():
    """Return a random user agent string to avoid detection."""
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15'
    ]
    return random.choice(user_agents)

def create_session():
    """Create and configure a requests session with appropriate headers."""
    session = requests.Session()
    session.headers.update({
        'User-Agent': get_random_user_agent(),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    })
    return session

def construct_ebay_search_url(base_url, query, sort_option, category=0, location="", condition=""):
    """Construct eBay search URL with various parameters.
    
    Args:
        base_url: The base eBay search URL
        query: Search term
        sort_option: Sorting method (Best Match, Lowest Price, Highest Price, Newest)
        category: eBay category ID (0 = all categories)
        location: Filter by item location
        condition: Filter by item condition (New, Used, etc.)
    """
    sort_params = {
        "Best Match": "",
        "Lowest Price": "&_sop=15",
        "Highest Price": "&_sop=16",
        "Newest": "&_sop=10",
        "Ending Soon": "&_sop=1",
        "Recently Listed": "&_sop=10"
    }
    
    # Build URL with parameters
    url = f"{base_url}?_nkw={quote_plus(query)}&_sacat={category}{sort_params.get(sort_option, '')}"
    
    # Add location filter if specified
    if location:
        url += f"&_locationPrefix={location}"
    
    # Add condition filter if specified
    if condition:
        condition_map = {
            "New": "1000",
            "Used": "3000",
            "Not Specified": "10",
            "For Parts or Not Working": "7000"
        }
        if condition in condition_map:
            url += f"&LH_ItemCondition={condition_map[condition]}"
    
    return url

def scrape_website(website):
    """Scrape website content using requests."""
    print(f"Scraping website: {website}")
    session = None
    
    try:
        # Ensure URL has scheme
        if not urlparse(website).scheme:
            website = 'https://' + website
        
        # Create session
        session = create_session()
        
        # Add random delay to mimic human behavior and avoid rate limiting
        time.sleep(random.uniform(2, 4))
        
        # Get the page
        response = session.get(website, timeout=30)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        # Get the HTML content
        html_content = response.text
        
        return html_content
        
    except requests.exceptions.RequestException as e:
        print(f"Error scraping website: {str(e)}")
        raise Exception(f"Failed to scrape the website: {str(e)}")
        
    finally:
        if session:
            try:
                session.close()
            except:
                pass

def extract_body_content(html_content):
    """Extract and clean body content from HTML."""
    try:
        soup = BeautifulSoup(html_content, "html.parser")
        
        # Remove unwanted elements
        for element in soup.find_all(['script', 'style', 'iframe', 'nav', 'footer']):
            element.decompose()
        
        body_content = soup.body
        if body_content:
            return str(body_content)
        return ""
    except Exception as e:
        print(f"Error extracting body content: {str(e)}")
        return ""

def clean_body_content(body_content):
    """Clean and format the extracted content."""
    try:
        soup = BeautifulSoup(body_content, "html.parser")

        # Remove unwanted elements
        for element in soup(['script', 'style', 'meta', 'link', 'header', 'footer', 'aside']):
            element.decompose()

        # Clean and format text
        cleaned_content = soup.get_text(separator="\n")
        
        # Remove empty lines and normalize whitespace
        lines = [line.strip() for line in cleaned_content.splitlines()]
        cleaned_content = "\n".join(line for line in lines if line)

        return cleaned_content
    except Exception as e:
        print(f"Error cleaning body content: {str(e)}")
        return body_content

def split_dom_content(dom_content, max_length=6000):
    """Split content into manageable chunks for processing."""
    try:
        # Split content at logical boundaries (e.g., paragraphs)
        chunks = []
        current_chunk = []
        current_length = 0
        
        for line in dom_content.split('\n'):
            line_length = len(line)
            
            if current_length + line_length > max_length and current_chunk:
                chunks.append('\n'.join(current_chunk))
                current_chunk = []
                current_length = 0
            
            current_chunk.append(line)
            current_length += line_length
        
        if current_chunk:
            chunks.append('\n'.join(current_chunk))
        
        return chunks
    except Exception as e:
        print(f"Error splitting content: {str(e)}")
        return [dom_content[i:i + max_length] for i in range(0, len(dom_content), max_length)] 