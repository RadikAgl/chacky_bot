import json

from django.http import HttpResponseForbidden, HttpResponseBadRequest, JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from bot.bot_utils import message_handler, callback_handler
from djbot.settings import BOT_TOKEN


class TelegramView(View):
    def post(self, request, bot_token):
        if bot_token != BOT_TOKEN:
            return HttpResponseForbidden('Invalid token')

        try:
            payload = json.loads(request.body.decode('utf-8'))
        except ValueError:
            return HttpResponseBadRequest('Invalid request body')
        else:
            if payload.get('id'):
                callback_handler(payload)
            else:
                message_handler(payload)

        return JsonResponse({}, status=200)

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(TelegramView, self).dispatch(request, *args, **kwargs)
