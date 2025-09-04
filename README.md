# Hackathons Italy

This is a simple aggregator of hackathons in Italy, featuring a website and an RSS feed. The data is automatically updated every Sunday.

This project aims to make it easier to discover hackathon opportunities and is not affiliated with any organization.

## How it works

The `weekly-update` workflow runs weekly to update the data. First, `scraper.py` queries the Custom Search JSON API for "Hackathon Italia", retrieving the first 100 results. The webpages of these results are then fetched and processed by an LLM (`mistral-medium-2505` at the moment) to verify the validity and get the event's starting date. The resulting data is used by `rss_generator.py` to create a `rss.xml` file for the RSS feed. Finally, the Vue website in the `web` directory is built and deployed on GitHub Pages.

## Disclaimers

The data displayed in the website might not be comprehensive nor correct, as these qualities depend on the results obtained via the search API and the outputs of the LLM.

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

Create a `.env` file with a [Google Custom Search API](https://developers.google.com/custom-search/v1/overview) key, a [Google Programmable Search Engine](https://programmablesearchengine.google.com/controlpanel/all) id and a [GitHub Models](https://github.com/marketplace/models/azureml-mistral/mistral-medium-2505) token:
```bash
GOOGLE_API_KEY=<your-key-here>
GOOGLE_CSE_ID=<your-cse-id-here>
MODEL_TOKEN=<your-model-token-here>
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
