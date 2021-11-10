from django.forms import ModelForm,modelformset_factory
from django.core.exceptions import ValidationError
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.forms.fields import ImageField
from .models import Code, Users
from .models import Sellers, Products, ProductImages, DelliverablePincodes, UserAddress
from django.forms.widgets import FileInput


CATEGORY_CHOICES = (
    ('mobile','Mobiles'),
    ('laptop','Laptops'),
    ('tv','TV&Appliances'),
    ('Camera','Camera&Accessories'),
)
def only_int(value): 
    if value.isdigit()==False:
        raise ValidationError('Field should be a number')
def fsize(value):
    if value.size > 2000001.4336:
        raise ValidationError('Size should be less than 2MB')
def ext(value):
    if not value.name.endswith('.pdf'):
        raise ValidationError('Only pdf files are allowed')


class AddressForm(ModelForm):
    house_no=forms.CharField(label="House Number", max_length=90)
    address_line1=forms.CharField(label="Address Line 1", max_length=400)
    address_line2=forms.CharField(label="Address Line 2", max_length=400, required=False)
    landmark=forms.CharField(label="Landmark", max_length=400 ,required=False)
    city_village_name=forms.CharField(label="City/Village Name", max_length=90)
    state=forms.CharField(label="State", max_length=90)
    pincode=forms.IntegerField(label="Pincode", max_value=999999, min_value=100000)
    class Meta:
        model = UserAddress
        fields= ['house_no', 'address_line1', 'address_line2', 'landmark', 'city_village_name', 'state','pincode' ]
    def __init__(self, *args, **kwargs):
        super(AddressForm, self).__init__(*args, **kwargs)
        self.fields['house_no'].widget.attrs['placeholder'] = 'Your House Number*'
        self.fields['address_line1'].widget.attrs['placeholder'] = 'Address Line*'
        self.fields['address_line2'].widget.attrs['placeholder'] = 'Address Line'
        self.fields['landmark'].widget.attrs['placeholder'] = 'Landmark'
        self.fields['city_village_name'].widget.attrs['placeholder'] = 'Your City/Village Name*'
        self.fields['state'].widget.attrs['placeholder'] = 'Your State*'
        self.fields['pincode'].widget.attrs['placeholder'] = 'Your Pincode*'




class RegisterForm(UserCreationForm):
    email=forms.EmailField(label='Email', max_length=100)
    user_name=forms.CharField(label='Your Name',max_length=100)
    phone=forms.CharField(label='Phone Number',max_length=10,min_length=10, validators=[only_int])
    profile_photo=ImageField(label='Profile Photo', validators=[fsize])
    class Meta:
        model = Users
        fields= ['email', 'user_name', 'phone', 'profile_photo', ]
        help_texts = {
            'email': None,
            'user_name': None,
        }
    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
        self.fields['email'].widget.attrs['placeholder'] = 'Email*'
        self.fields['user_name'].widget.attrs['placeholder'] = 'Your Name*'
        self.fields['phone'].widget.attrs['placeholder'] = 'Your 10 digit Phone Number*'
        self.fields['profile_photo'].required = False


class ProfileForm(ModelForm):
    email=forms.EmailField(label='Email', max_length=100)
    user_name=forms.CharField(label='Your Name',max_length=100)
    phone=forms.CharField(label='Phone Number',max_length=10,min_length=10, validators=[only_int])
    profile_photo=ImageField(label='Profile Photo', validators=[fsize])
    class Meta:
        model = Users
        fields= ['email', 'user_name', 'phone', 'profile_photo', ]
        help_texts = {
            'email': None,
            'user_name': None,
        }
    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        self.fields['email'].widget.attrs['placeholder'] = 'Email*'
        self.fields['user_name'].widget.attrs['placeholder'] = 'Your Name*'
        self.fields['phone'].widget.attrs['placeholder'] = 'Your 10 digit Phone Number*'
        self.fields['profile_photo'].required = False

class PincodeForm(ModelForm):
    pincode=forms.IntegerField(label='Pincode',max_value=999999, min_value=100000)
    no_of_days_to_deliver=forms.IntegerField(label="Number of days for expected delivery to the pincode ", max_value=28)
    class Meta:
        model=DelliverablePincodes
        fields=['pincode','no_of_days_to_deliver']
    def __init__(self, *args, **kwargs):
        super(PincodeForm, self).__init__(*args, **kwargs)
        self.fields['pincode'].widget.attrs['placeholder'] = '6 digit Pincode*'
        self.fields['no_of_days_to_deliver'].widget.attrs['placeholder'] = 'max= 28 days*'

 
class SellerForm(ModelForm):
    pdf=forms.FileField(label='Document', validators=[fsize, ext])
    gst_number=forms.CharField(label='GST Number',min_length=1, max_length=15, validators=[only_int])
    class Meta:
        model = Sellers
        fields = ['pdf', 'gst_number']
    def __init__(self, *args, **kwargs):
        super(SellerForm, self).__init__(*args, **kwargs)
        self.fields['pdf'].widget.attrs['placeholder'] = 'Upload a pdf containing your ID and GST Form.(Max Size: 2MB)'
        self.fields['pdf'].widget.attrs['placeholder'] = 'Your GST Number'
    
class CodeForm(ModelForm):
    number=forms.CharField(label="OTP",validators=[only_int])
    class Meta:
        model=Code
        fields=['number',]

class ProductForm(ModelForm):
    product_name = forms.CharField(label='Product Name',max_length=200)
    details=forms.CharField(max_length=1000,label='Details and Specifications')
    price=forms.FloatField(max_value=10000000, min_value=1, label='Price')
    stock=forms.IntegerField(label='Stock')
    category=forms.CharField(label='Category',widget=forms.Select(choices=CATEGORY_CHOICES),)
    class Meta:
        model = Products
        fields = ['product_name', 'details', 'price', 'stock', 'category' ]
    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
        self.fields['product_name'].widget.attrs['placeholder'] = 'Brand Name, Model Name(200 characters max)'
        self.fields['details'].widget.attrs['placeholder'] = 'Eg. RAM=8GB, Processor=i5 10th Gen(1000 characters max)'
        self.fields['price'].widget.attrs['placeholder'] = 'Price of one quantity of the product(in Rs.)'
        self.fields['stock'].widget.attrs['placeholder'] = 'Quantity you have for sale'
        self.fields['category'].widget.attrs['placeholder'] = ''

class ProductImagesForm(ModelForm):
    image=ImageField(label='image', validators=[fsize])
    class Meta:
        model = ProductImages
        fields = ['image']

class BuyerGeneralProfileForm(ModelForm):

    class Meta:
        model = Users
        fields = ('user_name', 'phone')

class BuyerAddressProfileForm(ModelForm):

    class Meta:
        model = UserAddress
        fields = ('house_no', 'address_line1','address_line2','landmark','city_village_name','state','pincode')
