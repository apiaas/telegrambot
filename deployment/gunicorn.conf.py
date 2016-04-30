import os
import multiprocessing

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#bind = "127.0.0.1:8000"
#workers = multiprocessing.cpu_count() * 2 + 1

bind = 'unix:{}'.format(os.path.join(
    BASE_DIR, 'deployment', 'tmp', 'gunicorn.sock')
)
#worker_class = 'gaiohttp'
