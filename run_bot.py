import openpyxl

from aiogram.utils import executor

from dataclasses import dataclass
from create_bot import dp
from data_base import settings_db, query_db
from handlers import client, admin, basket, other
from FSM import load_product_purpose, add_product_photo, create_order_fsm, queston_to_employee, answer_to_client


# @dataclass
# class Product:
#     article: int
#     name: str
#     volume: str
#     price_d: float
#     price: float
#     pv: float
#
#
# book = openpyxl.open('МИРРА ПРАЙС 01АПР 2023.xlsx', read_only=True)
#
# sheet = book.active
#
# cells = sheet['A330':'G345']
#
#
# def read_xml_file():
#     product_list = []
#     for article, name, none, volume, price_d, price, pv in cells:
#         product = Product(article=article.value,
#                           name=name.value,
#                           volume=volume.value,
#                           price_d=float(price_d.value),
#                           price=float(price.value),
#                           pv=pv.value)
#         product_list.append(product)
#
#     return product_list


# Запуск бота
async def on_startup(_) -> None:
    print('bot is online')
    if await settings_db.db_connect():  # Проверка на наличие подключения к базе
        print('database connect')
        await query_db.load_categories()
        # await query_db.create_products(read_xml_file())


admin.register_handlers_admin(dp)
load_product_purpose.register_handlers_save_purpose(dp)
create_order_fsm.register_handlers_create_order(dp)
add_product_photo.register_handlers_load_image(dp)
queston_to_employee.register_handlers_create_question(dp)
answer_to_client.register_handlers_create_answer_on_question(dp)
basket.register_handlers_basket(dp)
client.register_handlers_client(dp)
other.register_handlers_other(dp)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)