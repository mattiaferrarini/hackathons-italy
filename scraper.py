import os
import json
from duckduckgo_search import DDGS
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone
import sys

json_file_path = 'web/public/hackathons.json'   # Path to the JSON file where the results are stored
max_results = 50    # Maximum number of search results to fetch

months = ['gennaio', 'febbraio', 'marzo', 'aprile', 'maggio', 'giugno', 'luglio', 'agosto', 'settembre', 'ottobre', 'novembre', 'dicembre']
eng_months = ['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december']
current_year = str(datetime.now().year)


def load_existing_data():
    """
    Load existing data from the JSON file.

    Returns:
        dict: A dictionary containing the existing data.
    """

    if os.path.exists(json_file_path):
        with open(json_file_path, 'r') as json_file:
            return json.load(json_file)
    else:
        return {month: [] for month in months}


def fetch_search_results(max_results=max_results):
    """
    Fetch search results from DuckDuckGo.

    Returns:
        list: A list of search results.
    """

    return DDGS().text(f"hackathon italia {current_year}", region='it-it', safesearch='off', max_results=max_results)


def process_results(results, month_data):
    """
    Process the search results and update the month data.

    Args:
        results (list): A list of search results.
        month_data (dict): A dictionary containing the existing month data.

    Returns:
        tuple: A tuple containing the updated month data, a list of not processed URLs, and the count of new entries.
    """

    not_processed = []  # List of URLs that could not be processed
    new_count = 0   # Number of new URLs that were added to the JSON file

    for index, result in enumerate(results):
        try:
            # Print progress
            print(f"Processing {index + 1}/{len(results)} search result: {result['href']}")

            content = requests.get(result['href']).text

            # Parse the HTML content
            soup = BeautifulSoup(content, 'html.parser')

            # Extract the text from the parsed HTML and convert it to lowercase
            text = soup.get_text().lower()
            
            words = text.split()

            mentioned_months = []
            in_current_year = False

            # Check if the text mentions any month and if it mentions the current year
            for word in words:
                if word in months and word not in mentioned_months:
                    print(f"Added {result['title']} to {word}")
                    mentioned_months.append(word)
                if word in eng_months and months[eng_months.index(word)] not in mentioned_months:
                    print(f"Added {result['title']} to {word}")
                    mentioned_months.append(months[eng_months.index(word)])
                if word == current_year:
                    in_current_year = True

            # If the current year is mentioned, add the result to the corresponding months
            is_new = False
            if in_current_year:
                entry = {
                    'title': result['title'],
                    'href': result['href'],
                    'scraped_date': datetime.now(timezone.utc).isoformat()
                }
                for month in mentioned_months:
                    # Check if an entry with the same 'title' and 'href' already exists
                    if not any(existing_entry['title'] == entry['title'] and existing_entry['href'] == entry['href'] for existing_entry in month_data[month]):
                        month_data[month].append(entry)
                        is_new = True
            
            # Keep track of the number of new entries
            if is_new:
                new_count += 1

        except Exception as e:
            not_processed.append(result['title'])

    # Return results of processing
    return month_data, not_processed, new_count


def save_data(month_data):
    """
    Save the month data to the JSON file.

    Args:
        month_data (dict): A dictionary containing the month data.
    """

    with open(json_file_path, 'w') as json_file:
        json.dump(month_data, json_file, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    
    month_data = load_existing_data()

    if len(sys.argv) > 1:
        results = fetch_search_results(int(sys.argv[1]))
    else:
        results = fetch_search_results()
    
    month_data, not_processed, new_count = process_results(results, month_data)
    save_data(month_data)

    # Print the results
    print(f"Fetched {len(results)} results, processed {len(results) - len(not_processed)} web pages, added {new_count} new entries to the JSON file.")