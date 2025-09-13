import os
import re
from mistralai import Mistral, UserMessage, SystemMessage
from dotenv import load_dotenv
import json

load_dotenv()

token = os.environ.get("MODEL_TOKEN")
endpoint = "https://models.github.ai/inference"
model = "mistral-ai/mistral-medium-2505"

system_msg = "You are looking for hackathons, competitions and challenges happening in Italy."

user_msg_check = '''
I will give you the description of an event. Tell me if it is an hackathon\\competition\\challenge happening in Italy.
If the description does not refer to a specific event, return false. If the event is not happening in Italy, return false. 
Always end your response with a JSON object with an "answer" boolean key.

This is the event's description scraped from the web:

{event}
'''

client = Mistral(api_key=token, server_url=endpoint)

def is_hackathon_event(event_description):
    response = client.chat.complete(
        model=model,
        messages=[
            SystemMessage(content=system_msg),
            UserMessage(content=user_msg_check.format(event=event_description)),
        ],
        temperature=0,
        max_tokens=3000,
        top_p=1,
        # response_format = { "type": "json_object", }
    )
    content = response.choices[0].message.content
    print("LLM response content:", content)
   
    try:
        json_match = re.search(r'\{[^{}]*"answer"[^{}]*\}', content)
        if json_match:
            content = json_match.group(0)
        print(content)
        result = json.loads(content)
        return result.get("answer", False)
    except Exception as e:
        print(f"Error parsing JSON response in hackathon check: {e}")
        return False