import os
from openai import OpenAI
from dotenv import load_dotenv
import json
import re
from datetime import datetime

load_dotenv()

token = os.environ.get("MODEL_TOKEN")
endpoint = "https://models.github.ai/inference"
model = "openai/gpt-4.1"

current_year = datetime.now().year

system_msg = "You are a helpful assistant that extracts dates from event descriptions."

user_msg = '''
I will give you the description of an event scraped from a website. Extract its starting date. If you can only infer the starting month, return the first day of that month.
If no year is mentioned, assume it is {current_year}. If multiple dates are mentioned, try to infer the correct one. If no specific date is mentioned, return null.
Always enclose your answer in <ans></ans> tags like this: <ans>{current_year}-12-31</ans> or <ans>null</ans>.

This is the event's description scraped from the web:

[START OF EVENT DESCRIPTION]
{event}
[END OF EVENT DESCRIPTION]
'''

client = OpenAI(
    base_url=endpoint,
    api_key=token,
)

def extract_hackathon_starting_date(event_description):
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg.format(event=event_description, current_year=current_year)},
        ],
        temperature=0,
        max_tokens=3000,
        top_p=1,
    )

    content = response.choices[0].message.content
    print("LLM response content:", content)
    
    try:
        ans_match = re.search(r'<ans>([^<]+)</ans>', content)
        if ans_match:
            content = ans_match.group(1)
        return content if content != "null" else None
    except Exception as e:
        print(f"Error parsing response in date extraction: {e}")
        return None