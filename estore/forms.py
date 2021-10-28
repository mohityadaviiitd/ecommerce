from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from .models import Users
from .models import Sellers


class RegisterForm(UserCreationForm):
    class Meta:
        model = Users
        fields= ['email', 'user_name', 'phone', 'profile_photo']