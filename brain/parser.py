from adapt.intent import IntentBuilder
from adapt.engine import IntentDeterminationEngine
from brain.vision import Vision
import subprocess
from urllib.parse import urlparse, parse_qs
from document.views import document_search
from document.models import Document
from django.test import RequestFactory
from os.path import basename

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

delete_keywords = [
    'this_is_delete_intent_key',
]

photo_keywords = [
    'this_is_upload_photo_intent_key',
]

file_keywords = [
    'this_is_upload_file_intent_key',
]

image_keywords = [
    'image',
    'this_is_get_image_intent_key'
]

[engine.register_entity(k, 'Search') for k in search_keywords]
[engine.register_entity(k, 'Next') for k in next_keywords]
[engine.register_entity(k, 'Previous') for k in previous_keywords]
[engine.register_entity(k, 'Delete') for k in delete_keywords]
[engine.register_entity(k, 'Photo') for k in photo_keywords]
[engine.register_entity(k, 'File') for k in file_keywords]
[engine.register_entity(k, 'Image') for k in image_keywords]

# structure intent
intents = [
    IntentBuilder("SearchIntent").optionally("Search").build(),
    IntentBuilder("NextIntent").optionally('Next').build(),
    IntentBuilder("PreviousIntent").optionally('Previous').build(),
    IntentBuilder("DeleteIntent").optionally('Delete').build(),
    IntentBuilder("PhotoIntent").optionally('Photo').build(),
    IntentBuilder("FileIntent").optionally('File').build(),
    IntentBuilder("ImageIntent").optionally('Image').build(),
]

[engine.register_intent_parser(i) for i in intents]


def determine(text, message):
    if not text and message.get('photo'):
        text = 'this_is_upload_photo_intent_key'
    if not text and message.get('document'):
        text = 'this_is_upload_file_intent_key'

    return [i for i in engine.determine_intent(text) if i.get('confidence') > 0]

async def download_file(bot, file_id):
    new_file = await bot.getFile(file_id)
    file_name = 'media/' + basename(new_file['file_path'])
    await bot.download_file(file_id, file_name)
    return file_name


def delete(name):
    subprocess.call(['rm', name])


def create_document(file_id=None, text=None, user=None):
    data = dict(processed_text=text, file_id=file_id, author=user)
    document = Document(**data)
    document.save()


def search(text=None, page=None, user=None):
    request_factory = RequestFactory()
    url = '/search/'
    if len(text) > 0:
        url += '?processed_text__contains=' + text
    if page and int(page) > 1:
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
    else:
        data['image'] = None
    data['result'] = False
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
            data['result'] = True
            if response['count'] > 1:
                data['next_page'] = 2
            return "Searching for: '{}' \n{}".format(search_str,
                                                     response['results'][0]['highlighted']), data
        else:
            return "Searching for: '{}' no result".format(search_str), data

    if not data or not data.get('search_query'):
        data['next_page'] = 0
        data['prev_page'] = 0
        msg = "Please let me know what are you looking for. For example: search for unicorns"
        return msg, data

    if intent['intent_type'] == 'NextIntent':
        data['result'] = True
        response = search(text=data['search_query'], user=user, page=data['next_page'])
        data = parse_pages(response, data)
        return "Searching for: '{}' \n{}".format(data['search_query'],
                                                 response['results'][0]['highlighted']), data

    if intent['intent_type'] == 'PreviousIntent':
        data['result'] = True
        response = search(text=data['search_query'], user=user, page=data['prev_page'])
        data = parse_pages(response, data)
        return "Searching for: '{}' \n{}".format(data['search_query'],
                                                 response['results'][0]['highlighted']), data

    if intent['intent_type'] in ['PhotoIntent', 'FileIntent']:
        data['next_page'] = 0
        data['prev_page'] = 0
        if intent['intent_type'] in 'PhotoIntent':
            file_id = message['photo'][-1]['file_id']
        if intent['intent_type'] in 'FileIntent':
            file_id = message['document']['file_id']
        file_name = await download_file(bot, file_id)

        recognizer = Vision()
        text = recognizer.recognize(file_name)
        # text = 'some text'
        create_document(file_id, text, user)
        delete(file_name)
        return "Photo was indexed.", data

    if intent['intent_type'] == 'ImageIntent':
        if data['next_page'] != 0:
            page = int(data['next_page']) - 1
        else:
            page = int(data['prev_page']) + 1
        response = search(text=data['search_query'], user=user, page=page)
        data['image'] = response['results'][0]['file_id']
        return None, data

    if intent['intent_type'] == 'DeleteIntent':
        data['prev_page'] = int(data['prev_page'])
        data['next_page'] = int(data['next_page'])
        if data['next_page'] != 0:
            current_page = data['next_page'] - 1
        else:
            current_page = data['prev_page'] + 1

        response = search(text=data['search_query'], user=user, page=current_page)
        image_file_id = response['results'][0]['file_id']
        document = Document.objects.get(file_id=image_file_id)
        document.delete()

        if data['next_page'] == 0:
            current_page -= 1
            if data['prev_page'] > 0:
                data['prev_page'] -= 1

        if data['next_page'] == response['count']:
            data['next_page'] = 0

        response = search(text=data['search_query'], user=user, page=current_page)
        if response['count'] > 0:
            data['result'] = True
            if response['count'] > 1:
                data = parse_pages(response, data)
            return "Searching for: '{}' \n{}".format(data['search_query'],
                                                     response['results'][0]['highlighted']), data
        else:
            return "Searching for: '{}' no result".format(data['search_query']), data

