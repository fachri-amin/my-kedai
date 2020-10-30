from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.core import serializers
from django.core.paginator import Paginator
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.http import Http404
from django.db.models import Q
import json
import datetime

from .models import *
from .utils import cookieCart, cartData, guestOrder, makePayment, productPaginator

# Create your views here.


def store(request):

    data = cartData(request)
    cartItems = data['cartItems']

    if request.GET.get('search'):
        search = request.GET.get('search')
        product_list = Product.objects.filter(name__icontains=search)
    else:
        product_list = Product.objects.all()
        search = False

    per_page = 9
    number_paginator = 2

    product_pagination = productPaginator(
        request, product_list, per_page, number_paginator)

    context = {
        'products': product_pagination['products'],
        'cartItems': cartItems,
        'start': product_pagination['start'],
        'end': product_pagination['end'],
        'page': product_pagination['page'],
        'show_page_num': range(product_pagination['start'], product_pagination['end']+1),
        'total_page': product_pagination['total_page'],
    }

    if search:
        context['search'] = search

    return render(request, 'store/store.html', context)


def cart(request):

    data = cartData(request)
    order = data['order']
    items = data['items']
    cartItems = data['cartItems']

    context = {
        'items': items,
        'order': order,
        'cartItems': cartItems,
    }
    return render(request, 'store/cart.html', context)


def checkout(request):

    data = cartData(request)
    order = data['order']
    items = data['items']
    cartItems = data['cartItems']

    context = {
        'items': items,
        'order': order,
        'cartItems': cartItems,
    }
    return render(request, 'store/checkout.html', context)


def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']

    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(
        customer=customer, complete=False)
    orderItem, created = OrderItem.objects.get_or_create(
        order=order, product=product)

    if action == 'add':
        orderItem.quantity += 1
    elif action == 'remove':
        orderItem.quantity -= 1

    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()

    try:
        quantity = orderItem.quantity
    except OrderItem.DoesNotExist:
        quantity = 0

    total_item = order.get_cart_item
    total_price = order.get_cart_total

    json_response = {
        'total_item': total_item,
        'quantity': quantity,
        'total': total_price,
        'item_price': orderItem.get_total
    }

    return JsonResponse(json_response, safe=False)


def processOrder(request):
    data = json.loads(request.body)
    transaction_id = datetime.datetime.now().timestamp()

    if request.method == 'POST':
        if request.user.is_authenticated:
            customer = request.user.customer
            order, created = Order.objects.get_or_create(
                customer=customer, complete=False)
        else:
            customer, order = guestOrder(request, data)

        total = float(data['form']['total'])
        order.transaction_id = transaction_id

        if total == order.get_cart_total:
            order.complete = True

        order.save()

        if order.shipping == True:
            ShippingAddress.objects.create(
                customer=customer,
                order=order,
                address=data['shipping']['address'],
                city=data['shipping']['city'],
                state=data['shipping']['state'],
                zipcode=data['shipping']['zipcode']
            )

        payment_data = {
            'order_id': order.transaction_id,
            'gross_amount': order.get_cart_total,
            'name': customer.name,
            'email': customer.email,
        }

        token = makePayment(request, payment_data)

    return JsonResponse({'token': token}, safe=False)


def loginView(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            return redirect('store:store')
        else:
            messages.error(request, 'Login invalid')
            return redirect('store:store')


def registerView(request):
    if request.method == 'POST':
        email = request.POST['email']
        username = request.POST['username']
        name = request.POST['name']
        password = request.POST['password']

        user, created = get_user_model().objects.get_or_create(username=username)
        if created:
            user.email = email
            user.set_password(user.password)
            user.save()

        customer, created = Customer.objects.get_or_create(email=email)
        customer.name = name
        customer.user = user
        customer.save()

        login(request, user)

        return redirect('store:store')


def logoutView(request):
    logout(request)

    return redirect(('store:store'))
