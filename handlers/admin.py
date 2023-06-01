from aiogram import types, Dispatcher
from FSM import load_product_purpose, add_product_photo
from keyboards import inline_kb
from local_conf.config import ADMINS


# Запускает загрузку категории товара
async def load_purpose(message: types.Message):
    if str(message.from_user.id) in ADMINS:  # Список
        await load_product_purpose.cm_start_save_purpose(message)


#Запускает загрузку товара
async def load_product_photo(message: types.Message):
    if str(message.from_user.id) in ADMINS:
        # save = 'save_purpose'  # Передает флаг для загрузки товара
        # markup = await inline_kb.categories_kb(save)
        await add_product_photo.cm_start_add_photo(message)


# async def get_user_discount(message: types.Message):
#     if str(message.from_user.id) in admins:
#         await check_discount.cm_start_query_discount(message)


# Регистрация хендлеров
def register_handlers_admin(dp: Dispatcher):
    dp.register_message_handler(load_product_photo, commands='load_photo')
    dp.register_message_handler(load_purpose, commands='save_purpose')
    # dp.register_message_handler(get_user_discount, commands='discount')