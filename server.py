from wit import Wit
import pywapi
from flask import Flask, request
from pymessenger.bot import Bot
import requests
import ipdb
import os

# Insert Wit access token here. Don't forget to train the Wit bot.
access_token = os.environ.get('WIT_TOKEN')

# Facebook App access token. Don't forge to connect app to page.
TOKEN = os.environ.get('FB_PAGE_TOKEN')

bot = Bot(TOKEN)

app = Flask(__name__)


def first_entity_value(entities, entity):
    if entity not in entities:
        return None
    val = entities[entity][0]['value']
    if not val:
        return None
    return val['value'] if isinstance(val, dict) else val

def say(session_id, context, msg):
    print(msg)

def merge(session_id, context, entities, msg):
    loc = first_entity_value(entities, 'location')
    if loc:
        context['loc'] = loc
    return context

def error(session_id, context, e):
    print(str(e))

def fetch_weather(session_id, context):
    location = context['loc']
    location_id = pywapi.get_loc_id_from_weather_com(location)[0][0]
    weather_com_result = pywapi.get_weather_from_weather_com(location_id)
    context['forecast'] = weather_com_result["current_conditions"]["temperature"]
    return context

actions = {
    'say': say,
    'merge': merge,
    'error': error,
    'fetch-weather': fetch_weather,
}

client = Wit(access_token, actions)

# Insert wit username below
session_id = os.environ.get('WIT_USERNAME')

# client.run_actions(session_id, 'weather in %s'%place, {})

@app.route("/webhook", methods = ['GET', 'POST'])
def hello():
    if request.method == 'GET':
        if (request.args.get("hub.verify_token") == os.environ.get('FB_VERIFY_TOKEN')):
                return request.args.get("hub.challenge")
    if request.method == 'POST':
        output = request.json
        event = output['entry'][0]['messaging']
        for x in event:
            if (x.get('message') and x['message'].get('text')):
                message = x['message']['text']
                recipient_id = x['sender']['id']
                messageToSend = client.run_actions(session_id, message, {})
                bot.send_text_message(recipient_id, messageToSend)
            else:
                pass
        return "success"

@app.route("/")
def hello():
    return "Server is Online."


if __name__ == "__main__":
    app.run(port=5000, debug=True)