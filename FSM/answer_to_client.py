from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup

import asyncio

from emoji import emojize

from create_bot import bot
from keyboards import inline_kb

from local_conf.config import WORK_ID


class FSMCreateAnswer(StatesGroup):
    message = State()
    confirmation = State()


async def cm_start_create_answer(call: types.CallbackQuery, *args):
    global from_user_id
    from_user_id = int(args[0])

    await FSMCreateAnswer.message.set()

    await call.message.answer('Напишите ваш ответ')
    await call.answer()


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
    await FSMCreateAnswer.next()
    await message.reply('Отправить это сообщение ?', reply_markup=markup)


async def send_message(call: types.CallbackQuery,  state: FSMContext):
    async with state.proxy() as data:
        employee = call.from_user.full_name.split()[0]
        if call.data == 'Y':
            text = f'\n{"<b>"}Ответ на ваш вопрос:{"</b>"}\n\n' \
                   f'От сотрудника: {employee}\n\n' \
                   f'{data["message"]}'

            await bot.send_message(chat_id=from_user_id,
                                   text=emojize(':bangbang:', language='alias') + f'{text}', parse_mode='HTML')
        else:
            await call.message.answer('Всего доброго')
            await call.answer()
    await state.finish()
    await call.answer('Сообщение отправлено')


def register_handlers_create_answer_on_question(dp: Dispatcher):
    dp.register_message_handler(cancel_state, Text(equals='отмена', ignore_case=True), state='*')
    dp.register_message_handler(save_user_message, state=FSMCreateAnswer.message)
    dp.register_callback_query_handler(send_message, state=FSMCreateAnswer.confirmation)