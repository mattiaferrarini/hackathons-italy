import os
import json
import re
from googleapiclient.discovery import build
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone
import sys

json_file_path = 'web/public/hackathons.json'   # Path to the JSON file where the results are stored
max_results = 100    # Maximum number of search results to fetch

months = ['gennaio', 'febbraio', 'marzo', 'aprile', 'maggio', 'giugno', 'luglio', 'agosto', 'settembre', 'ottobre', 'novembre', 'dicembre']
it_months_short = ['gen', 'feb', 'mar', 'apr', 'mag', 'giu', 'lug', 'ago', 'set', 'ott', 'nov', 'dic']
eng_months = ['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december']
eng_months_short = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']
current_year = str(datetime.now().year)


def load_existing_data():
    """
    Load existing data from the JSON file, or initialize empty data if the script is run in the first seven days of the year.

    Returns:
        dict: A dictionary containing the existing data.
    """

    today = datetime.now()
    if today.month == 1 and today.day <= 7:
        return {month: [] for month in months}
    elif os.path.exists(json_file_path):
        with open(json_file_path, 'r') as json_file:
            return json.load(json_file)
    else:
        return {month: [] for month in months}


def fetch_search_results(max_results=max_results):
    """
    Fetch search results from Google Custom Search API.
    
    Args:
        max_results (int): Maximum number of search results to fetch.
        
    Returns:
        list: A list of search results.
    """
    
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
            q=f"Hackathons Italia {current_year}",
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


def get_months_and_year(text):
    """
    Extracts mentioned months and checks if the current year is mentioned in the given text.
    Args:
        text (str): The input text to be analyzed.
    Returns:
        tuple: A tuple containing:
            - mentioned_months (list): A list of unique months mentioned in the text.
            - in_current_year (bool): A boolean indicating whether the current year is mentioned in the text.
    """
    words = text.split()

    mentioned_months = []
    in_current_year = False

    for word in words:
        # Check Italian full month names
        if word in months and word not in mentioned_months:
            mentioned_months.append(word)
        
        # Check English full month names
        if word in eng_months and months[eng_months.index(word)] not in mentioned_months:
            mentioned_months.append(months[eng_months.index(word)])
        
        # Check Italian month abbreviations
        if word in it_months_short and months[it_months_short.index(word)] not in mentioned_months:
            mentioned_months.append(months[it_months_short.index(word)])
        
        # Check English month abbreviations
        if word in eng_months_short and months[eng_months_short.index(word)] not in mentioned_months:
            mentioned_months.append(months[eng_months_short.index(word)])
            
        if word == current_year:
            in_current_year = True
            
    return mentioned_months, in_current_year


def load_locations():
    """
    Loads and combines location data from multiple JSON files.

    Returns:
        list: A combined list of cities and regions from the specified JSON files.
    """

    with open('cities_it.json', 'r') as json_file:
        italian_list = json.load(json_file)['cities']
    with open('cities_en.json', 'r') as json_file:
        english_list = json.load(json_file)['cities']
    with open('regions.json', 'r') as json_file:
        regions_list = json.load(json_file)['regions']
    return italian_list + english_list + regions_list


def get_mentioned_locations(text, locations):
    """
    Extracts and returns a list of locations mentioned in the given text.
    Args:
        text (str): The text to search for location mentions.
        locations (list of str): A list of location names to search for in the text.
    Returns:
        list of str: A list of location names that are mentioned in the text.
    """

    mentioned_locations = [city for city in locations if re.search(r'\b' + re.escape(city.lower()) + r'\b', text)]

    return mentioned_locations


def add_entry(month_data, result, mentioned_months):
    """
    Adds an entry to the month_data dictionary for each month in mentioned_months.
    Args:
        month_data (dict): A dictionary where keys are month names and values are lists of entries.
        result (dict): A dictionary containing 'title' and 'href' keys for the entry to be added.
        mentioned_months (list): A list of month names to which the entry should be added.
    Returns:
        bool: True if the entry is new and was added to any month's list, False otherwise.
    """
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
    
    return is_new


def check_hackathon_mention(text):
    """
    Check if the given text mentions the word 'hackathon'.
    Args:
        text (str): The input text to be analyzed.
    Returns:
        bool: True if the text mentions the word 'hackathon', False otherwise.
    """
    return 'hackathon' in text


def parse_html(content):
    """
    Parses the given HTML content, removes footer elements, and extracts the text.
    Args:
        content (str): The HTML content to be parsed.
    Returns:
        str: The extracted text from the HTML content, converted to lowercase.
    """

    # Parse the HTML content
    soup = BeautifulSoup(content, 'html.parser')
            
    # Remove footer elements
    for footer in soup.find_all('footer'):
        footer.decompose()
                
    # Remove elements with footer in class or id
    for element in soup.find_all(class_=lambda x: x and 'footer' in x.lower()):
        element.decompose()
    for element in soup.find_all(id=lambda x: x and 'footer' in x.lower()):
        element.decompose()

    # Extract the text from the parsed HTML and convert it to lowercase
    text = soup.get_text().lower()

    return text


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
    locations = load_locations()

    for index, result in enumerate(results):
        try:
            # Print progress
            print(f"Processing {index + 1}/{len(results)} search result: {result['href']}")

            # Get and parse the HTML content
            content = requests.get(result['href'], timeout=20).text
            text = parse_html(content)
            
            # Check if the text mentions the word 'hackathon'
            mentions_hackathon = check_hackathon_mention(text)

            # Check if the text mentions any month and if it mentions the current year
            mentioned_months, in_current_year = get_months_and_year(text)

            # If the current year is mentioned, proceed with further processing
            is_new = False
            if in_current_year and mentions_hackathon:

                # Check if the text mentions any city
                mentioned_locations = get_mentioned_locations(text, locations)

                # If the text mentions any city, add the entry to the month data
                if len(mentioned_locations) > 0:
                    is_new = add_entry(month_data, result, mentioned_months)
            
                    # Keep track of the number of new entries
                    if is_new:
                        new_count += 1

        except Exception:
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
    
    # Load environment variables from .env file
    load_dotenv()

    # Load existing data from the JSON file
    month_data = load_existing_data()

    if len(sys.argv) > 1:
        results = fetch_search_results(int(sys.argv[1]))
    else:
        results = fetch_search_results()

    # Process the search results and save them
    month_data, not_processed, new_count = process_results(results, month_data)
    save_data(month_data)

    # Print the results
    print(f"Fetched {len(results)} results, processed {len(results) - len(not_processed)} web pages, added {new_count} new entries to the JSON file.")