from adapt.intent import IntentBuilder
from adapt.engine import IntentDeterminationEngine
from brain.httpclient import HttpClient

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

[engine.register_entity(k, 'Search') for k in search_keywords]
[engine.register_entity(k, 'Next') for k in next_keywords]
[engine.register_entity(k, 'Previous') for k in previous_keywords]

# structure intent
intents = [
    IntentBuilder("SearchIntent").optionally("Search").build(),
    IntentBuilder("NextIntent").optionally('Next').build(),
    IntentBuilder("PreviousIntent").optionally('Previous').build(),
]

[engine.register_intent_parser(i) for i in intents]


def determine(text):
    return [i for i in engine.determine_intent(text) if i.get('confidence') > 0]


def search_intent(text, data=None, user=None):
    if not data:
        data = {}
    si = determine(text)
    if not si:
        data['next_page'] = 0
        data['prev_page'] = 0
        return "Sorry, I don't know how to do that yet.", data

    intent = si.pop()
    if intent['intent_type'] == 'SearchIntent':
        search_str = text.lower().replace(intent['Search'], '', 1).strip()
        data['search_query'] = search_str
        data['next_page'] = 2
        data['prev_page'] = 0
        client = HttpClient()
        print(client.search(text=search_str, user=user))
        return "Searching for: '{}'".format(search_str), data

    if not data or not data.get('search_query'):
        data['next_page'] = 0
        data['prev_page'] = 0
        msg = "Please let me know what are you looking for. For example: search for unicorns"
        return msg, data

    if intent['intent_type'] == 'NextIntent':
        msg = "This is page {}.".format(data['next_page'])
        data['next_page'] += 1
        data['prev_page'] += 1
        return msg, data

    if intent['intent_type'] == 'PreviousIntent':
        msg = "This is page {}".format(data['prev_page'])
        data['next_page'] -= 1
        data['prev_page'] -= 1
        return msg, data
