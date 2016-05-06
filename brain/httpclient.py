import requests
import json
from django.conf import settings


class HttpClient(object):
    def __init__(self):
        # self.users = {}
        self.users = {135109628: {'username': 135109628, 'token': u'8c47e2b80d7b8142ff338a51f8b387790d4570b9', 'password': u'yVYwf32Dwn'}, 168517558: {'username': 168517558, 'password': u'baE2B3sZjG'}}
        # self.api_host = 'http://localhost:8008'
        self.api_host = settings.TELEGRAMBOT_API_HOST

    def register_user(self, user_id):
        url = self.api_host + '/api/register/'
        r = requests.post(url=url, data={'username': user_id})
        if r.status_code == 201:
            self.users[user_id] = {'username': user_id, 'password': json.loads(r.text)['password']}
            return self.auth(user_id)
        return None

    def get_user_token(self, user_id):
        user = self.users.get(user_id)
        if user:
            if user.get('token'):
                return user.get('token')
            elif user.get('password'):
                return self.auth(user_id)
        return self.register_user(user_id)

    def auth(self, user_id):
        url = self.api_host + '/api/auth-token/'
        r = requests.post(url=url,
                          data={'username': self.users[user_id]['username'],
                                'password': self.users[user_id]['password']})
        if r.status_code == 200:
            token = json.loads(r.text)['token']
            self.users[user_id]['token'] = token
            return token
        return None

    def search(self, text=None, page=None, user=None):
        headers = {'Authorization': 'Token ' + self.get_user_token(user.telegram_id)}
        url = self.api_host + '/search/'
        # url += '?telegram_user_id=' + str(user['id'])
        if len(text) > 0:
            url += '?processed_text__contains=' + text
        if page:
            url += '&page={}'.format(page)
        r = requests.get(url=url, headers=headers)
        if r.status_code == 403:
            self.auth(user.telegram_id)
            return self.search(text=text, user=user)
        result = json.loads(r.text)
        return result

    def send_document(self, filename=None, user=None):
        url = self.api_host + '/api/document/document/'
        headers = {'Authorization': 'Token ' + self.get_user_token(user['id'])}
        files = {'file': open(filename, 'rb')}
        r = requests.post(url=url, files=files, headers=headers,
                          data={'processed_text': 'tra-ta-ta wasd asdw', 'text': 'text test example'})
        response = json.loads(r.text)
        processed_text = 'tra-ta-ta asd wasd'
        # processed_text = recognize(filename=filename)
        # self.send_text(user=user, doc_id=response['doc_id'], text=processed_text)
        # return response['info']
        if r.status_code == 403:
            self.auth(user['id'])
            return self.send_document(filename, user)
        return response
