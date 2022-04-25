from django.core.management import BaseCommand

import requests

from djbot.settings import BOT_TOKEN, HOST

URL = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook?url={HOST}/chacky/bot/{BOT_TOKEN}"


class Command(BaseCommand):
    def handle(self, *args, **options):
        r = requests.get(URL)

        self.stdout.write(str(r.json()))
