from django.db import models


def get_game():
    return Game.objects.first()


class TelegramUser(models.Model):
    chat_id = models.IntegerField(unique=True, verbose_name='Идентификатор чата')
    nickname = models.CharField(max_length=50, null=True, blank=True, verbose_name='Ник')
    info = models.TextField(null=True, blank=True, verbose_name='О себе')
    game = models.ForeignKey('Game', null=True, blank=True, related_name="users", on_delete=models.SET(get_game), verbose_name='Основная игра')

    def has_nickname(self):
        return True if self.nickname else False

    def get_card(self):
        return (f"Ник: {self.nickname}\n\n"
                f"Информация о пользователе:\n{self.info}\n\n"
                f"Любимая игра: {self.game}")

    def __str__(self):
        return self.nickname


class Game(models.Model):
    name = models.CharField(max_length=50, verbose_name='Название игры')
    description = models.TextField(blank=True, verbose_name='Описание игры')

    def __str__(self):
        return self.name


