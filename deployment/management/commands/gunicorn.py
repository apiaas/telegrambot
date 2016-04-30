import time
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from subprocess import run, PIPE


class Command(BaseCommand):
    help = 'Start gunicorn server.'

    def handle(self, *args, **options):
        process = run('which gunicorn', shell=True, stdout=PIPE)
        if process.returncode != 0:
            raise CommandError('Gunicorn is not installed.')

        cmd = 'gunicorn admin.wsgi -c deployment/gunicorn.conf.py'
        try:
            run(cmd, shell=True, cwd=settings.BASE_DIR)
        except KeyboardInterrupt:
            self.stdout.write(
                'Shutting down gunicorn.'
            )
        time.sleep(1)

