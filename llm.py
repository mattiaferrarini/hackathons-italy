import os
from mistralai import Mistral, UserMessage, SystemMessage
from dotenv import load_dotenv
import json

load_dotenv()

token = os.environ.get("MODEL_TOKEN")
endpoint = "https://models.github.ai/inference"
model = "mistral-ai/mistral-medium-2505"

client = Mistral(api_key=token, server_url=endpoint)

system_msg = "You are looking for hackathons, competitions and challenges happening in Italy."

user_msg_check = '''
I will give you the description of an event. Tell me if it is an hackathon\\competition\\challenge happening in Italy. Always answer with a JSON object with an "answer" boolean key.

This is the event's description scraped from the web:

{event}
'''

user_msg = '''
I will give you the description of an event. Tell me its starting date. If you can only infer the starting month, return the first day of that month. 
If you cannot find the starting date, return null. Always answer with a JSON object with a "starting_date" key.

This is the event's description scraped from the web:

{event}
'''

def is_hackathon_event(event_description):
    response = client.chat.complete(
        model=model,
        messages=[
            SystemMessage(content=system_msg),
            UserMessage(content=user_msg_check.format(event=event_description)),
        ],
        temperature=0,
        max_tokens=200,
        top_p=1,
        response_format = {
            "type": "json_object",
        }
    )
    content = response.choices[0].message.content
    try:
        result = json.loads(content)
        return result.get("answer", False)
    except Exception as e:
        print(f"Error parsing JSON response in hackathon check: {e}")
        return False

def extract_hackathon_starting_date(event_description):

    if not is_hackathon_event(event_description):
        print("The event is not a hackathon in Italy.")
        return None

    response = client.chat.complete(
        model=model,
        messages=[
            SystemMessage(content=system_msg),
            UserMessage(content=user_msg.format(event=event_description)),
        ],
        temperature=0,
        max_tokens=200,
        top_p=1,
        response_format = {
            "type": "json_object",
        }
    )
    content = response.choices[0].message.content
    try:
        result = json.loads(content)
        return result.get("starting_date", None)
    except Exception as e:
        print(f"Error parsing JSON response in date extraction: {e}")
        return None