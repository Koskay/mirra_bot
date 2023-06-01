from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup

from typing import TypedDict

from emoji import emojize

from create_bot import bot
from keyboards import inline_kb

from local_conf.config import WORK_ID


class FSMCCreateQuestion(StatesGroup):
    message = State()
    confirmation = State()


async def cm_start_create_question(message: types.Message):
    await FSMCCreateQuestion.message.set()
    await message.answer('Напишите ваш вопрос')


async def cancel_state(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    await message.delete()
    await message.answer('Сохранение отменено')
    await message.answer('Обращайся')


async def save_user_message(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['message'] = message.text
    markup = await inline_kb.confirmation_kb()
    await FSMCCreateQuestion.next()
    await message.reply('Отправить это сообщение ?', reply_markup=markup)


async def send_message(call: types.CallbackQuery,  state: FSMContext):
    async with state.proxy() as data:
        markup = await inline_kb.answer_to_user_kb(call.from_user.id)
        if call.data == 'Y':
            text = f'\n{"<b>"}У вас новый вопрос{"</b>"}\n' \
                   f'От пользователя: {call.from_user.full_name}\n\n' \
                   f'{"<b>"}Вопрос:{"</b>"}\n' \
                   f'{data["message"]}'
            await bot.send_message(chat_id=WORK_ID,
                                   text=emojize(':bangbang:', language='alias') + f'{text}',
                                   reply_markup=markup, parse_mode='HTML')
        else:
            await call.message.answer('Всего доброго')
            await call.answer()
    await state.finish()
    await call.answer('Сообщение отправлено')
    # await message.answer()
    # await FSMCreateOrder.next()
    # await message.message.answer('Напишите полный адрес получения')


def register_handlers_create_question(dp: Dispatcher):
    dp.register_message_handler(cancel_state, Text(equals='отмена', ignore_case=True), state='*')
    dp.register_message_handler(save_user_message, state=FSMCCreateQuestion.message)
    dp.register_callback_query_handler(send_message, state=FSMCCreateQuestion.confirmation)