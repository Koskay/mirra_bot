from aiogram import types, Dispatcher

from FSM import queston_to_employee, answer_to_client


async def search_handler(message: types.Message):
    await message.answer('В разработке')


async def contacts_handler(message: types.Message):
    await message.answer(
        'Мобильный телефон WhatsApp:\n+79013151262 (Если есть вопросы - пишите сразу сюда. Отвечаем в рабочее время.)\n\nАдрес: г. Санкт-Петербург, ул.Пушкинская, д.11, помещение 15-Н (отдельный вход) ( м."Пл Восстания"/"Маяковская" )\n\nТелефон: +7 (812) 715-1262\n\nВремя работы: Пн-Пт с 11:00 до 19:00, Сб 11-15,\nВс-выходной\n\nЭлектронная почта:\n\n office@mirraspb.ru (но лучше пишите на WhatsApp)')


async def question_handler(message: types.Message):
    await queston_to_employee.cm_start_create_question(message)


async def answer_on_question_handler(call: types.CallbackQuery):
    await answer_to_client.cm_start_create_answer(call, call.data)


async def other(message: types.Message):
    """ Обрабатывает некоректные команды пользователя"""

    user_text_low = message.text.lower()
    user_text_list = user_text_low.split()

    if 'время' in user_text_list:
        await message.answer('Время работы: Пн-Пт с 11:00 до 19:00, Сб 11-15,\nВс-выходной\n'
                             'Подробная информация: /contacts')
    elif 'телефон' in user_text_list:
        await message.answer('Мобильный телефон WhatsApp:\n+79013151262 '
                             '(Если есть вопросы - пишите сразу сюда. Отвечаем в рабочее время.)'
                             'Подробная информация: /contacts')
    elif 'адрес' in user_text_list:
        await message.answer('Адрес: г. Санкт-Петербург, ул.Пушкинская, д.11, помещение 15-Н'
                             ' (отдельный вход) ( м."Пл Восстания"/"Маяковская" )'
                             'Подробная информация: /contacts')
    else:
        await message.answer('Не нашли нужной информации?\n'
                             'Напишите вопрос нашему сотруднику: /question')


def register_handlers_other(disp: Dispatcher):
    disp.register_message_handler(search_handler, commands='search')
    disp.register_message_handler(contacts_handler, commands='contacts')
    disp.register_message_handler(question_handler, commands='question')
    disp.register_callback_query_handler(answer_on_question_handler)
    disp.register_message_handler(other)
