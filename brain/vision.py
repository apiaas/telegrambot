import requests
import json
from base64 import b64encode


class Vision(object):
    key = 'AIzaSyD_qTrOwB1I7J76BM-7a9e3us0Q2JOYQm4'
    url = 'https://vision.googleapis.com/v1/images:annotate?key={}'.format(key)
    template = {
        "requests": [
            {
                "image": {
                    "content": ''
                },
                "features": [
                    # {
                    #     "type": "LANDMARK_DETECTION",
                    #     "maxResults": "5"
                    # },
                    # {
                    #     "type": "LABEL_DETECTION",
                    #     "maxResults": "5"
                    # },
                    {
                        "type": "TEXT_DETECTION",
                    }
                ]
            }
        ]
    }

    def recognize(self, file_name):
        with open(file_name, 'rb') as img_file:
            data = b64encode(img_file.read()).decode()
        self.template['requests'][0]['image']['content'] = data
        print('Sending data...')
        r = requests.post(self.url, json.dumps(self.template))
        data = json.loads(r.text)
        recognized_text = ''
        for item in data['responses'][0]['textAnnotations']:
            recognized_text += item['description'] + ' '
        return recognized_text
        # return data['responses'][0]['textAnnotations'][0]['description']
