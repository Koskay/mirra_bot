from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from data_base import query_db
from aiogram.dispatcher.filters.state import State, StatesGroup


class FSMPurposeNameSave(StatesGroup):
    code= State()


# Начало состояния сохранения категории
async def cm_start_save_purpose(message: types.Message):
    await FSMPurposeNameSave.code.set()
    await message.answer('Введите ваш персональный номер дистрибутива')


# Отмена сохранения в бд
async def cancel_state(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    await message.delete()
    await message.answer('Сохранение отменено')
    await message.answer('Обращайся')


# Сохранение названия категории
# async def load_category_name(message: types.Message,  state: FSMContext):
#     category_list = await query_db.get_categories()
#     category_text = ''
#     for category in category_list:
#         category_text += f'{category.name} -- {category.id}\n'
#     async with state.proxy() as data:
#         data['name'] = message.text
#     await FSMPurposeNameSave.next()
#     await message.reply('Запишите номера из списка, подходящих для данной категории товаров через пробел')
#     await message.answer(category_text)


# Сохранение в бд модели к данной категории
async def load_models_list(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['code'] = message.text
        data['user'] = message.from_user.id
    await query_db.create_code(data)
    await state.finish()
    await message.reply('Успешно!')


# Регистрация хендлеров
def register_handlers_save_purpose(dp: Dispatcher):
    dp.register_message_handler(cancel_state, Text(equals='отмена', ignore_case=True), state='*')
    dp.register_message_handler(load_models_list, state=FSMPurposeNameSave.code)
    # dp.register_message_handler(load_models_list, state=FSMPurposeNameSave.category)

