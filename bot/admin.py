from django.contrib import admin

from bot.models import TelegramUser, Game


class TelegramUserAdmin(admin.ModelAdmin):
    list_display = [field.name for field in TelegramUser._meta.get_fields()]


class GameAdmin(admin.ModelAdmin):
    list_display = ['name',  'description']


admin.site.register(TelegramUser, TelegramUserAdmin)
admin.site.register(Game, GameAdmin)
