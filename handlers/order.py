from aiogram.utils.exceptions import BotBlocked

from create_bot import bot

from local_conf.config import WORK_ID, ADMINS


async def send_order(order) -> None:

    text = f'{"<b>"}Заказ № {order.id}{"</b>"}\nОформил: {order.full_name}\nТелефон: {order.phone_number}\nТип доставки: {order.delivery}' \
           f'\nАдрес доставки: {order.address}\nCвязь в телеграмме: tg://user?id={order.from_user.id}\n\n' \
           f'{"<b>"}Состав заказа:{"</b>"}\n{format_order_answer(order.basket_history)}'

    try:
        await bot.send_message(chat_id=WORK_ID,
                               text=f'{text}', parse_mode='HTML')

    except BotBlocked:
        await bot.send_message(chat_id=ADMINS[0],
                               text=f'{text}', parse_mode='HTML')
    # for user in users:
    #     #  обработать исключение
    #     try:
    #         await bot.send_message(chat_id=user.id,
    #                                text=f'У нас новое поступление в коллекции {model.title}, /catalog ')
    #         if not user.active:
    #             await sql_commands.set_active(user.id, True)
    #     except BotBlocked:
    #         await sql_commands.set_active(user.id, False)


def format_order_answer(order: dict):

    products = []

    for product in order['products']:
        # product_markup = await inline_kb.basket_prod_kb(bas.product.id)

        # prod_price = bas.quantity * bas.product.price
        # all_price.append(prod_price)
        mess_text = f'{"<i>"}Название товара{"</i>"}:\n- {product["product_name"]}\n' \
                    f'{"<i>"}Количество{"</i>"}: {product["quantity"]} шт\n' \
                    f'{"<i>"}Артикул{"</i>"}: {product["article"]}\n' \
                    f'{"<i>"}Цена{"</i>"}: {product["price"]} руб.'
        products.append(mess_text)

    text = '\n___________________\n'.join(products)

    text_answer = f'{text}'\
                  f'\n\n{"<i>"}Общая сумма заказа{"</i>"}: {order["total_price"]} руб.'

    return text_answer
