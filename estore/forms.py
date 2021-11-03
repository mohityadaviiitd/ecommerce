from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from .models import Users
from .models import Sellers, Products, ProductImages


class RegisterForm(UserCreationForm):
    class Meta:
        model = Users
        fields= ['email', 'user_name', 'phone', 'profile_photo']

class SellerForm(ModelForm):
    class Meta:
        model = Sellers
        fields = ['pdf', 'gst_number']

class ProductForm(ModelForm):
    class Meta:
        model = Products
        fields = ['product_name', 'details', 'price', 'stock', 'category', 'status' ]

class ProductImagesForm(ModelForm):
    class Meta:
        model = ProductImages
        fields = ['image']