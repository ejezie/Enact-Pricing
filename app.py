from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from playwright.sync_api import sync_playwright
import openai
from dotenv import load_dotenv
import os
import json
import logging

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="eBay AI Scraper")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ScrapingRequest(BaseModel):
    search_query: str = Field(..., description="Search query for eBay", min_length=2)
    max_results: int = Field(default=5, le=20, description="Maximum number of results to return")

class ScrapingResponse(BaseModel):
    items: List[Dict]
    analysis: Optional[str] = None

def scrape_ebay(query: str, max_results: int) -> List[Dict]:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # Navigate to eBay search results
        url = f"https://www.ebay.co.uk/sch/i.html?_nkw={query.replace(' ', '+')}"
        page.goto(url)
        
        # Wait for results to load
        page.wait_for_selector("ul.srp-results li.s-item")
        
        # Extract items
        items = []
        listings = page.query_selector_all("ul.srp-results li.s-item")
        
        for i, listing in enumerate(listings[:max_results]):
            try:
                title_elem = listing.query_selector(".s-item__title")
                price_elem = listing.query_selector(".s-item__price")
                link_elem = listing.query_selector("a.s-item__link")
                condition_elem = listing.query_selector(".SECONDARY_INFO")
                
                title = title_elem.text_content() if title_elem else "No title"
                price = price_elem.text_content() if price_elem else "No price"
                link = link_elem.get_attribute("href") if link_elem else "#"
                condition = condition_elem.text_content() if condition_elem else "Not specified"
                
                items.append({
                    "title": title,
                    "price": price,
                    "condition": condition,
                    "link": link
                })
            except Exception as e:
                logger.error(f"Error extracting item {i}: {str(e)}")
                continue
        
        browser.close()
        return items

def analyze_with_ai(items: List[Dict]) -> str:
    try:
        # Prepare the data for AI analysis
        items_text = json.dumps(items, indent=2)
        
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a market analysis expert. Analyze the eBay listings and provide insights about pricing trends, conditions, and recommendations."},
                {"role": "user", "content": f"Analyze these eBay listings and provide a brief summary of pricing trends and recommendations:\n\n{items_text}"}
            ],
            max_tokens=250
        )
        
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Error in AI analysis: {str(e)}")
        return "Unable to perform AI analysis at this time."

@app.get("/")
async def root():
    return {"message": "eBay AI Scraper API is running"}

@app.post("/api/scrape", response_model=ScrapingResponse)
async def scrape(request: ScrapingRequest):
    try:
        # Scrape eBay
        items = scrape_ebay(request.search_query, request.max_results)
        
        if not items:
            raise HTTPException(status_code=404, detail="No items found")
        
        # Analyze results with AI
        analysis = analyze_with_ai(items)
        
        return ScrapingResponse(items=items, analysis=analysis)
        
    except Exception as e:
        logger.error(f"Error during scraping: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000) 