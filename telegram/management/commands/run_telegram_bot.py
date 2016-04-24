import asyncio
from django.core.management.base import BaseCommand, CommandError
from telegram.bot import Bot
from telegram.models import Config


class Command(BaseCommand):
    help = 'Start telegram bot.'

    def handle(self, *args, **options):

        config = Config.objects.filter(default=True).all()[0]
        if not config:
            raise CommandError('Default config was not found')

        self.stdout.write('Starting {} bot.'.format(config.name))
        loop = asyncio.get_event_loop()
        loop.create_task(Bot(config.token).message_loop())
        self.stdout.write('Listening ...')

        try:
            loop.run_forever()
        except KeyboardInterrupt:
            self.stdout.write('Shutting down.')
