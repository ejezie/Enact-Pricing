import requests
import json

def test_scrape_endpoint():
    url = "http://127.0.0.1:8000/api/scrape"
    headers = {"Content-Type": "application/json"}
    data = {
        "search_query": "iphone",
        "sort_by": "Best Match",
        "results_limit": 5
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Raw Response: {response.text}")
        
        if response.text:
            try:
                print(f"JSON Response: {json.dumps(response.json(), indent=2)}")
            except json.JSONDecodeError as e:
                print(f"Failed to parse JSON: {str(e)}")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_scrape_endpoint() 