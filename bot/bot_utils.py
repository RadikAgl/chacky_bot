import random

import telepot
from telepot.namedtuple import InlineKeyboardButton, InlineKeyboardMarkup

from bot.models import TelegramUser, Game
from djbot.settings import BOT_TOKEN

tg_bot = telepot.Bot(BOT_TOKEN)

prev_msg = {}
messages_for_delete = {}


def display_help() -> str:
    """Возвращает текст справки по командам бота"""
    return ('Вас приветствует **ChackyBot!**\n'
            'Я могу выполнить следующие команды:\n'
            '/help - справка по командам\n'
            '/mycard - карточка пользователя\n'
            '/play - выбрать игрока для игры\n'
            '/edit - редактировать карточку\n'
            )


def games_keyboard(prefix: str, width: int = 3) -> InlineKeyboardMarkup:
    """Формирует и возвращает инлайн клавиатуру со списком доступных игр"""
    games = Game.objects.all().values('name')
    keyboard = []
    buttons = []

    for game in games:
        buttons.append(InlineKeyboardButton(text=game['name'], callback_data=prefix + game['name']))
        if len(buttons) == width:
            keyboard.append(buttons)
            buttons = []
    if buttons:
        keyboard.append(buttons)

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def add_user(msg: dict) -> None:
    """Добавляет текущего пользователя в базу данных"""
    chat_id = msg['chat']['id']
    nickname = msg['from']['username']
    user, created = TelegramUser.objects.get_or_create(chat_id=chat_id)
    if nickname:
        user.nickname = nickname
        user.save()


def edit_keyboard() -> InlineKeyboardMarkup:
    """Формирует и возвращает инлайн клавиатуру с полями, доступными для редактирования"""
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text='about myself', callback_data='myself'),
        InlineKeyboardButton(text='my game', callback_data='fv_game')
    ]])


def get_current_player_card(chat_id: int) -> str:
    """Возвращает карточку пользователя по идентификатору чата"""
    user = TelegramUser.objects.get(chat_id=chat_id)
    return user.get_card()


def get_random_player(chat_id: int, name: str) -> TelegramUser:
    """Возвращает случайного пользователя по любимой игре"""
    users = TelegramUser.objects.filter(game__name=name).exclude(chat_id=chat_id).exclude(nickname__isnull=True)
    if users:
        return random.choice(users)


def sent_invitation(nickname: str, opponent_id: int, game: str) -> None:
    """Отправляет приглашение пользователю"""
    message = f'Игрок @{nickname} приглашает тебя на игру "{game}"'
    tg_bot.sendMessage(opponent_id, message)


def has_access(msg: dict) -> bool:
    """Проверяет наличия ника пользователя"""
    chat_id = msg['chat']['id']
    user = TelegramUser.objects.get(chat_id=chat_id)
    if user.has_nickname():
        return True
    else:
        nickname = msg['from']['username']
        if nickname:
            user.nickname = nickname
            user.save()
            return True
        return False


def add_favorite_game(chat_id: int, my_game: str) -> None:
    """Добавляет основную игру пользователя в базу данных"""
    user = TelegramUser.objects.get(chat_id=chat_id)
    game = Game.objects.get(name=my_game)
    user.game = game
    user.save()


def add_user_info(msg: dict) -> None:
    """Добавляет информацию о пользователе в базу данных"""
    chat_id = msg['chat']['id']
    text = msg['text']
    user = TelegramUser.objects.get(chat_id=chat_id)
    user.info = text
    user.save()


def message_handler(msg: dict) -> None:
    """Обработка текстовых сообщений и команд"""
    global prev_msg
    global messages_for_delete
    keyboard = None
    chat_id = msg['chat']['id']
    text = msg['text']

    if messages_for_delete.get('chat_id'):
        tg_bot.deleteMessage(messages_for_delete.pop('chat_id'))

    if text == '/start':
        add_user(msg)
        prev_msg[chat_id] = msg.get('message_id')
        message = display_help()
        message += '\nДавай знакомиться, расскажи о себе'
    elif text == '/help':
        message = display_help()
    elif text == '/mycard':
        message = get_current_player_card(chat_id)
    elif text == '/play':
        if has_access(msg):
            message = 'Выбери игру'
            prefix = 'play_'
            keyboard = games_keyboard(prefix)
        else:
            message = 'У тебя не указан ник в телеграм аккаунте. Пожалуйста, укажи ник и попробуй снова.'
    elif text == '/edit':
        keyboard = edit_keyboard()
        message = 'Что хочешь изменить?'
    elif prev_msg.get(chat_id) and prev_msg.pop(chat_id) + 2 == msg.get('message_id'):
        add_user_info(msg)
        if not prev_msg.get(str(chat_id) + 'edit'):
            prefix = 'mygame_'
            message = 'Выбери любимую игру'
            keyboard = games_keyboard(prefix)
        else:
            del prev_msg[str(chat_id) + 'edit']
            message = 'Информация изменена'
    else:
        message = 'Я тебя не понимаю. Посмотри, что я умею в /help'
    msg = tg_bot.sendMessage(chat_id, message, reply_markup=keyboard)
    if keyboard:
        messages_for_delete['chat_id'] = telepot.message_identifier(msg)


def callback_handler(msg: dict) -> None:
    """Обработка нажатых кнопок инлайн клавиатур"""
    global messages_for_delete
    chat_id = msg['message']['chat']['id']
    message = 'Я вас не понимаю. Посмотри, что я умею в /help'
    keyboard = None

    if messages_for_delete.get('chat_id'):
        tg_bot.deleteMessage(messages_for_delete.pop('chat_id'))

    callback_data = msg['data']
    if callback_data.startswith('mygame'):
        my_game = callback_data.split('_')[1]
        message = 'Ваша основная игра добавлена'
        add_favorite_game(chat_id, my_game)
        if not has_access(msg['message']):
            message += '\nУ тебя не указан ник в телеграм аккаунте. Пожалуйста, укажи ник.'
        else:
            message = 'Подготовка завершена. Введи команду /play, чтобы выбрать игрока'

    elif callback_data.startswith('play'):
        game_name = callback_data.split('_')[1]
        player = get_random_player(chat_id, game_name)
        if player:
            message = player.get_card()
            keyboard = InlineKeyboardMarkup(inline_keyboard=[[
                InlineKeyboardButton(text='play', callback_data='sent_' + str(player.chat_id) + '_' + game_name),
                InlineKeyboardButton(text='next', callback_data='play_' + game_name)
            ]])
        else:
            message = 'Игроков не нашлось, попробуй другую игру'

    elif callback_data.startswith('sent'):
        opponent_chat_id = int(callback_data.split('_')[1])
        game = callback_data.split('_')[2]
        cur_user_nickname = msg['message']['chat']['username']
        sent_invitation(cur_user_nickname, opponent_chat_id, game)
        message = 'Приглашение отправлено'

    elif callback_data == 'myself':
        prev_msg[chat_id] = msg['message'].get('message_id')
        prev_msg[str(chat_id) + 'edit'] = True
        message = 'Расскажи о себе'

    elif callback_data == 'fv_game':
        prefix = 'mygame_'
        message = 'Выбери любимую игру'
        keyboard = games_keyboard(prefix)

    msg = tg_bot.sendMessage(chat_id, message, reply_markup=keyboard, parse_mode='markdown')

    if keyboard:
        messages_for_delete['chat_id'] = telepot.message_identifier(msg)
