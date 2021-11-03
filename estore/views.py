from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from .models import Users, Sellers, ProductImages, Products
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RegisterForm, SellerForm, ProductForm, ProductImagesForm
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_text, force_str, DjangoUnicodeDecodeError
from .utils import maketoken
def signin(request):
    page= 'signin'
    if request.user.is_authenticated:
        return redirect("profile")
    if request.method=='POST':
        email=request.POST['email']
        password=request.POST['password']
        try:
            user=Users.objects.get(email==email)
        except:
            messages.error(request, "wrong email")
        user=authenticate(request, email=email, password=password)
        # if not user.is_email.verified:
        #     messages.add_message(request, messages.ERROR, "email not verified")
        #     return redirect('register')

        if user is not None:
            login(request, user)
            return redirect('profile')
        else:
            messages.error(request, "email or password incorrect")
        
    return render(request, 'estore/signin.html')

def registerUser(request):
    if request.user.is_authenticated:
        return redirect("profile")
    page='register'
    form=RegisterForm(request.POST, request.FILES)
    if request.method=='POST':
        # form=RegisterForm(request.POST)
        if form.is_valid():
            u=form.save(commit=False)
            email=request.POST.get('email')
            u.email=u.email.lower()
            u.save()

            # currenturl=get_current_site(request)

            # subject='Verify your Email'
            # body=render_to_string('estore/activate.html',{
            #     'user':u,
            #     'domain':currenturl,
            #     'uid':urlsafe_base64_encode(force_bytes(u.pk)),
            #     'token': maketoken.make_token(u)
            # })

            # send_mail(subject,
            #         body,
            #         settings.EMAIL_HOST_USER,
            #         [email],
            #         fail_silently=False,
            #         )
            

            messages.success(request, "User account created")

            # login(request, u)
            # return redirect('profile')
        else:
            messages.error(request, "Error while registration")
    context={'page': page, 'form':form}
    return render(request, 'estore/signin.html', context)



def activate_user(request, uidb64, token):
    try:
        uid=force_text(urlsafe_base64_decode(uidb64))
        user=Users.objects.get(pk=uid)

    except Exception as e:
        user=None
    if user and maketoken.check_token(user, token):
        user.is_email_verified=True
        user.save()
        return redirect('signin')
    return redirect('register')

@login_required(login_url="signin")
def become_seller(request):
    id_user=request.user.user_id
    if request.user.is_seller==True:
        print('from here')
        return redirect('profile')
    form=SellerForm(request.POST, request.FILES)
    if request.method=='POST':
        if form.is_valid():
            sell=form.save(commit=False)
            sell.user_id=id_user
            sell.save()
            u=Users.objects.get(user_id=id_user)
            u.is_seller=True
            u.save()
            return redirect('register')
    context={'form':form}
    return render(request, 'estore/become_seller.html', context)

@login_required(login_url="signin")
def upload_product(request):
    id_user=request.user.user_id
    uobject=Users.objects.get(user_id=id_user)
    sobject=Sellers.objects.get(user_id=id_user)
    form=ProductForm(request.POST, request.FILES)
    form2=ProductImagesForm(request.POST, request.FILES)
    if uobject.is_seller==False or sobject.approval_status==False:
        return redirect('signin')
    if request.method=='POST':
        if form.is_valid() and form2.is_valid():
            pro=form.save(commit=False)
            pro.seller=sobject
            ima=form.save(commit=False)
            ima.product=Products.objects.get(seller=sobject)
            pro.save()
            ima.save()
            return redirect('Profile')

    context={'form':form, 'form2': form2}
    return render(request, 'estore/upload_product.html', context)
    


@login_required(login_url="signin")
def signout(request):
    logout(request)
    return redirect('signin')

@login_required(login_url="signin")
def shop(request):
    return render(request, 'estore/shop.html')

@login_required(login_url="signin")
def profile(request):
    return render(request, 'estore/profile.html')

@login_required(login_url="signin")
def checkout(request):
    return render(request, 'estore/checkout.html')

@login_required(login_url="signin")
def cart(request):
    return render(request, 'estore/cart.html')

@login_required(login_url="signin")
def epayment(request):
    return render(request, 'estore/epayment.html')

def base(request):
    return render(request, 'estore/base.html')

