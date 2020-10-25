from django.shortcuts import render
from django.http import JsonResponse
from django.core import serializers
from django.core.paginator import Paginator
import json

from .models import *

# Create your views here.


def store(request):

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(
            customer=customer, complete=False)
        cartItems = order.get_cart_item
    else:
        cartItems = 0

    products = Product.objects.all()
    context = {
        'products': products,
        'cartItems': cartItems,
    }
    return render(request, 'store/store.html', context)


def cart(request):

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(
            customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_item
    else:
        items = []
        order = {
            'get_cart_total': 0,
            'get_cart_item': 0,
        }
        cartItems = 0
    context = {
        'items': items,
        'order': order,
        'cartItems': cartItems,
    }
    return render(request, 'store/cart.html', context)


def checkout(request):

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(
            customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_item
    else:
        items = []
        order = {
            'get_cart_total': 0,
            'get_cart_item': 0,
        }
    context = {
        'items': items,
        'order': order,
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
