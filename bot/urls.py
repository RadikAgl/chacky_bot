from django.urls import re_path

from bot.views import TelegramView

urlpatterns = [
    re_path(r'^bot/(?P<bot_token>.+)/$', TelegramView.as_view(), name='command'),
]