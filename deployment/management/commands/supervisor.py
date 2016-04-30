import sys
import os
import getpass
from django.core.management.base import BaseCommand, CommandError
from django.template import Context, Template
from django.conf import settings
from subprocess import run, PIPE


supervisor_template = """
[unix_http_server]
file={{app_base}}/tmp/supervisor.sock

[supervisord]
logfile={{app_base}}/log/supervisor.log
pidfile={{app_base}}/tmp/supervisor.pid

[program:telegram_bot]
command={{python}} manage.py run_telegram_bot
directory={{work_dir}}
user={{user}}
autorestart=true
redirect_stderr=true

[program:gunicorn]
command={{gunicorn}} admin.wsgi -c {{app_base}}/gunicorn.conf.py
directory={{work_dir}}
user={{user}}
autorestart=true
redirect_stderr=true


[supervisorctl]
serverurl=unix://{{app_base}}/tmp/supervisor.sock

[rpcinterface:supervisor]
supervisor.rpcinterface_factory = supervisor.rpcinterface:make_main_rpcinterface
"""


class Command(BaseCommand):
    help = 'Start supervisor managed processes.'
    conf_name = 'supervisord.conf'
    app_name = 'deployment'

    def handle(self, *args, **options):
        self.stdout.write('Generating {} ...'.format(self.conf_name))
        template = Template(supervisor_template)
        env = os.path.abspath(sys.exec_prefix)
        context = Context({
            'python': sys.executable,
            'gunicorn': os.path.join(env, 'bin/gunicorn'),
            'work_dir': settings.BASE_DIR,
            'user': getpass.getuser(),
            'app_base': os.path.join(settings.BASE_DIR, self.app_name)
        })
        config_file = os.path.join(
            settings.BASE_DIR, self.conf_name
        )

        with open(config_file, 'w') as f:
            f.write(template.render(context))

        process = run('which supervisord', shell=True, stdout=PIPE)
        if process.returncode != 0:
            raise CommandError('supervisor is not installed.')

        self.stdout.write('Starting supervisor process ...')
        process = run(
            'supervisord -c {}'.format(config_file), shell=True, stdout=PIPE
        )
        if process.returncode != 0:
            raise CommandError('Failed to start supervisor.')

        self.stdout.write(
            'Supervisor was started successfully. You can use `supervisorctl` to manage it.'
        )
