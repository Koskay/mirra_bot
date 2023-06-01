import asyncio

from contextlib import suppress

from dataclasses import dataclass
from aiogram import types, Dispatcher
from emoji import emojize
from data_base import query_db
from aiogram.utils.exceptions import (ButtonURLInvalid,
                                      BadRequest,
                                      MessageNotModified,
                                      MessageToDeleteNotFound, MessageCantBeDeleted)

from FSM import load_product_purpose
from create_bot import dp, bot

from keyboards import inline_kb
from set_commands import setting

message_list = list()
products_list = None
one_product = None
mess_reply = None


@dataclass
class ProductData:
    id: int
    name: str
    price: float
    price_d: float
    description: str
    article: int
    volume: str
    is_active: bool


async def distributs_handler(message: types.Message):
    await message.answer(f'Следуйте инструкциям, {message.from_user.full_name.split()[0]}.\n\n', parse_mode='HTML')
    await load_product_purpose.cm_start_save_purpose(message)


async def start_handler(message: types.Message):
    """ Обрабатвыет команду /start """

    await message.answer(f'Добро пожаловать, {message.from_user.full_name.split()[0]}.\n\n', parse_mode='HTML')
    await setting.set_def_com(message.bot, message.from_user.id)

    # Сохранение пользователя
    if message.from_user.username:
        await query_db.create_user(message.from_user.id, message.from_user.username)
    else:
        await query_db.create_user(message.from_user.id, message.from_user.full_name)


async def delete_message(messages):
    for message in messages:
        await message.delete()
    global message_list
    message_list = []


async def show_menu_handler(message: types.Message | types.CallbackQuery, **kwargs):
    """ Показывает меню с категориями"""

    markup = await inline_kb.categories_kb()
    if type(message) == types.CallbackQuery:
        await delete_message(message_list)

        await message.message.edit_text(f'{"<b>"}Линии Mirra{"</b>"} ' + emojize(':herb:', language='alias'),
                                        parse_mode='HTML')
        await message.message.edit_reply_markup(markup)
        await message.answer('Выберите Категорию')
    else:
        await message.answer(f'{"<b>"}Линии Mirra{"</b>"} ' + emojize(':herb:', language='alias'),
                             reply_markup=markup, parse_mode='HTML')


async def get_products_list_handler(callback: types.CallbackQuery, **kwargs):
    """ Отдает пользователю список продуктов по категориям"""
    global message_list, mess_reply, products_list

    category_id: int = kwargs['category_id']
    level = kwargs.get('level')
    count = int(kwargs.get('count'))

    if products_list:
        if products_list[0].product_category.id != category_id:
            products_list = None

    if not products_list:
        products: list = await query_db.get_products(category_id)
        len_products_list = f'Найдено товаров: {len(products)} шт'
        products_list = products.copy()
    else:
        products = products_list
        if len(products) - count <= 4:
            len_products_list = f'Не просмотренно: {0} шт'
        else:
            len_products_list = f'Не просмотренно товаров: {len(products) - count} шт'
    try:
        await callback.message.delete()
    except MessageToDeleteNotFound:
        await callback.message.answer('Не нажимать так быстро!!!')

    if not products:
        not_item = await callback.message.answer('Тут пока пусто')
        await asyncio.sleep(1)
        await not_item.delete()
    else:
        limit = 0
        for i in range(count, len(products)):
            markup = await inline_kb.add_item_basket(product_id=products[count].id,
                                                     level=level,
                                                     category_id=category_id)

            mess = await callback.message.answer(
                f'{"<b>"}{products[count].name}{"</b>"}\n___________________________\n'
                f'{"<i>"}Артикул{"</i>"}: {products[count].article}\n'
                f'{"<i>"}Цена{"</i>"}: {products[count].price} руб.\n',
                parse_mode='HTML', reply_markup=markup
            )

            message_list.append(mess)

            await asyncio.sleep(0.1)

            count += 1

            if limit == 4:
                break
            limit += 1

    delimiter = await callback.message.answer('.' + emojize(':small_red_triangle_down:' * 10, language='alias') + '.')
    message_list.append(delimiter)
    back_menu_markup = await inline_kb.back_to_level(level, count, category_id, len(products))

    message = await callback.message.answer(
        f'{"<b>"}{len_products_list}{"</b>"}' + emojize(":star2:", language='alias'),
        reply_markup=back_menu_markup, parse_mode='HTML')

    mess_reply = message
    await callback.answer()


async def get_product_handler(callback: types.CallbackQuery, **kwargs):
    global one_product, message_list
    category_id: int = kwargs['category_id']
    product_id = kwargs.get('product_id')
    level = kwargs.get('level')

    product = await query_db.get_product(product_id)
    one_product = ProductData(
        id=product.id,
        name=product.name,
        article=product.article,
        description=product.description,
        price=product.price,
        price_d=product.distributable_price,
        volume=product.volume,
        is_active=product.is_active,
    )

    markup = await inline_kb.add_item_basket(product_id, level, category_id)

    if one_product.is_active:
        product_availability = emojize(':white_check_mark:', language='alias')
    else:
        product_availability = emojize(':no_entry_sign:', language='alias')

    await callback.message.edit_text(
        f'{"<b>"}Название:{"</b>"}\n {one_product.name}\n\n'
        f'{"<b>"}Описание:{"</b>"}\n {one_product.description}\n\n'
        f'{"<b>"}Объем{"</b>"}: {one_product.volume}\n'
        f'{"<b>"}Цена{"</b>"}: {one_product.price} руб.\n'
        f'{"<b>"}Артикул{"</b>"}: {one_product.article}\n'
        f'{"<b>"}Наличие{"</b>"}: {product_availability}\n',
        parse_mode='HTML', reply_markup=markup
    )

    await callback.answer()


async def get_product_handler_one(callback: types.CallbackQuery, **kwargs):
    global one_product

    category_id: int = kwargs['category_id']
    level = kwargs.get('level')

    markup = await inline_kb.add_item_basket(product_id=one_product.id, level=level, category_id=category_id)

    await callback.message.edit_text(
                        f'{"<b>"}{one_product.name}{"</b>"}\n___________________________\n'
                        f'Цена: {one_product.price} руб.\n'
                        f'Артикул: {one_product.article}\n',
                        parse_mode='HTML', reply_markup=markup
        )

    await callback.answer()


async def add_product_in_basket(callback: types.CallbackQuery, **kwargs):

    user = callback.from_user.id
    product_id = kwargs.get('product_id')
    await query_db.get_or_create_basket(product_id, user)

    await callback.answer('Добавлено')


@dp.callback_query_handler(inline_kb.menu_cd.filter())
async def navigate_menu(call: types.CallbackQuery, callback_data: dict[str, str]):
    """ Ловит callback от кнопок и вызывает соответствующую функцию """

    curr_level: str = callback_data.get('level')
    category_id: int = int(callback_data.get('category_id'))
    choice_inline_kb_out_product: str = callback_data.get('choice_inline_kb_out_product')
    product_id: int = int(callback_data.get('product_id'))
    one: str = callback_data.get('one')
    count: int = int(callback_data.get('count'))

    # Уровень вложенности кнопок.
    levels = {
        '0': show_menu_handler,
        '1': get_products_list_handler,
        '5': add_product_in_basket,
    }

    if count != 0:
        curr_level = '1'

    if choice_inline_kb_out_product == 'show_product':
        levels['2'] = get_product_handler

    if one == 'True':
        levels['1'] = get_product_handler_one

    curr_level_func = levels[curr_level]

    await curr_level_func(
            call,
            level=curr_level,
            one=one,
            category_id=category_id,
            product_id=product_id,
            count=count,
        )


def register_handlers_client(disp: Dispatcher):
    disp.register_message_handler(start_handler, commands='start')
    disp.register_message_handler(distributs_handler, commands='distributor')
    disp.register_message_handler(show_menu_handler, commands='catalog')
