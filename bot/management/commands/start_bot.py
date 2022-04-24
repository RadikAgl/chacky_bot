import time

import requests
from django.core.management import BaseCommand

from bot.bot_utils import tg_bot

from telepot.loop import MessageLoop

from djbot.settings import BOT_TOKEN, HOST

URL = f'{HOST}/chacky/bot/{BOT_TOKEN}/'


class Command(BaseCommand):
    def handle(self, *args, **options):
        def bot_handler(msg):
            requests.post(url=URL, json=msg)

        MessageLoop(tg_bot, bot_handler).run_as_thread()
        while 1:
            time.sleep(10)
