import ormar

from .settings_db import database, metadata
from enum import Enum


class UserDiscountEnum(Enum):
    distributable = '1'
    discount = '2'
    ordinary = '3'


class MetaData(ormar.ModelMeta):
    metadata = metadata
    database = database


# Модель категории MIRRA
class ProductCategory(ormar.Model):
    class Meta(MetaData):
        pass

    id: int = ormar.Integer(primary_key=True, autoincrement=True, index=True)
    name: str = ormar.String(max_length=150)


class Product(ormar.Model):
    class Meta(MetaData):
        pass

    id: int = ormar.Integer(primary_key=True, autoincrement=True, index=True)
    name: str = ormar.String(max_length=255)
    image: str = ormar.String(max_length=500, nullable=True)
    description: str = ormar.Text(nullable=True)
    article: int = ormar.Integer(default=0, index=True)
    volume: str = ormar.String(max_length=50, default='0')
    price = ormar.Decimal(max_digits=10, decimal_places=2)
    distributable_price = ormar.Decimal(max_digits=10, decimal_places=2)
    pv_cof: float = ormar.Float()
    is_active = ormar.Boolean(default=True)
    product_category: int = ormar.ForeignKey(ProductCategory)


class User(ormar.Model):
    class Meta(MetaData):
        pass

    id: int = ormar.Integer(primary_key=True, unique=True, index=True)
    username: str = ormar.String(max_length=255)
    phone_number: int = ormar.Integer(nullable=True, index=True)
    address: str = ormar.Text(nullable=True)
    discount: str = ormar.String(max_length=30, choices=list(UserDiscountEnum), default=UserDiscountEnum.ordinary.value)


class Distributable(ormar.Model):
    class Meta(MetaData):
        pass

    id: int = ormar.Integer(primary_key=True, autoincrement=True)
    code: str = ormar.String(max_length=255)


class Basket(ormar.Model):
    class Meta(MetaData):
        pass

    id: int = ormar.Integer(primary_key=True, autoincrement=True, unique=True, index=True)
    user: int = ormar.ForeignKey(User, ondelete='CASCADE')
    products = ormar.ManyToMany(Product)


class ProductQuantityInBasket(ormar.Model):
    class Meta(MetaData):
        pass

    id: int = ormar.Integer(primary_key=True, autoincrement=True, index=True)
    quantity: int = ormar.Integer(default=1)
    product: int = ormar.ForeignKey(Product, ondelete='CASCADE')
    basket: int = ormar.ForeignKey(Basket, ondelete='CASCADE')


class Order(ormar.Model):
    class Meta(MetaData):
        pass

    id: int = ormar.Integer(primary_key=True, autoincrement=True, index=True)
    full_name: str = ormar.String(max_length=200)
    address: str = ormar.Text()
    delivery: str = ormar.String(max_length=20)
    phone_number: str = ormar.String(max_length=30)
    from_user: int = ormar.ForeignKey(User, ondelete='CASCADE')
    comment: str = ormar.String(max_length=255, nullable=True)
    basket_history = ormar.JSON()

    

