from ormar import NoMatch

from .models import ProductCategory, Product, Basket, User, Distributable, ProductQuantityInBasket, Order

categories_list = [
              'COLLAGEN PREMIUM', 'CRYO PRO', 'GOLDEN LINE', 'HEMPYBIO',
              'MIRRA BABY', 'MIRRA BIOTECHNOLOGY', 'MIRRA BODY', 'MIRRA CAVIAR', 'MIRRA DAILY', 'MIRRA DECOR',
              'MIRRA DENT', 'MIRRA HAIR', 'MIRRA INTENSIVE', 'MIRRA MINERAL', 'MIRRA INTIM', 'MIRRA PARFUM',
              'MIRRA PROPHYLACTIC', 'MIRRA PROTECT', 'MIRRA VINOTECHNOLOGY', 'PROFESSIONAL', 'БАЛЬЗАМЫ-ЦЕЛИТЕЛИ',
              'ДЛЯ МУЖЧИН', 'ФУНКЦИОНАЛЬНОЕ ПИТАНИЕ', 'АКСЕССУАРЫ', 'ПЕЧАТНАЯ ПРОДУКЦИЯ'
              ]


async def load_categories() -> None:
    load_first_model = await ProductCategory.objects.exists()
    if not load_first_model:
        for category in categories_list:
            category_name = category.capitalize()
            await ProductCategory.objects.create(name=category_name)


async def create_products(products_list):
    for product in products_list:
        await Product.objects.create(
            name=product.name,
            article=product.article,
            volume=product.volume,
            price=product.price,
            distributable_price=product.price_d,
            pv_cof=product.pv,
            product_category=19,
        )


async def get_categories() -> list:
    categories = await ProductCategory.objects.all()
    return categories


async def get_products(category_id: int) -> list:

    products = await Product.objects.select_related('product_category').filter(
        product_category=category_id).all()
    print('QUERY')
    return products


async def add_item_in_basket(item_id, user_id):
    a = list()

    a.append(user_id)
    prod = await Product.objects.get(id=item_id)
    print(prod)
    user_basket = await Basket.objects.filter(user=user_id).all()
    if user_basket:
        await user_basket[0].products.add(prod)
    else:
        a = await Basket.objects.create(user=user_id)
        await a.products.add(prod)


async def get_basket(user_id):
    try:
        basket = await Basket.objects.get(user=user_id)
        basket_user = await ProductQuantityInBasket.objects.select_related('product').filter(basket=basket).all()
        return basket_user
    except NoMatch:
        return []


async def create_user(user_id, username):
    user = await User.objects.filter(id=user_id).exists()

    if not user:
        await User.objects.create(id=user_id, username=username)


async def get_user(user_id):
    return await User.objects.get(id=user_id)


async def create_code(data):
    user_id = int(data.get('user'))
    await Distributable.objects.create(code=data.get('code'))
    await User.objects.filter(id=user_id).update(is_distributable=True)


async def get_product(product_id) -> Product:
    print('Запрос в бд для продукта')
    product = await Product.objects.get(id=product_id)
    return product


async def update_product_image(data):
    product = await Product.objects.get(article=data['article'])
    await product.update(image=data['image'])


async def get_or_create_basket(product_id, user_id):
    basket = await Basket.objects.select_related('products').filter(user=user_id).all()
    product = await Product.objects.get(id=product_id)
    if basket:
        # print(list(basket[0].products))
        if product in list(basket[0].products):
            product_quantity = await ProductQuantityInBasket.objects.get(basket=basket[0], product=product)
            count = product_quantity.quantity
            await product_quantity.update(quantity=count+1)
        else:
            await basket[0].products.add(product)
            await ProductQuantityInBasket.objects.create(basket=basket[0], product=product)
    else:
        bask = await Basket.objects.create(user=user_id)
        await bask.products.add(product)
        await ProductQuantityInBasket.objects.create(basket=bask, product=product)


async def basket_delete(user_id):
    await Basket.objects.delete(user=user_id)


async def create_order(data):
    return await Order.objects.create(**data)


async def delete_product(prod_quan_id, basket_id):
    # print(basket_id)
    prod_qun = await ProductQuantityInBasket.objects.get(id=prod_quan_id)
    product = await Product.objects.get(id=prod_qun.product.id)
    # print(product)
    basket = await Basket.objects.select_related('products').filter(id=basket_id).all()
    # print(basket)
    await basket[0].products.remove(product)
    # print(product)
    await ProductQuantityInBasket.objects.delete(id=prod_quan_id)


async def update_user_info(user_id, address, phone_number):
    user = await User.objects.get(id=user_id)
    await user.update(address=address, phone_number=phone_number)
