# Hackathons Italy

This is a simple aggregator of hackathons in Italy, featuring a website and an RSS feed. The data is automatically updated every Sunday.

This project aims to make it easier to discover hackathon opportunities and is not affiliated with any organization.

## How it works

The `weekly-update` workflow runs weekly to update the data. First, `scraper.py` queries the Custom Search JSON API for "Hackathons Italia {current_year}", scrapes the first 100 results, and organizes them based on explicit references of months of the year. The resulting data is then used by `rss_generator.py` to create a `rss.xml` file for the RSS feed. Finally, the Vue website in the `web` directory is built and deployed on GitHub Pages.

## Disclaimers

1. Some of the items listed may not be hackathons, as it's unlikely that all the first 50 results are relevant. Similarly, some events might not be from the current year.
2. Some hackathons might be listed in several months, since the month categorization depends on the mention of months on the websites (mentions only include forms like 'Gennaio'/'Gen'/'January'/'Jan' and not '01').
3. Some events might not be listed if they only mention dates in numeric format.

## Usage

If you'd like to run the code locally, follow these steps.

Clone the repository:
```bash
git clone https://github.com/mattiaferrarini/hackathons-italy.git
```

Install the requirements:
```bash
pip install -r requirements.txt
```

Create a `.env` file with a [Google Custom Search API](https://developers.google.com/custom-search/v1/overview) key and a [Google Programmable Search Engine](https://programmablesearchengine.google.com/controlpanel/all) id:
```bash
GOOGLE_API_KEY=<your-key-here>
GOOGLE_CSE_ID=<your-cse-id-here>
```

Run the scraper and the RSS feed generator (in this order):
```bash
python scraper.py
python rss_generator.py
```

This will create two files in `web/public`: `hackathons.json` and `rss.xml`.

To run a local server and test the website:
```bash
cd web
npm install
npm run dev
```

To build the website for production:
```bash
npm run build
```
