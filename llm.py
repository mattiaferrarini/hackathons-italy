import os
from mistralai import Mistral, UserMessage, SystemMessage
from dotenv import load_dotenv
import json

load_dotenv()

token = os.environ.get("MODEL_TOKEN")
endpoint = "https://models.github.ai/inference"
model = "mistral-ai/mistral-medium-2505"

client = Mistral(api_key=token, server_url=endpoint)

system_msg = "You are looking for hackathons happening in Italy."

user_msg = '''
Is this event an hackathon happening in Italy? If so, return its starting date. If you can only infer the starting month, return the first day of that month. 
If the event is not an hackathon happening in Italy, return null. In any case, return a JSON object with a "starting_date" key.

This is the event:

{event}
'''

def extract_hackathon_starting_date(event_description):
    response = client.chat.complete(
        model=model,
        messages=[
            SystemMessage(content=system_msg),
            UserMessage(content=user_msg.format(event=event_description)),
        ],
        temperature=0.8,
        max_tokens=200,
        top_p=0.1,
        response_format = {
            "type": "json_object",
        }
    )
    content = response.choices[0].message.content
    try:
        result = json.loads(content)
        return result.get("starting_date", None)
    except (json.JSONDecodeError, TypeError, KeyError) as e:
        return None