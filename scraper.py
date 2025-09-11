import os
import json
import re
from googleapiclient.discovery import build
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone, timedelta
import sys
from llm import extract_hackathon_starting_date

json_file_path = 'web/public/hackathons.json'   # Path to the JSON file where the results are stored
max_results = 50    # Maximum number of search results to fetch
time_cutoff_days = 35  # Number of days to keep hackathons in the JSON file
current_year = str(datetime.now().year)


def load_existing_data():
    if os.path.exists(json_file_path):
        with open(json_file_path, 'r') as json_file:
            data = json.load(json_file)
    else:
        data = {}
    return filter_old_hackathons(data)


def filter_old_hackathons(hackathons, days=time_cutoff_days):
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
    return [hackathon for hackathon in hackathons if datetime.fromisoformat(hackathon['starting_date']).replace(tzinfo=timezone.utc) >= cutoff_date]


def fetch_search_results(max_results=max_results):
    # Get API credentials from environment variables
    api_key = os.environ.get('GOOGLE_API_KEY')
    cse_id = os.environ.get('GOOGLE_CSE_ID')
    
    if not api_key or not cse_id:
        raise ValueError("Missing required environment variables: GOOGLE_API_KEY and GOOGLE_CSE_ID")
    
    # Build the service
    service = build("customsearch", "v1", developerKey=api_key, cache_discovery=False)
    
    results = []
    # Google API returns max 10 results per request, we may need multiple requests
    for i in range(0, min(max_results, 100), 10):
        search_results = service.cse().list(
            q=f"Hackathon in Italia",
            cx=cse_id,
            num=min(10, max_results - i),
            start=i + 1
        ).execute()
        
        if 'items' in search_results:
            for item in search_results['items']:
                results.append({
                    'title': item['title'],
                    'href': item['link']
                })
                
        if len(results) >= max_results or 'items' not in search_results:
            break
    
    return results


def parse_hackathon_website(content):
    soup = BeautifulSoup(content, 'html.parser')

    # Remove footer elements
    for footer in soup.find_all('footer'):
        footer.decompose()
    for element in soup.find_all(class_=lambda x: x and 'footer' in x.lower()):
        element.decompose()
    for element in soup.find_all(id=lambda x: x and 'footer' in x.lower()):
        element.decompose()

    # Remove header elements
    for header in soup.find_all('header'):
        header.decompose()
    for element in soup.find_all(class_=lambda x: x and 'header' in x.lower()):
        element.decompose()
    for element in soup.find_all(id=lambda x: x and 'header' in x.lower()):
        element.decompose()

    text = soup.get_text(separator='\n').lower()
    text = re.sub(r'\n{2,}', '\n', text)

    return text


def process_results(results):
    not_processed = []  # List of URLs that could not be processed
    hackathons = []

    for index, result in enumerate(results):
        try:
            # Print progress
            print(f"Processing {index + 1}/{len(results)} search result: {result['href']}")

            # Get and parse the hackathon's website
            content = requests.get(result['href'], timeout=20).text
            event_description = parse_hackathon_website(content)
            starting_date = extract_hackathon_starting_date(event_description)

            if starting_date:
                hackathons.append({
                    "title": result['title'],
                    "href": result['href'],
                    "starting_date": starting_date,
                    "scraped_date": datetime.now(timezone.utc).date().isoformat()
                })
        except Exception as e:
            print(f"Could not process {result['href']} because of {e}.")
            not_processed.append(result['title'])

    # Return results of processing
    return hackathons, not_processed


if __name__ == '__main__':
    # Load environment variables from .env file
    load_dotenv()

    # Fetch web search results
    if len(sys.argv) > 1:
        results = fetch_search_results(int(sys.argv[1]))
    else:
        results = fetch_search_results()

    # Process the search results to extract hackathon details
    new_hackathons, not_processed = process_results(results)
    new_hackathons = filter_old_hackathons(new_hackathons)

    # Load existing data and merge with new data, avoiding duplicates
    existing_hackathons = load_existing_data()
    existing_hackathon_hrefs = {hackathon['href'] for hackathon in existing_hackathons}
    new_hackathons = [hackathon for hackathon in new_hackathons if hackathon['href'] not in existing_hackathon_hrefs]
    all_hackathons = existing_hackathons + new_hackathons

    # Save the updated data back to the JSON file
    with open(json_file_path, 'w') as json_file:
        json.dump(all_hackathons, json_file, indent=2)

    # Print the results
    print(f"Fetched {len(results)} results, processed {len(results) - len(not_processed)} web pages, added {len(new_hackathons)} new entries to the JSON file.")