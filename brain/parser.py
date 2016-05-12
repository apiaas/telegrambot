from adapt.intent import IntentBuilder
from adapt.engine import IntentDeterminationEngine
from brain.httpclient import HttpClient
from django.conf import settings
from brain.vision import Vision
from os.path import basename
import subprocess

engine = IntentDeterminationEngine()

search_keywords = [
    'find',
    'search for',
    'search',
    'locate',
]

next_keywords = [
    'next',
    'next page',
]

previous_keywords = [
    'prev',
    'previous',
    'previous page',
]

photo_keywords = [
    'photo',
    'send photo',
]

# file_keywords = [
#     'file',
#     'send file',
# ]

[engine.register_entity(k, 'Search') for k in search_keywords]
[engine.register_entity(k, 'Next') for k in next_keywords]
[engine.register_entity(k, 'Previous') for k in previous_keywords]
[engine.register_entity(k, 'Photo') for k in photo_keywords]

# structure intent
intents = [
    IntentBuilder("SearchIntent").optionally("Search").build(),
    IntentBuilder("NextIntent").optionally('Next').build(),
    IntentBuilder("PreviousIntent").optionally('Previous').build(),
    IntentBuilder("PhotoIntent").optionally('Photo').build(),
]

[engine.register_intent_parser(i) for i in intents]


def determine(text):
    return [i for i in engine.determine_intent(text) if i.get('confidence') > 0]


async def download_file(bot, file_id):
    new_file = await bot.getFile(file_id)
    file_name = 'media/' + basename(new_file['file_path'])
    await bot.download_file(file_id, file_name)
    return file_name


def delete(name):
    subprocess.call(['rm', name])


async def search_intent(text, data=None, user=None, message=None, bot=None):
    if not data:
        data = {}
    if not text and message.get('photo'):
        text = 'send photo'
    si = determine(text)
    if not si:
        data['next_page'] = 0
        data['prev_page'] = 0
        return "Sorry, I don't know how to do that yet.", data

    intent = si.pop()
    http_client = HttpClient()
    if intent['intent_type'] == 'SearchIntent':
        search_str = text.lower().replace(intent['Search'], '', 1).strip()
        data['search_query'] = search_str
        data['next_page'] = 2
        data['prev_page'] = 0
        response = http_client.search(text=search_str, user=user)
        image_location = response['results'][0]['path']
        return "Searching for: '{}' \n{}".format(search_str, settings.TELEGRAMBOT_API_HOST + '/' + image_location), data

    if not data or not data.get('search_query'):
        data['next_page'] = 0
        data['prev_page'] = 0
        msg = "Please let me know what are you looking for. For example: search for unicorns"
        return msg, data

    if intent['intent_type'] == 'NextIntent':
        response = http_client.search(text=data['search_query'], user=user, page=data['next_page'])
        data['next_page'] += 1
        data['prev_page'] += 1
        image_location = response['results'][0]['path']
        return "Searching for: '{}' \n{}".format(data['search_query'], settings.TELEGRAMBOT_API_HOST + '/' + image_location), data

    if intent['intent_type'] == 'PreviousIntent':
        response = http_client.search(text=data['search_query'], user=user, page=data['prev_page'])
        data['next_page'] -= 1
        data['prev_page'] -= 1
        image_location = response['results'][0]['path']
        return "Searching for: '{}' \n{}".format(data['search_query'], settings.TELEGRAMBOT_API_HOST + '/' + image_location), data

    if intent['intent_type'] == 'PhotoIntent':
        data['next_page'] = 0
        data['prev_page'] = 0
        file_name = await download_file(bot, message['photo'][-1]['file_id'])
        # recognizer = Vision()
        # text = recognizer.recognize(file_name)
        text = 'wasd asdw qwerty'
        http_client.send_document(file_name, message['photo'][-1]['file_id'], text,  user)
        delete(file_name)
        return "Send photo", data
