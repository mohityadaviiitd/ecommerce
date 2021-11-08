from django.db import models
from django import forms
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
import uuid, random
class usermanager(BaseUserManager):
    def create_user(self, user_name, email,phone, password=None):
        if not email:
           raise ValueError('Users must have an email address')
        if not phone:
           raise ValueError('Users must have an phone no')
        if not user_name:
           raise ValueError('Users must have an name')

        user = self.model(email=self.normalize_email(email))
        user.set_password(password)
        user.user_name=user_name
        user.phone=phone
        user.save(using=self._db)
        return user

    def create_superuser(self, user_name, phone, email, password=None):
        
        user = self.create_user(email=self.normalize_email(email),password=password, user_name=user_name, phone=phone)
        user.is_admin = True
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user

def get_product_photo(self, filename):
    return f'profile_images/{self.pk}/{"profile_photo.png"}'

class Cart(models.Model):
    cart = models.ForeignKey('Users', on_delete=models.CASCADE)
    product = models.ForeignKey('Products', on_delete=models.CASCADE)
    quantity = models.IntegerField()

    class Meta:
        managed = True
        db_table = 'cart'

class Wishlist(models.Model):
    wishlist = models.ForeignKey('Users', on_delete=models.CASCADE)
    product = models.ForeignKey('Products', on_delete=models.CASCADE)

    class Meta:
        managed = True
        db_table = 'wishlist'


class Checkouts(models.Model):
    checkout_id = models.CharField(primary_key=True, max_length=90)
    kart = models.ForeignKey('Users', models.DO_NOTHING)
    delivery_status = models.CharField(max_length=90)
    shipping_address_id = models.ForeignKey('UserAddress',on_delete=models.CASCADE)
    expected_date = models.DateTimeField()
    ordered_date = models.DateTimeField()
    products_ordered = models.CharField(max_length=9000)

    class Meta:
        managed = True
        db_table = 'checkouts'


class DelliverablePincodes(models.Model):
    seller = models.ForeignKey('Sellers', on_delete=models.CASCADE)
    pincode = models.IntegerField()
    no_of_days_to_deliver = models.IntegerField()

    class Meta:
        managed = True
        db_table = 'delliverable_pincodes'


def get_product_photo(self, filename):
    return f'product_images/{self.pk}/{"product_photo.png"}'

class ProductImages(models.Model):
    image_id =  models.UUIDField(default=uuid.uuid4, primary_key=True, unique=True, editable=False)
    product = models.ForeignKey('Products', on_delete=models.CASCADE)
    image = models.ImageField(null=True, blank=True,  upload_to=get_product_photo)

    class Meta:
        managed = True
        db_table = 'product_images'
    
    def get_product_photo(self):
        return str(self.pdf)[str(self.pdf).index(f'product_images/{self.pk}/'):]

# CATEGORY_CHOICES = (
#     ('M','Mobiles'),
#     ('L','Laptops'),
#     ('T','TV&Appliances'),
#     ('C','Camera&Accessories'),
# )
class Code(models.Model):
    number = models.CharField(max_length=5, blank=True)
    user=models.ForeignKey('Users', on_delete=models.CASCADE)
    def __str__(self):
        return str(self.number)
    def save(self, *args, **kwargs):
        ans=""
        for i in range(0,5):
            r=random.randint(0,9)
            ans=ans+str(r)
        self.number=ans
        super().save(*args, **kwargs)

class Products(models.Model):
    product_id = models.UUIDField(default=uuid.uuid4, primary_key=True, unique=True, editable=False)
    product_name = models.CharField(max_length=1000)
    details = models.CharField(max_length=4000, blank=True, null=True)
    category = models.CharField(max_length=90)
    price = models.FloatField()
    stock = models.IntegerField()
    seller = models.ForeignKey('Sellers', on_delete=models.CASCADE)
    status = models.CharField(default='active',max_length=90)
    date_created=models.DateTimeField(verbose_name="date created", auto_now_add=True)


    class Meta:
        managed = True
        db_table = 'products'



# class Returns(models.Model):
#     return_id = models.IntegerField(primary_key=True)
#     user = models.ForeignKey('Users', models.DO_NOTHING)
#     product = models.ForeignKey(Products, models.DO_NOTHING)

#     class Meta:
#         managed = True
#         db_table = 'returns'



def get_profile_photo(self, filename):
    return f'profile_images/{self.pk}/{"profile_photo.png"}'
def default_profile_photo():
    return "defaultlogo/pp.png"

def get_pdf(self, filename):
    return f'pdf/{self.pk}/{"proof.pdf"}'
def default_pdf():
    return "defaultlogo/proof.pdf"

class Sellers(models.Model):
    seller_id = models.UUIDField(default=uuid.uuid4, primary_key=True, unique=True, editable=False)
    user = models.ForeignKey('Users', on_delete=models.CASCADE)
    pdf = models.FileField(upload_to=get_pdf, default=default_pdf)
    approval_status = models.BooleanField(default=False)
    gst_number = models.CharField(unique=True, max_length=90)

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return True

    # def __str__(self):
    #     return self.seller_id

    def get_pdf(self):
        return str(self.pdf)[str(self.pdf).index(f'pdf/{self.pk}/'):]

    class Meta:
        managed = True
        db_table = 'sellers'


class UserAddress(models.Model):
    address_id = models.UUIDField(default=uuid.uuid4, primary_key=True,unique=True, editable=False)
    user = models.ForeignKey('Users', on_delete=models.CASCADE)
    house_no = models.CharField(max_length=90)
    address_line1 = models.CharField(max_length=400)
    address_line2 = models.CharField(max_length=400, blank=True, null=True)
    landmark = models.CharField(max_length=400, blank=True, null=True)
    city_village_name = models.CharField(max_length=90)
    state = models.CharField(max_length=90)
    pincode = models.IntegerField()

    # def __str__(self):
    #     return self.user

    class Meta:
        managed = True
        db_table = 'user_address'


class Users(AbstractBaseUser):
    user_id = models.UUIDField(default=uuid.uuid4, primary_key=True, unique=True, editable=False)
    user_name = models.CharField(max_length=90)
    # password = models.CharField( max_length=400)
    email = models.EmailField(verbose_name="email", unique=True, max_length=90)
    phone = models.CharField(unique=True, max_length=90)
    is_phone_verified = models.BooleanField(default=False)
    is_email_verified = models.BooleanField(default=False)
    cart_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    profile_photo = models.ImageField(null=True, blank=True,  upload_to=get_profile_photo, default=default_profile_photo)
    date_joined=models.DateTimeField(verbose_name="date joined", auto_now_add=True)
    last_login=models.DateTimeField(verbose_name="last login", auto_now=True)
    is_admin=models.BooleanField(default=False)
    is_active=models.BooleanField(default=True)
    is_staff=models.BooleanField(default=False)
    is_superuser=models.BooleanField(default=False)
    is_seller=models.BooleanField(default=False)
    wishlist_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    active = models.BooleanField(default=1)
    deleted = models.BooleanField(default=0)

    objects = usermanager()

    USERNAME_FIELD='email'
    REQUIRED_FIELDS=['user_name', 'phone']

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return True
    def __str__(self):
        return self.email

    def get_profile_photo(self):
        return str(self.profile_photo)[str(self.profile_photo).index(f'profile_images/{self.pk}/'):]
    

    class Meta:
        managed = True
        db_table = 'users'