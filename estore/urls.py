from django.urls import path
from . import views
urlpatterns = [
    path('', views.base, name="base"),
    path('signin/', views.signin, name="signin"),
    path('register/', views.registerUser, name="register"),
    path('signout/', views.signout, name="signout"),
	path('checkout/', views.checkout, name="checkout"),
    path('profile/', views.profile, name="profile"),
	path('epayment/', views.epayment, name="epayment"),
    path('cart/', views.cart, name="cart"),
    path('activate/<uidb64>/<token>', views.activate_user, name="activate"),
    path('become_seller/', views.become_seller, name="become_seller"),
    path('upload_product/', views.upload_product, name="upload_product"),
]