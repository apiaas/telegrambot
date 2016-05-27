from adapt.intent import IntentBuilder
from adapt.engine import IntentDeterminationEngine
from brain.vision import Vision
import subprocess
from urllib.parse import urlparse, parse_qs
from document.views import document_search
from document.models import Document
from django.test import RequestFactory
from os.path import basename
import time

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
    # 'photo',
    # 'send photo',
    'thisisphotointentkey',
]

file_keywords = [
    # 'file',
    # 'send file',
    'thisisfileintentkey',
]

[engine.register_entity(k, 'Search') for k in search_keywords]
[engine.register_entity(k, 'Next') for k in next_keywords]
[engine.register_entity(k, 'Previous') for k in previous_keywords]
[engine.register_entity(k, 'Photo') for k in photo_keywords]
[engine.register_entity(k, 'File') for k in file_keywords]

# structure intent
intents = [
    IntentBuilder("SearchIntent").optionally("Search").build(),
    IntentBuilder("NextIntent").optionally('Next').build(),
    IntentBuilder("PreviousIntent").optionally('Previous').build(),
    IntentBuilder("PhotoIntent").optionally('Photo').build(),
    IntentBuilder("FileIntent").optionally('File').build(),
]

[engine.register_intent_parser(i) for i in intents]


def determine(text, message):
    if not text and message.get('photo'):
        text = 'thisisphotointentkey'
    if not text and message.get('document'):
        text = 'thisisfileintentkey'

    return [i for i in engine.determine_intent(text) if i.get('confidence') > 0]


async def download_file(bot, file_id):
    new_file = await bot.getFile(file_id)
    file_name = 'media/' + basename(new_file['file_path'])
    await bot.download_file(file_id, file_name)
    return file_name


def delete(name):
    subprocess.call(['rm', name])


def get_full_url(path):
    return path


def create_document(file_name=None, text=None, user=None):
    data = dict(processed_text=text, description='text test example', file=file_name, filename=basename(file_name),
                author=user, path='user_{0}/{1}_{2}'.format(user.id, str(time.time()), basename(file_name)))
    document = Document(**data)
    document.save()


def search(text=None, page=None, user=None):
    request_factory = RequestFactory()
    url = '/search/'
    if len(text) > 0:
        url += '?processed_text__contains=' + text
    if page:
        url += '&page={}'.format(page)
    request = request_factory.get(url)
    request.user = user
    response = document_search(request)
    return dict(response.data)

def parse_pages(response, data):
    data['next_page'] = 0
    if response.get('next'):
        prev_page = parse_qs(urlparse(response['next']).query).get('page')
        if prev_page:
            data['next_page'] = prev_page[0]
        else:
            data['next_page'] = 1

    data['prev_page'] = 0
    if response.get('previous'):
        prev_page = parse_qs(urlparse(response['previous']).query).get('page')
        if prev_page:
            data['prev_page'] = prev_page[0]
        else:
            data['prev_page'] = 1
    return data


async def search_intent(text, data=None, user=None, message=None, bot=None):
    if not data:
        data = {}
    si = determine(text, message)
    if not si:
        data['next_page'] = 0
        data['prev_page'] = 0
        return "Sorry, I don't know how to do that yet.", data

    intent = si.pop()
    if intent['intent_type'] == 'SearchIntent':
        search_str = text.lower().replace(intent['Search'], '', 1).strip()
        data['search_query'] = search_str
        response = search(text=search_str, user=user)
        data['next_page'] = 0
        data['prev_page'] = 0
        if response['count'] > 0:
            if response['count'] > 1:
                data['next_page'] = 2
            return "Searching for: '{}' \n{} \n{}".format(search_str, get_full_url(response['results'][0]['path']),
                                                          response['results'][0]['processed_text'][0:250]), data
        else:
            return "Searching for: '{}' no result".format(search_str), data

    if not data or not data.get('search_query'):
        data['next_page'] = 0
        data['prev_page'] = 0
        msg = "Please let me know what are you looking for. For example: search for unicorns"
        return msg, data

    if intent['intent_type'] == 'NextIntent':
        response = search(text=data['search_query'], user=user, page=data['next_page'])
        data = parse_pages(response, data)
        return "Searching for: '{}' \n{} \n{}".format(data['search_query'],
                                                      get_full_url(response['results'][0]['path']),
                                                      response['results'][0]['processed_text'][0:250]), data

    if intent['intent_type'] == 'PreviousIntent':
        response = search(text=data['search_query'], user=user, page=data['prev_page'])
        data = parse_pages(response, data)
        return "Searching for: '{}' \n{} \n{}".format(data['search_query'],
                                                      get_full_url(response['results'][0]['path']),
                                                      response['results'][0]['processed_text'][0:250]), data

    if intent['intent_type'] in ['PhotoIntent', 'FileIntent']:
        data['next_page'] = 0
        data['prev_page'] = 0
        if intent['intent_type'] in 'PhotoIntent':
            file_name = await download_file(bot, message['photo'][-1]['file_id'])
        if intent['intent_type'] in 'FileIntent':
            file_name = await download_file(bot, message['document']['file_id'])

        recognizer = Vision()
        text = recognizer.recognize(file_name)
        # text = 'some text'
        create_document(file_name, text, user)
        delete(file_name)
        return "Photo was indexed.", data
