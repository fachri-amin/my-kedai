from django.urls import path

from . import views

app_name = 'store'

urlpatterns = [
    path('', views.store, name='store'),
    path('cart/', views.cart, name='cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('login/', views.loginView, name='login'),
    path('logout/', views.logoutView, name='logout'),
    path('process_order/', views.processOrder, name='process_order'),
    path('register/', views.registerView, name='register'),
    path('show_detail/', views.showDetail, name='show_detail'),
    path('update_item/', views.updateItem, name='update_item'),
]
