from app.models import Category, Product, User, Receipt, ReceiptDetails
from app import app, db
import hashlib
from flask_login import current_user
from sqlalchemy import func


def get_categories():
    return Category.query.all()


def get_products(kw, cate_id, page=None):
    products = Product.query

    if kw:
        products = products.filter(Product.name.contains(kw))

    if cate_id:
        products = products.filter(Product.category_id.__eq__(cate_id))

    if page:
        page = int(page)
        page_size = app.config['PAGE_SIZE']
        start = (page - 1) * page_size

        return products.slice(start, start + page_size)

    return products.all()


def count_product():
    return Product.query.count()


def get_user_by_id(user_id):
    return User.query.get(user_id)


def auth_user(username, password):
    password = str(hashlib.md5(password.encode('utf-8')).hexdigest())

    return User.query.filter(User.username.__eq__(username),
                             User.password.__eq__(password)).first()


def add_receipt(cart):
    if cart:
        r = Receipt(user=current_user)
        db.session.add(r)

        for c in cart.values():
            d = ReceiptDetails(quantity=c['quantity'], price=c['price'], receipt=r, product_id=c['id'])
            db.session.add(d)
        try:
            db.session.commit()
        except:
            return False
        else:
            return True


def count_products_bt_cate():
    return db.session.query(Category.id, Category.name, func.count(Product.id)) \
        .join(Product, Product.category_id.__eq__(Category.id), isouter=True) \
        .group_by(Category.id).all()


def stats_revenue(kw=None):
    query = db.session.query(Product.id, Product.name, func.sum(ReceiptDetails.quantity * ReceiptDetails.price)) \
        .join(ReceiptDetails, ReceiptDetails.product_id.__eq__(Product.id))

    if kw:
        query = query.filter(Product.name.contains(kw))

    return query.group_by(Product.id).all()


def stats_revenue_by_month(year=2024):
    return db.session.query(func.extract('month', Receipt.created_date),
                            func.sum(ReceiptDetails.quantity * ReceiptDetails.price)) \
        .join(ReceiptDetails, ReceiptDetails.receipt_id.__eq__(Receipt.id)) \
        .filter(func.extract('year', Receipt.created_date).__eq__(year)) \
        .group_by(func.extract('month', Receipt.created_date)).all()


if __name__ == '__main__':
    with app.app_context():
        print(count_products_bt_cate())
