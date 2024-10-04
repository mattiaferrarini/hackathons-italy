import json
from feedgen.feed import FeedGenerator

json_file_path = 'web/public/hackathons.json'   # Path to the JSON file where the results are stored
rss_file_path = 'web/public/rss.xml'    # Path to the RSS feed file

def generate_rss():
    # Load the JSON data
    with open(json_file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    # Create a new RSS feed
    fg = FeedGenerator()
    fg.title('Feed degli hackathon in Italia')
    fg.description('Ultimi hackathon trovati')
    fg.link(href='http://mattiaferrarini.com/hackathons-italy/rss.xml', rel='self')
    fg.language('it')

    # Add items to the RSS feed
    for month, hackathons in data.items():
        for hackathon in hackathons:
            fe = fg.add_entry()
            fe.title(f'{hackathon["title"]} ({month})')
            fe.link(href=hackathon['href'])
            fe.description(hackathon['title'])
            fe.pubDate(hackathon['scraped_date'])

    # Generate the RSS feed and save it to a file
    fg.rss_file(rss_file_path, pretty=True)
    print('RSS feed generated successfully!')

if __name__ == '__main__':
    generate_rss()