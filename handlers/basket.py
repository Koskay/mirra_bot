import asyncio

from aiogram import types, Dispatcher

from dataclasses import dataclass

from emoji import emojize

from create_bot import dp, bot
from data_base import query_db
from keyboards import inline_kb

from FSM import create_order_fsm

from .client import show_menu_handler


@dataclass
class Basket:
    product_name: str
    product_quantity: int
    price: float


async def basket_handler(message: types.Message | types.CallbackQuery, **kwargs):
    user_id = message.from_user.id
    if type(message) == types.CallbackQuery:
        await bot.delete_message(message.message.chat.id, message.message.message_id)
        await message.answer()
        message = message.message
    else:
        await bot.delete_message(message.chat.id, message.message_id)
    basket = await query_db.get_basket(user_id)

    if not basket:
        not_mess = await message.answer('Ваша корзина пуста')
        await asyncio.sleep(2)
        await not_mess.delete()
    else:
        all_price = list()
        markup = await inline_kb.basket_kb(basket[0].basket.id)

        a = list()
        # await message.answer(f'{"<b>"}Ваша корзина:{"</b>"}\n', parse_mode='HTML')

        # product_markup = await inline_kb.basket_prod_kb(prod_id)

        for bas in basket:
            # product_markup = await inline_kb.basket_prod_kb(bas.product.id)

            prod_price = bas.quantity*bas.product.price
            all_price.append(prod_price)
            mess_text = f'{"<i>"}Название товара{"</i>"}:\n- {bas.product.name}\n'\
                                 f'{"<i>"}Количество{"</i>"}: {bas.quantity} шт\n'\
                                 f'{"<i>"}Артикул{"</i>"}: {bas.product.article}\n'\
                                 f'{"<i>"}Цена{"</i>"}: {prod_price} руб.'
            a.append(mess_text)
        text = '\n___________________\n'.join(a)
        mess = await message.answer(
                             f'{"<b>"}Ваша корзина:{"</b>"} ' + emojize(":shopping_bags:", language='alias') + '\n\n'
                             f'{text}'
                             f'\n\n{"<i>"}Общая сумма заказа{"</i>"}: {sum(all_price)} руб.'
                             , parse_mode='HTML', reply_markup=markup)


async def delete_product(callback: types.CallbackQuery, basket_id):
    user_id = callback.from_user.id
    markup = await inline_kb.delete_product(user_id, basket_id)
    await callback.message.edit_reply_markup(markup)
    await callback.answer('Выберите товар')


@dp.callback_query_handler(inline_kb.basket_cd.filter())
async def navigate_menu(call: types.CallbackQuery, callback_data: dict[str, str]):
    """ Ловит callback от кнопок и вызывает соответствующую функцию """

    variant = callback_data.get('variant')
    product_quntyti_id = callback_data.get('product_id')
    basket_id = callback_data.get('basket_id')
    # print(basket_id)

    if variant == 'return':
        # a = call
        await call.message.delete()

        # await show_menu_handler(call, basket='basket')

    elif variant == 'clean':
        await delete_product(call, basket_id)

    elif variant == 'relog':
        await basket_handler(call)

    elif variant == 'order':
        await create_order_fsm.cm_start_create_order(call)

    if product_quntyti_id != '0':
        await query_db.delete_product(product_quntyti_id, basket_id)
        await call.answer('Успешно')
        await basket_handler(call)


def register_handlers_basket(disp: Dispatcher):
    disp.register_message_handler(basket_handler, commands='basket')

