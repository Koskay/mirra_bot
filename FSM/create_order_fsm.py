from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup

from typing import TypedDict
from dataclasses import dataclass

from keyboards import inline_kb
from data_base import query_db, settings_db

from handlers.order import send_order


class BasketHistory(TypedDict):
    product_name: str
    article: int
    price: float
    quantity: int


@dataclass
class UserInfo:
    address: str
    phone_number: str


user_info = None


class FSMCreateOrder(StatesGroup):
    name = State()
    phone = State()
    delivery = State()
    comment = State()
    address = State()


# Начало состояния сохранения заказа
async def cm_start_create_order(message: types.CallbackQuery):
    user = await query_db.get_user(message.from_user.id)
    if user.address:
        global user_info
        user_info = UserInfo(address=user.address, phone_number=user.phone_number)
    await FSMCreateOrder.name.set()
    await message.message.answer('Напишите ваше ФИО')
    await message.answer()


# Отмена сохранения в бд
async def cancel_state(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    await message.delete()
    await message.answer('Сохранение отменено')
    await message.answer('Обращайся')


async def save_name(message: types.Message,  state: FSMContext):
    async with state.proxy() as data:
        data['full_name'] = message.text
    await FSMCreateOrder.next()
    if user_info:
        await message.reply(f'Если Ваш номер {"<b>"}{user_info.phone_number}{"</b>"}\nНапишите "Да"\n'
                            f'Либо напишите актуальный номер телефона', parse_mode='HTML')
    else:
        await message.reply(f'Напишите номера телефона в формате:\nПример {"<b>"}89215553322{"</b>"}', parse_mode='HTML')


async def save_phone(message: types.Message, state: FSMContext):
    if message.text.lower() == 'да':
        async with state.proxy() as data:

            data['phone_number'] = user_info.phone_number
        await FSMCreateOrder.next()
        markup = await inline_kb.delivery_kb()
        await message.answer('Выберите службу доставки', reply_markup=markup)
    else:
        if not message.text.isdigit():
            await message.reply('Телефон должен состоять только из цифр')
            await message.answer(f'Напишите номера телефона в формате:\nПример {"<b>"}89215553322{"</b>"}',
                                 parse_mode='HTML')
        elif len(message.text) != 11:
            await message.reply('Некорректный номер телефона')
            await message.answer(f'Напишите номера телефона в формате:\nПример {"<b>"}89215553322{"</b>"}',
                                 parse_mode='HTML')
        else:
            async with state.proxy() as data:

                data['phone_number'] = message.text
            await FSMCreateOrder.next()
            markup = await inline_kb.delivery_kb()
            await message.answer('Выберите службу доставки', reply_markup=markup)


async def save_delivery(message: types.CallbackQuery,  state: FSMContext):

    async with state.proxy() as data:
        data['delivery'] = message.data
    await message.answer()
    await FSMCreateOrder.next()
    await message.message.answer('Напишите комментарий к заказу')


async def save_comment(message: types.Message,  state: FSMContext):
    async with state.proxy() as data:
        data['comment'] = message.text
    await FSMCreateOrder.next()
    if user_info:
        await message.answer(f'Если это актуальный адрес доставки:\n{"<b>"}{user_info.address}{"</b>"}\nНапишите "Да"\n'
                             f'Либо напишите акутальный адрес доставки',
                             parse_mode='HTML')
    else:
        await message.reply('Напишите полный адрес получения')


async def save_address(message: types.Message,  state: FSMContext):

    async with state.proxy() as data:
        if message.text.lower() == 'да':
            data['address'] = user_info.address
        else:
            data['address'] = message.text
            await query_db.update_user_info(user_id=message.from_user.id,
                                            address=data['address'],
                                            phone_number=data['phone_number'])
        data['from_user'] = message.from_user.id
        basket = await query_db.get_basket(message.from_user.id)
        product_list = []
        total_price = []
        for bas in basket:
            price = float(bas.product.price*bas.quantity)
            product_list.append(BasketHistory(**{'product_name': bas.product.name,
                                                 'article': bas.product.article,
                                                 'quantity': bas.quantity,
                                                 'price': price}))
            total_price.append(price)
        data['basket_history'] = {'products': product_list, 'total_price': sum(total_price)}
    transaction = await settings_db.database.transaction()
    try:
        order = await query_db.create_order(data)
        # print(a)
        await query_db.basket_delete(message.from_user.id)

        await send_order(order)
        await state.finish()
        # await exept(1,0)
        await message.reply('Ваш заказ успешно создан!\n'
                            f'Заказ № {order.id}\n'
                            f'На сумму: {order.basket_history["total_price"]} руб.')
        await transaction.commit()
    except Exception as err:
        await transaction.rollback()
        await message.reply('Что то пошло не так')
        raise err
    # else:
        # await transaction.commit()


async def exept(a,b):
    return a/b


# Сохранение названия категории
# async def load_category_name(message: types.Message,  state: FSMContext):
#     category_list = await query_db.get_categories()
#     category_text = ''
#     for category in category_list:
#         category_text += f'{category.name} -- {category.id}\n'
#     async with state.proxy() as data:
#         data['name'] = message.text
#     await FSMPurposeNameSave.next()
#     await message.reply('Напишите номера телефона в формате: ')
#     await message.answer(category_text)


# Сохранение в бд модели к данной категории
# async def load_models_list(message: types.Message, state: FSMContext):
#     async with state.proxy() as data:
#         data['code'] = message.text
#         data['user'] = message.from_user.id
#     await query_db.create_code(data)
#     await state.finish()
#     await message.reply('Успешно!')


# Регистрация хендлеров
def register_handlers_create_order(dp: Dispatcher):
    dp.register_message_handler(cancel_state, Text(equals='отмена', ignore_case=True), state='*')
    dp.register_message_handler(save_name, state=FSMCreateOrder.name)
    dp.register_message_handler(save_phone, state=FSMCreateOrder.phone)
    dp.register_callback_query_handler(save_delivery, state=FSMCreateOrder.delivery)
    dp.register_message_handler(save_comment, state=FSMCreateOrder.comment)
    dp.register_message_handler(save_address, state=FSMCreateOrder.address)
