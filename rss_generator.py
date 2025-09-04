import json
from feedgen.feed import FeedGenerator
from datetime import datetime, timedelta
from datetime import timezone

json_file_path = 'web/public/hackathons.json'   # Path to the JSON file where the results are stored
rss_file_path = 'web/public/rss.xml'    # Path to the RSS feed file

def generate_rss():
    # Load the JSON data
    with open(json_file_path, 'r', encoding='utf-8') as file:
        hackathons = json.load(file)

    # Create a new RSS feed
    fg = FeedGenerator()
    fg.title('Feed degli hackathon in Italia')
    fg.description('Ultimi hackathon trovati')
    fg.link(href='http://mattiaferrarini.com/hackathons-italy/rss.xml', rel='self')
    fg.language('it')

    # Get today's date
    today = datetime.now().date()

    # Add items to the RSS feed
    for hackathon in hackathons:
        try:
            scraped_date = datetime.strptime(hackathon['scraped_date'], "%Y-%m-%d")
            scraped_date = scraped_date.replace(tzinfo=timezone.utc)
            if abs((today - scraped_date.date()).days) <= 1:
                fe = fg.add_entry()
                fe.title(f'{hackathon["title"]} ({hackathon["starting_date"]})')
                fe.link(href=hackathon['href'])
                fe.description(f"Inizia il {hackathon['starting_date']}")
                fe.pubDate(scraped_date)
        except Exception as e:
            print(f"Error: {e}. Processing hackathon: {hackathon}")
            continue

    # Generate the RSS feed and save it to a file
    fg.rss_file(rss_file_path, pretty=True)
    print('RSS feed generated successfully!')

if __name__ == "__main__":
    generate_rss()