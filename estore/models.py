from django.db import models

class Cart(models.Model):
    cart = models.ForeignKey('Users', models.DO_NOTHING)
    product = models.ForeignKey('Products', models.DO_NOTHING)
    quantity = models.IntegerField()

    class Meta:
        managed = True
        db_table = 'cart'

class Wishlist(models.Model):
    wishlist = models.ForeignKey('Users', models.DO_NOTHING)
    product = models.ForeignKey('Products', models.DO_NOTHING)

    class Meta:
        managed = True
        db_table = 'wishlist'


class Checkouts(models.Model):
    checkout_id = models.CharField(primary_key=True, max_length=90)
    kart = models.ForeignKey('Users', models.DO_NOTHING)
    delivery_status = models.CharField(max_length=90)
    shipping_address_id = models.CharField(max_length=90)
    expected_date = models.DateTimeField()
    ordered_date = models.DateTimeField()

    class Meta:
        managed = True
        db_table = 'checkouts'


class DelliverablePincodes(models.Model):
    seller = models.ForeignKey('Sellers', models.DO_NOTHING)
    pincode = models.IntegerField()
    no_of_days_to_deliver = models.IntegerField()

    class Meta:
        managed = True
        db_table = 'delliverable_pincodes'




class ProductImages(models.Model):
    image_id = models.IntegerField(primary_key=True)
    product = models.ForeignKey('Products', models.DO_NOTHING)
    image = models.ImageField(null=True, blank=True,  upload_to="productimages/")

    class Meta:
        managed = True
        db_table = 'product_images'


class Products(models.Model):
    product_id = models.IntegerField(primary_key=True)
    product_name = models.CharField(max_length=1000)
    details = models.CharField(max_length=4000, blank=True, null=True)
    category = models.CharField(max_length=90)
    price = models.FloatField()
    stock = models.IntegerField()
    seller = models.ForeignKey('Sellers', models.DO_NOTHING)
    status = models.CharField(max_length=90)

    class Meta:
        managed = True
        db_table = 'products'


class Returns(models.Model):
    return_id = models.IntegerField(primary_key=True)
    user = models.ForeignKey('Users', models.DO_NOTHING)
    product = models.ForeignKey(Products, models.DO_NOTHING)

    class Meta:
        managed = True
        db_table = 'returns'


class SellerAddresses(models.Model):
    address_id = models.CharField(primary_key=True, max_length=90)
    seller = models.ForeignKey('Sellers', models.DO_NOTHING)
    house_no = models.CharField(max_length=90)
    address_line1 = models.CharField(max_length=400)
    address_line2 = models.CharField(max_length=400, blank=True, null=True)
    ciyt_village_name = models.CharField(max_length=90)
    landmark = models.CharField(max_length=400, blank=True, null=True)
    state = models.CharField(max_length=90)
    pincode = models.IntegerField()

    class Meta:
        managed = True
        db_table = 'seller_addresses'


class Sellers(models.Model):
    seller_id = models.CharField(primary_key=True, max_length=90)
    seller_name = models.CharField(max_length=90)
    password = models.CharField(max_length=400)
    email = models.CharField(unique=True, max_length=90)
    phone = models.CharField(unique=True, max_length=90)
    pdf = models.FileField(upload_to='pdfs/', null=True, blank=True)
    approval_status = models.CharField(max_length=90)
    gst_number = models.CharField(unique=True, max_length=90)
    profile_photo = models.ImageField(null=True, blank=True,  upload_to="sellerimages/")

    class Meta:
        managed = True
        db_table = 'sellers'


class UserAddress(models.Model):
    address_id = models.CharField(primary_key=True, max_length=90)
    user = models.ForeignKey('Users', models.DO_NOTHING)
    house_no = models.CharField(max_length=90)
    address_line1 = models.CharField(max_length=400)
    address_line2 = models.CharField(max_length=400, blank=True, null=True)
    landmark = models.CharField(max_length=400, blank=True, null=True)
    city_village_name = models.CharField(max_length=90)
    state = models.CharField(max_length=90)
    pincode = models.IntegerField()

    class Meta:
        managed = True
        db_table = 'user_address'


class Users(models.Model):
    user_id = models.CharField(primary_key=True, max_length=90)
    user_name = models.CharField(max_length=90)
    password = models.CharField(max_length=400)
    email = models.CharField(unique=True, max_length=90)
    phone = models.CharField(unique=True, max_length=90)
    is_phone_verified = models.CharField(max_length=90)
    is_email_verified = models.CharField(max_length=90)
    cart_id = models.CharField(unique=True, max_length=90)
    wishlist_id = models.CharField(unique=True, max_length=90)
    profile_photo = models.ImageField(null=True, blank=True,  upload_to="userimages/")

    class Meta:
        managed = True
        db_table = 'users'
