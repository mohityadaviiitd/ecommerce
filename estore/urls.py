from django.urls import path
from . import views
urlpatterns = [
    path('', views.shop, name="shop"),
    path('products/<str:productCategory>', views.products, name="products"),
    path('products/search/<str:searchQuery>', views.products, name="products"),
    path('products/filter/<str:filterQuery>', views.products, name="products"),
    path('products/sort/<str:sortBy>', views.products, name="products"),
    path('products/search/<str:searchQuery>/filter/<str:filterQuery>', views.products, name="products"),
    path('products/filter/<str:filterQuery>/sort/<str:sortBy>', views.products, name="products"),
    path('products/search/<str:searchQuery>/sort/<str:sortBy>', views.products, name="products"),
    path('products/search/<str:searchQuery>/filter/<str:filterQuery>/sort/<str:sortBy>', views.products, name="products"),
    path('products/', views.products, name="products"),
    path('itemDetails/id=<int:item_id>', views.items, name="items"),
    path('signin/', views.signin, name="signin"),
	path('checkout/', views.checkout, name="checkout"),
    path('profile/', views.profile, name="profile"),
	path('epayment/', views.epayment, name="epayment"),
    path('cart/', views.cart, name="cart"),
    path('wishlist/', views.wishlist, name="wishlist"),
]