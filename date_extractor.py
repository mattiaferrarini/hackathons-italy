import os
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv
import json
import re
from datetime import datetime

load_dotenv()

token = os.environ.get("MODEL_TOKEN")
endpoint = "https://models.github.ai/inference"
model = "meta/Llama-4-Scout-17B-16E-Instruct"

current_year = datetime.now().year

system_msg = "You extract dates from event descriptions."

user_msg = '''
I will give you the description of an event. Extract its starting date. If you can only infer the starting month, return the first day of that month.
If no year is mentioned, assume it is {current_year}. If multiple dates are mentioned, try to infer the correct one. If no specific date is mentioned, return null.
Always end your answer with a JSON object with a "starting_date" key.

This is the event's description scraped from the web:

{event}
'''

client = ChatCompletionsClient(
    endpoint=endpoint,
    credential=AzureKeyCredential(token),
)

def extract_hackathon_starting_date(event_description):
    response = client.complete(
        model=model,
        messages=[
            SystemMessage(content=system_msg),
            UserMessage(content=user_msg.format(event=event_description, current_year=current_year)),
        ],
        temperature=0,
        max_tokens=3000,
        top_p=1,
    )

    content = response.choices[0].message.content
    print("LLM response content:", content)
    
    try:
        json_match = re.search(r'\{[^{}]*"starting_date"[^{}]*\}', content)
        if json_match:
            content = json_match.group(0)
        result = json.loads(content)
        return result.get("starting_date", None)
    except Exception as e:
        print(f"Error parsing JSON response in date extraction: {e}")
        return None