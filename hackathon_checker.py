import os
import re
from openai import OpenAI
from dotenv import load_dotenv
import json

load_dotenv()

token = os.environ["MODEL_TOKEN"]
endpoint = "https://models.github.ai/inference"
model = "openai/gpt-4.1-mini"

system_msg = "You are a helpful assistant looking for hackathons, competitions and challenges happening in Italy."

user_msg_check = '''\
I will give you the description of an event scraped from a website. Tell me if it is an hackathon\\competition\\challenge happening in Italy.
If the description does not refer to a specific event, return false. If the event is not happening in Italy, return false. 
Always enclose your answer in <ans></ans> tags like this: <ans>true</ans> or <ans>false</ans>.

This is the event's description scraped from the web:

[START OF EVENT DESCRIPTION]
{event}
[END OF EVENT DESCRIPTION]
'''

client = OpenAI(
    base_url=endpoint,
    api_key=token,
)

def is_hackathon_event(event_description):
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg_check.format(event=event_description)},
        ],
        temperature=0,
        max_tokens=5000,
        top_p=1
    )
    content = response.choices[0].message.content
    print("LLM response content:", content)
   
    try:
        match = re.search(r'<ans>(true|false)</ans>', content, re.IGNORECASE)
        if match:
            answer = match.group(1).lower()
            return answer == 'true'
        else:
            print("Could not find <ans> tags in the response.")
            return False
    except Exception as e:
        print(f"Error parsing response in hackathon check: {e}")
        return False