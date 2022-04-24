from django.core.management import BaseCommand

from bot.models import Game


class Command(BaseCommand):
    def handle(self, *args, **options):
        games_amount = Game.objects.count()
        for num in range(games_amount, games_amount + 5):
            game = Game(
                name='game' + str(num),
                description='description' + str(num)
            )
            game.save()

        self.stdout.write('Games added successfully')
