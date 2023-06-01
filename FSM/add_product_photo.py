from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from data_base import query_db
from aiogram.dispatcher.filters.state import State, StatesGroup


class FSMPhotoSave(StatesGroup):
    article = State()
    photo_id = State()


# Начало состояния сохранения категории
async def cm_start_add_photo(message: types.Message):
    await FSMPhotoSave.article.set()
    await message.answer('Введите артикл товара')


# Отмена сохранения в бд
async def cancel_state(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    await message.delete()
    await message.answer('Сохранение отменено')
    await message.answer('Обращайся')


# Сохранение в бд модели к данной категории
async def load_models_list(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['article'] = message.text
        # data['user'] = message.from_user.id
    await FSMPhotoSave.next()
    await message.reply('Загрузите фото')


async def load_photo(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['image'] = message.photo[0].file_id
        # data['user'] = message.from_user.id
    await query_db.update_product_image(data)
    await state.finish()
    await message.reply('Успешно!')


# Регистрация хендлеров
def register_handlers_load_image(dp: Dispatcher):
    dp.register_message_handler(cancel_state, Text(equals='отмена', ignore_case=True), state='*')
    dp.register_message_handler(load_models_list, state=FSMPhotoSave.article)
    dp.register_message_handler(load_photo, state=FSMPhotoSave.photo_id, content_types=['photo'])
