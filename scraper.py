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
import time


JSON_FILE_PATH = 'web/public/hackathons.json'   # Path to the JSON file where the results are stored
MAX_RESULTS = 50    # Maximum number of search results to fetch
TIME_CUTOFF_DAYS = 35  # Number of days to keep hackathons in the JSON file
REQUEST_PER_MINUTE_LLM = 15 # Number of requests per minute allowed by the LLM API


def load_existing_data():
    if os.path.exists(JSON_FILE_PATH):
        with open(JSON_FILE_PATH, 'r') as json_file:
            data = json.load(json_file)
    else:
        data = {}
    return filter_old_hackathons(data)


def filter_old_hackathons(hackathons, days=TIME_CUTOFF_DAYS):
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
    filtered = []
    for hackathon in hackathons:
        starting_date = hackathon.get('starting_date')
        if starting_date is None or starting_date == '' or starting_date == 'null':
            filtered.append(hackathon)
        else:
            try:
                date_obj = datetime.fromisoformat(starting_date).replace(tzinfo=timezone.utc)
                if date_obj >= cutoff_date:
                    filtered.append(hackathon)
            except Exception:
                # If starting_date is invalid, keep the hackathon
                filtered.append(hackathon)
    return filtered


def fetch_search_results(max_results=MAX_RESULTS):
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

    text = soup.get_text(separator='\n').strip()
    text = re.sub(r'(\n\s*){3,}', '\n\n', text)
    return text


def process_results(results):
    not_processed = []  # List of URLs that could not be processed
    hackathons = []

    for index, result in enumerate(results):
        # Respect rate limits of the LLM API
        if index > 0 and index % (REQUEST_PER_MINUTE_LLM // 2 - 1) == 0:
            print("Waiting to respect rate limits...")
            time.sleep(75)

        try:
            print(f"Processing {index + 1}/{len(results)} search result: {result['href']}")

            # Get and parse the hackathon's website
            content = requests.get(result['href'], timeout=20).text
            event_description = parse_hackathon_website(content)
            starting_date = extract_hackathon_starting_date(event_description)
            print("The event's starting date is:", starting_date)

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


def merge_existing_and_new_hackathons(existing_hackathons, new_hackathons):
    # Update starting_date for existing hackathons if new data is available
    existing_hackathons_by_href = {hackathon['href']: hackathon for hackathon in existing_hackathons}
    for new_hackathon in new_hackathons:
        if new_hackathon['href'] in existing_hackathons_by_href:
            existing_hackathons_by_href[new_hackathon['href']]['starting_date'] = new_hackathon['starting_date']
            existing_hackathons_by_href[new_hackathon['href']]['scraped_date'] = new_hackathon['scraped_date']
            print(f"Updated starting_date for existing hackathon: {new_hackathon['title']}")
    existing_hackathons = list(existing_hackathons_by_href.values())

    # Remove duplicates from new_hackathons and merge with existing data
    new_hackathons = [hackathon for hackathon in new_hackathons if hackathon['href'] not in existing_hackathons_by_href]
    all_hackathons = existing_hackathons + new_hackathons

    return all_hackathons


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

    # Load existing data and merge with new data
    existing_hackathons = load_existing_data()
    all_hackathons = merge_existing_and_new_hackathons(existing_hackathons, new_hackathons)

    # Save the updated data back to the JSON file
    with open(JSON_FILE_PATH, 'w') as json_file:
        json.dump(all_hackathons, json_file, indent=2)

    # Print the results
    print(f"Fetched {len(results)} results, processed {len(results) - len(not_processed)} web pages, added {len(new_hackathons)} new entries to the JSON file.")