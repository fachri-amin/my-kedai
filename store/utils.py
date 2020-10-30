import json
import midtransclient
from django.core.paginator import Paginator

from .models import *


def cookieCart(request):

    try:
        cart = json.loads(request.COOKIES['cart'])
    except:
        cart = {}

    items = []
    order = {
        'get_cart_total': 0,
        'get_cart_item': 0,
        'shipping': False,
    }
    cartItems = 0

    for i in cart:
        try:
            cartItems += cart[i]['quantity']

            product = Product.objects.get(id=i)
            total = product.price * cart[i]['quantity']

            order['get_cart_total'] += total
            order['get_cart_item'] += cart[i]['quantity']

            item = {
                'product': {
                    'id': product.id,
                    'name': product.name,
                    'price': product.price,
                    'imageURL': product.imageURL,
                },
                'quantity': cart[i]['quantity'],
                'get_total': total,
            }

            items.append(item)

            if not product.digital:
                order["shipping"] = True
        except:
            pass

    return{'items': items, 'order': order, 'cartItems': cartItems}


def cartData(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(
            customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_item
    else:
        cookie = cookieCart(request)
        order = cookie['order']
        items = cookie['items']
        cartItems = cookie['cartItems']

    return{'items': items, 'order': order, 'cartItems': cartItems}


def guestOrder(request, data):
    name = data['form']['name']
    email = data['form']['email']

    cookieData = cookieCart(request)
    items = cookieData['items']

    customer, created = Customer.objects.get_or_create(email=email)
    customer.name = name
    customer.save()

    order = Order.objects.create(customer=customer, complete=False)

    for item in items:
        product = Product.objects.get(id=item['product']['id'])

        orderItem = OrderItem.objects.create(
            product=product, order=order, quantity=item['quantity'])

    return customer, order


def makePayment(request, data):

    # Create Snap API instance
    snap = midtransclient.Snap(
        # Set to true if you want Production Environment (accept real transaction).
        is_production=False,
        server_key='SB-Mid-server-ZL-_sjMqs2h_UcvgH-z3WnLk'
    )
    # Build API parameter
    param = {
        "transaction_details": {
            "order_id": data['order_id'],
            "gross_amount": int(data['gross_amount'])
        }, "credit_card": {
            "secure": True
        }, "customer_details": {
            "name": data["name"],
            "email": data["email"],
        }
    }

    transaction = snap.create_transaction(param)

    return transaction['token']


def productPaginator(request, product_list, per_page, number_paginator):
    per_page = 9
    paginator = Paginator(product_list, per_page)
    number_paginator = 2
    total_page = paginator.num_pages

    if request.GET.get('page'):
        try:
            page = int(request.GET['page'])
        except:
            return Http404

        products = paginator.page(page)
        start = (page - number_paginator) if page > number_paginator else 1
        if page < (paginator.num_pages - number_paginator):
            end = (page+number_paginator)
        else:
            end = paginator.num_pages
    else:
        page = 1
        products = paginator.page(page)
        start = 1
        end = paginator.num_pages

    data = {
        'start': start,
        'end': end,
        'page': page,
        'total_page': total_page,
        'products': products,
    }

    return data
