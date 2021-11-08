from django.contrib import admin

# Register your models here.
from .models import Users
from .models import UserAddress
from .models import Sellers
from .models import Products
from .models import ProductImages
from .models import DelliverablePincodes
from .models import Checkouts
from .models import Cart
from .models import Code

admin.site.register(Users)
admin.site.register(UserAddress)
admin.site.register(Sellers)
admin.site.register(Products)
admin.site.register(ProductImages)
admin.site.register(DelliverablePincodes)
admin.site.register(Checkouts)
admin.site.register(Cart)
admin.site.register(Code)

