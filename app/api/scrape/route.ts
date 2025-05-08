import { NextResponse } from 'next/server';

export async function POST(request: Request) {
  try {
    const body = await request.json();

    // Make a request to your Python backend
    const response = await fetch('http://127.0.0.1:5000/api/scrape', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        search_query: body.search_query,
        sort_by: body.sort_by || "Best Match",
        results_limit: parseInt(body.results_limit?.toString() || "10"),
        country: body.country || "UK"
      }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      return NextResponse.json(
        { detail: errorData.detail || 'Failed to scrape data' },
        { status: response.status }
      );
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Scraping error:', error);
    return NextResponse.json(
      { detail: error instanceof Error ? error.message : 'Failed to scrape data' },
      { status: 500 }
    );
  }
} 