from aiogram.types import BotCommand, BotCommandScopeChat
from create_bot import bot


# выводит меню команд
async def set_def_com(tbot: bot, user_id: int):
    return await tbot.set_my_commands(
        commands=[
            BotCommand('/catalog', 'Показать меню'),
            BotCommand('/basket', 'Просмотреть корзину'),
            BotCommand('/start', 'Общее описание бота'),
            # BotCommand('/distributor', 'Добавить номер дистрибутива'),
            # BotCommand('/basket', 'Просмотреть корзину'),
            BotCommand('/search', 'Поиск товара по артикулу или названию'),
            BotCommand('/contacts', 'Наши кнотакты'),
        ],
        scope=BotCommandScopeChat(user_id)
    )

