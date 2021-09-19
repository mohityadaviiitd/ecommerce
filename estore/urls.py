from django.urls import path
from . import views
urlpatterns = [
    path('', views.shop, name="shop"),
    path('signin/', views.signin, name="signin"),
	path('checkout/', views.checkout, name="checkout"),
    path('profile/', views.profile, name="profile"),
	path('epayment/', views.epayment, name="epayment"),
    path('cart/', views.cart, name="cart"),
]