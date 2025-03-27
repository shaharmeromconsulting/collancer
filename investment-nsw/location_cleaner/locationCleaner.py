from openai import OpenAI
from requests import get
from pathlib import Path
import json 
import sys
import os
from config import api_key,organization,assistant_id #Gets assistant, org and api key
import pandas as pd

client = OpenAI(organization = organization,api_key=api_key)
assistant = client.beta.assistants.retrieve(assistant_id = assistant_id)

def clean_data(_entry):
    thread = client.beta.threads.create(
        messages=[
            {
                "role": "user",
                "content": _entry,
            }
        ]
        )
    _messages = []

    with client.beta.threads.runs.stream(
            thread_id=thread.id,
            assistant_id=assistant.id
            #event_handler=EventHandler(),
        ) as stream:
            #stream.until_done()
            for message in stream:
                if message.event == 'thread.message.completed':
                     _messages = _messages + [message.data.content[0].text.value]
                if message.event == 'thread.message.delta':
                    print(message.data.delta.content[0].text.value, end="")
    return _messages[-1]

#clean_data('Europe;Asia;North America;Switzerland;Israel;Spain;United States;Jerusalem;Bilbao;Austin;Boston')

file_location = r'C:\Users\merom\OneDrive - Shahar Merom consulting\16 NSW Government\01 NSW Funding Review\02 Data\Deep-Tech incubators-accelerators.csv'
file_destination = r'C:\Users\merom\OneDrive - Shahar Merom consulting\16 NSW Government\01 NSW Funding Review\02 Data\Deep-Tech incubators-accelerators-clean_loc_v2.csv'
data = pd.read_csv(file_destination,index_col='id')

#data['LOCATIONS_CLEAN'] = ''

for ix in data.index:
    if (str(data.loc[ix,'LOCATIONS_CLEAN']) == 'nan')|(data.loc[ix,'LOCATIONS_CLEAN']==''):
        try:
            input_text = str(data.loc[ix,'LOCATIONS'])
            data.loc[ix,'LOCATIONS_CLEAN'] = clean_data(input_text)
            data.to_csv(file_destination)
            print(ix)
        except Exception as e:
            print(e)
    else: 
        print(str(ix)+' COMPLETE')