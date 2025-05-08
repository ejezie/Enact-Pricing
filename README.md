# Enact Pricing Scraper

A web scraping tool for eBay price intelligence using Next.js and FastAPI.

## Features

- Real-time eBay product scraping
- Price analysis and market intelligence
- AI-powered data extraction
- Beautiful Material UI interface
- Responsive design

## Tech Stack

- Frontend: Next.js 14, Material UI, React Query
- Backend: FastAPI, BeautifulSoup4, OpenAI
- AI: GPT-3.5 for data analysis

## Setup

1. Clone the repository
2. Install dependencies:
   ```bash
   # Frontend
   npm install

   # Backend
   pip install -r requirements.txt
   ```
3. Set up environment variables:
   ```
   # Backend Configuration
   PORT=5000
   HOST=localhost

   # OpenAI Configuration
   OPENAI_API_KEY=your_key_here

   # Scraping Configuration
   MAX_RETRIES=3
   REQUEST_TIMEOUT=30
   RATE_LIMIT_DELAY=2
   ```

4. Start the servers:
   ```bash
   # Start backend (port 5000)
   python app.py

   # Start frontend (port 3000)
   npm run dev
   ```

## Usage

1. Enter your search query
2. Configure filters (category, location, condition)
3. Set results limit
4. Click search
5. View analyzed results and market insights

## License

MIT License 