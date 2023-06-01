from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData
from emoji.core import emojize

from data_base import query_db

menu_cd = CallbackData('in_kb_level', 'level', 'category_id', 'product_id', 'choice_inline_kb_out_product', 'one', 'count')
basket_cd = CallbackData('basket', 'variant', 'user_id', 'product_id', 'basket_id')


# функция устанавливает параметры по умолчанию, если они не были переданы
def make_callback_data(product_id=0, category_id=0, one=False, choice_inline_kb_out_product='', count=0, **kwargs):

    return menu_cd.new(product_id=product_id, category_id=category_id,
                       choice_inline_kb_out_product=choice_inline_kb_out_product, one=one, count=count, **kwargs)


def make_callback_data_basket(variant='', user_id=0, product_id=0, basket_id=0):

    return basket_cd.new(variant=variant, user_id=user_id, product_id=product_id, basket_id=basket_id)


async def categories_kb() -> InlineKeyboardMarkup:
    """Инлайн клавиатура с категориями"""
    markup = InlineKeyboardMarkup(row_width=2)

    curr_level = 0

    categories = await query_db.get_categories()

    for category in categories:
        butt_text = category.name
        data = make_callback_data(level=curr_level + 1, category_id=category.id)
        markup.insert(
            InlineKeyboardButton(text=butt_text, callback_data=data)
        )
    return markup


async def back_to_level(level, count, category_id, len_list) -> InlineKeyboardMarkup:

    data = make_callback_data(level=int(level)-1)
    data_count = make_callback_data(level=int(level), count=count, category_id=category_id)
    more_button = InlineKeyboardButton('Показать еще', callback_data=data_count)
    back_button = InlineKeyboardButton('Вернуться в каталог', callback_data=data)
    if len_list-count >= 4:
        back_keyboard = InlineKeyboardMarkup(resize_keyboard=True).add(more_button).add(back_button)
    else:
        back_keyboard = InlineKeyboardMarkup(resize_keyboard=True).add(back_button)
    return back_keyboard


async def add_item_basket(product_id, level, category_id) -> InlineKeyboardMarkup:

    markup = InlineKeyboardMarkup(row_width=2)
    basket_data = make_callback_data(level=5, choice_inline_kb_out_product='add_basket',
                                     product_id=product_id, category_id=category_id)

    add_to_basket_text = 'В корзину ' + emojize(':shopping_bags:', language='alias')
    more_text = 'Подробннее ' + emojize(':page_with_curl:', language='alias')

    product_description_data = make_callback_data(level=int(level)+1,choice_inline_kb_out_product='show_product',
                                                  product_id=product_id, category_id=category_id)

    basket_button = InlineKeyboardButton(text=add_to_basket_text, callback_data=basket_data)

    if int(level) != 2:
        show_product = InlineKeyboardButton(text=more_text, callback_data=product_description_data)
    else:
        show_product = InlineKeyboardButton(
                text='Назад ' + emojize(':feet:', language='alias'),
                callback_data=make_callback_data(level=int(level) - 1, product_id=product_id,
                                                 category_id=category_id, one=True)
            )

    markup.row(
        basket_button, show_product
    )

    return markup


async def create_order_kb(basket_id):
    avito_url = InlineKeyboardButton(text='Оформить заказ', callback_data='ok')
    avito_keyboard = InlineKeyboardMarkup(resize_keyboard=True).add(avito_url)
    return avito_keyboard


async def basket_kb(basket_id):
    markup = InlineKeyboardMarkup(resize_keyboard=True)

    order_data = make_callback_data_basket(variant='order')
    clean_basket = make_callback_data_basket(variant='clean', basket_id=basket_id)
    return_catalog = make_callback_data_basket(variant='return')
    relog_basket = make_callback_data_basket(variant='relog')
    markup.add(
        InlineKeyboardButton(text='Оформить заказ  ' + emojize(':gift:', language='alias'),
                             callback_data=order_data)
    ).add(
        InlineKeyboardButton(text='Удалить товар  ' + emojize(":x:", language='alias'),
                             callback_data=clean_basket)
    ).add(
        InlineKeyboardButton(text='Вернуться в каталог  ' + emojize(':feet:', language='alias'),
                             callback_data=return_catalog)
    ).add(
        InlineKeyboardButton(text='Обновить корину  ' + emojize(':hourglass:', language='alias'),
                             callback_data=relog_basket)
    )
    return markup


async def delivery_kb():
    markup = InlineKeyboardMarkup(resize_keyboard=True)

    # order_data = make_callback_data_basket(variant='order')
    # clean_basket = make_callback_data_basket(variant='clean')
    # return_catalog = make_callback_data_basket(variant='return')
    # relog_basket = make_callback_data_basket(variant='relog')
    markup.add(
        InlineKeyboardButton(text='CDEK', callback_data='CDEK')
    ).add(
        InlineKeyboardButton(text='Почта', callback_data='Почта')
    ).add(
        InlineKeyboardButton(text='Самозабор', callback_data='Самозабор')
    )
    return markup


# async def basket_prod_kb(prod_id):
#     markup = InlineKeyboardMarkup(resize_keyboard=True)
#
#     # order_data = make_callback_data_basket(variant='order')
#     # clean_basket = make_callback_data_basket(variant='clean')
#     # return_catalog = make_callback_data_basket(variant='return')
#     # relog_basket = make_callback_data_basket(variant='relog')
#     markup.add(
#         InlineKeyboardButton(text='Удалить', callback_data='DELETE')
#     )
#
#     return markup

async def delete_product(user_id, basket_id):
    products = await query_db.get_basket(user_id)
    markup = InlineKeyboardMarkup(resize_keyboard=True)
    for product in products:
        data = make_callback_data_basket(product_id=product.id, basket_id=basket_id)
        markup.add(
            InlineKeyboardButton(text=f'{product.product.name} ',
                                 callback_data=data)
        )
    return markup


async def confirmation_kb():
    markup = InlineKeyboardMarkup(resize_keyboard=True)
    markup.add(
        InlineKeyboardButton(text=f'ДА', callback_data='Y')
    ).add(
        InlineKeyboardButton(text=f'НЕТ', callback_data='N')
    )
    return markup


async def answer_to_user_kb(from_user_id):
    markup = InlineKeyboardMarkup(resize_keyboard=True)
    markup.add(
        InlineKeyboardButton(text=f'Ответить', callback_data=from_user_id)
    )

    return markup

