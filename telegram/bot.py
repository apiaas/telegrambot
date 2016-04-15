import asyncio
import telepot
import telepot.async
from brain.models import Client
from brain import parser
from django.core.exceptions import ObjectDoesNotExist


async def in_thread(func, *args):
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, func, *args)
    return result


class ClientId(telepot.async.Bot):
    def _get_client(self, telegram_id):
        try:
            client = Client.objects.get(telegram_id=telegram_id)
        except ObjectDoesNotExist:
            client = None
        return client

    def _create_client(self, telegram_id, first_name, last_name):
        client = Client.objects.create(
            telegram_id=telegram_id, first_name=first_name,
            last_name=last_name
        )
        return client

    async def _get_or_create_client(self, msg):
        user_id = msg['from']['id']
        client = await in_thread(self._get_client, user_id)
        if not client:
            client = await in_thread(
                self._create_client, user_id,
                msg['from'].get('first_name', str(user_id)),
                msg['from'].get('last_name', '')
            )
        return client

    async def on_chat_message(self, msg):
        client = await self._get_or_create_client(msg)
        await self.on_client_message(msg, client)

    async def on_client_message(self, msg, client):
        raise NotImplementedError


class Bot(ClientId):
    async def on_client_message(self, msg, client):
        content_type, chat_type, chat_id = telepot.glance(msg)
        intents = parser.determine(msg['text'])
        if not intents:
            await self.sendMessage(
                chat_id, "Sorry, I don't know how to do that yet."
            )
            return

        intent = intents[0]
        time_str = parser.time_list_to_str(
            intent.get('Hour', 0), intent.get('Min', 0), intent.get('Sec', 0)
        )

        reply = 'Okay, I will ping you in {}'.format(time_str)
        await self.sendMessage(chat_id, reply)
