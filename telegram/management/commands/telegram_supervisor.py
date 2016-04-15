import sys
import os
import getpass
from django.core.management.base import BaseCommand, CommandError
from django.template import Context, Template
from django.conf import settings
from subprocess import run, PIPE


supervisor_template = """
[unix_http_server]
file=%(here)s/supervisord/supervisor.sock

[supervisord]
logfile=supervisord/supervisor.log
pidfile=supervisord/supervisor.pid

[program:telegram_bot]
command={{python}} manage.py run_telegram_bot
directory={{work_dir}}
user={{user}}
autorestart=true
redirect_stderr=true

[supervisorctl]
serverurl=unix://%(here)s/supervisord/supervisor.sock

[rpcinterface:supervisor]
supervisor.rpcinterface_factory = supervisor.rpcinterface:make_main_rpcinterface
"""


class Command(BaseCommand):
    help = 'Manage telegram bot with supervisor.'
    conf_name = 'supervisord.conf'

    def handle(self, *args, **options):
        self.stdout.write('Generating {} ...'.format(self.conf_name))
        template = Template(supervisor_template)
        context = Context({
            'python': sys.executable,
            'work_dir': settings.BASE_DIR,
            'user': getpass.getuser(),
        })
        with open(os.path.join(settings.BASE_DIR, self.conf_name), 'w') as f:
            f.write(template.render(context))

        process = run('which supervisord', shell=True, stdout=PIPE)
        if process.returncode != 0:
            raise CommandError('supervisor is not installed.')

        self.stdout.write('Starting supervisor process ...')
        process = run(
            'supervisord -c {}'.format(self.conf_name), shell=True, stdout=PIPE
        )
        if process.returncode != 0:
            raise CommandError('Failed to start supervisor.')

        self.stdout.write(
            'Bot was started successfully. You can use `supervisorctl` to manage it.'
        )





