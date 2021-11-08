import uuid
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from .models import Users, Sellers, ProductImages, Products, Cart, UserAddress, Users, Wishlist, deactivatedProducts
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .forms import RegisterForm, SellerForm, ProductForm, ProductImagesForm, PincodeForm, AddressForm, ProfileForm
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_text, force_str, DjangoUnicodeDecodeError
from .utils import maketoken
from django.http.response import HttpResponse
from django.http import HttpResponseRedirect
import random
from django.urls import resolve, reverse
from .forms import BuyerGeneralProfileForm
from .forms import BuyerAddressProfileForm
from django.shortcuts import get_object_or_404
from django.http import FileResponse
import os
import re
from django.forms import modelformset_factory
from django.http import FileResponse, Http404, JsonResponse
import stripe
from django.db.models import Sum
stripe.api_key = settings.STRIPEKEY


@login_required(login_url="signin")
def activate_product(request):
    if(request.user.is_authenticated and request.user.is_admin == False):
        return HttpResponseRedirect('/signin')
    try:
        resUserData = deactivatedProducts.objects.all()
    except:
        return redirect('/')
    usersArr = []
    for data in resUserData:
        if(1== 1):
            userObj = {}
            userObj['id'] = data.product_id
            userObj['name'] = data.product_name
            userObj['price'] = data.price
            userObj['stock'] = data.stock
            userObj['dateCreated'] = data.date_created
            userObj['seller'] = data.seller.user.user_name
            usersArr.append(userObj)
    return render(request, 'estore/activate_product.html', {'users':usersArr})


@login_required(login_url="signin")
def deactivate_product(request):
    if(request.user.is_authenticated and request.user.is_admin == False):
        return HttpResponseRedirect('/signin')
    try:
        resUserData = Products.objects.all()
    except:
        return redirect('/')
    usersArr = []
    for data in resUserData:
        if(1== 1):
            userObj = {}
            userObj['id'] = data.product_id
            userObj['name'] = data.product_name
            userObj['price'] = data.price
            userObj['stock'] = data.stock
            userObj['dateCreated'] = data.date_created
            userObj['seller'] = data.seller.user.user_name
            usersArr.append(userObj)
    return render(request, 'estore/deactivate_product.html', {'users':usersArr})



@login_required(login_url="signin")
def index(request):
    if(request.user.is_admin==True):
        return redirect('/')
    
    try:
        cobj=Cart.objects.filter(cart=request.user)
    except:
            return redirect('/')
    if Cart.objects.filter(cart=request.user).count()==0:
        return redirect('/')
        
    return render(request, 'estore/index.html')

@login_required(login_url="signin")
def success_msg(request, args):
	amount = args
	return render(request, 'estore/success_msg.html', {'amount':amount})


@login_required(login_url="signin")
def charge(request):
    if(request.user.is_admin==True):
        return redirect('/')
    if request.method == 'POST':
        amount=0
        try:
            cobj=Cart.objects.filter(cart=request.user)
        except:
            return redirect('/')
        for ele in cobj:
            pro=ele.product
            price=pro.price
            amount=amount+price*ele.quantity
        amount=int(amount)
        if amount<=0:
            return redirect('/')
        customer= stripe.Customer.create( email=request.user.email, source=request.POST['stripeToken'] )
        charge= stripe.Charge.create( customer=customer, amount=amount*100, currency='inr', description="Payment for Products" )
    return redirect(reverse('success_msg', args=[amount]))

@login_required(login_url="signin")
def user_profile(request):
    if(request.user.is_authenticated and request.user.is_admin == True):
        return HttpResponseRedirect('/signin')
    if(request.user.is_authenticated and request.user.is_seller == False):
        return HttpResponseRedirect('/invalid') 
    if(1==1):
        initial_data={
            'user_name':request.user.user_name,
            'phone':request.user.phone,
            'email':request.user.email,
            'profile_photo':request.user.profile_photo,
        }
        em=request.user.email
        ph=request.user.email
        form1=ProfileForm(request.POST or None,request.FILES or None,initial=initial_data,instance=request.user)
        if form1.is_valid():
            sell=form1.save(commit=False)
            if(sell.phone!=ph):
                request.user.is_phone_verified=False
            if(sell.email!=em):
                request.user.is_email_verified=False
                sell.save()
                logout(request)
                return redirect('emailverify')
            
            sell.save()
            return HttpResponseRedirect(request.path_info)
    s=False
    if(request.user.is_seller==True):
        sobj=Sellers.objects.get(user=request.user)
        if(sobj.approval_status==True):
            s=True
    else:
        s=False
    user = {}
    user['firstName'] = request.user.user_name.split(" ")[0]
    user['isSeller'] = s
    user['isinventory']=0
    
    context={'form1':form1,'user':user}
    return render(request, 'estore/user_profile.html', context)
    # if s:
    #     return render(request, 'estore/user_profile.html', context)
    # else:
    #     return render(request, 'estore/buyer_profile.html', context)

@login_required(login_url="signin")
def deleteAddress(request):
    if(request.POST):
        try:
            addr = request.POST.get('address_id')
        except:
            return redirect('invalid')
        u = UserAddress.objects.get(address_id=addr)
        if(request.user!=u.user):
            print("here")
            return redirect('invalid')
        u.delete()
    return redirect('user_address')

@login_required(login_url="signin")
def inventory(request,productCategory = "",searchQuery="",filterQuery="",sortBy=""):
    if(request.user.is_seller==False):
        return redirect('/')
    filterArr= []
    finalArr = []
    pageTitle = ''
    try:
        s=Sellers.objects.get(user=request.user)
    except:
        return redirect('/')
    if(s.approval_status==False):
        return redirect('/')
    
    imgData = ProductImages.objects.all()
    so=False
    if(request.user.is_seller==True):
        sobj=Sellers.objects.get(user=request.user)
        if(sobj.approval_status==True):
            so=True
    else:
        so=False
    user = {}
    user['firstName'] = request.user.user_name.split(" ")[0]
    user['isSeller'] = so
    user['isinventory']=1
    if productCategory=="" and searchQuery == "" :
        pageTitle="Products"
        # print('1--------------')
        filterArr = Products.objects.filter(seller=s).order_by('-date_created')
    elif productCategory != "" and searchQuery == ""  :
         pageTitle = productCategory
        #  print('2--------------')
         filterArr = Products.objects.filter(seller=s, category=productCategory).order_by('-date_created')
    elif productCategory == "" and searchQuery != "":
        # print('3--------------')
        pageTitle = "Search Results"
        tempArr = Products.objects.filter(seller=s).order_by('-date_created')
        for product in tempArr:
            foundInName = re.search(searchQuery.lower(),product.product_name.lower())
            foundInDes = re.search(searchQuery.lower(),product.details.lower())
            foundInCategory = re.search(searchQuery.lower(),product.category.lower())
            #print('41--------------',foundInName,foundInCategory,foundInDes)
            if(foundInName != None or foundInDes != None or foundInCategory != None):
                filterArr.append(product)
    if filterQuery != "" : 
        arrQueries = filterQuery.split('&')
        inStock = arrQueries[2]
        minPrice = arrQueries[4]
        maxPrice = arrQueries[6]
        tempArr = filterArr
        for elem in tempArr:
            if int(elem.price) >= int(minPrice) and int(elem.price) <= int(maxPrice) :
                if inStock == 'true':
                    if elem.stock > 0:
                        finalArr.append(elem)
                else:
                    finalArr.append(elem)
    else:
        finalArr = filterArr        
    if sortBy == "A-Z" :
        finalArr.sort(key=lambda x: x.product_name, reverse=False)
    if sortBy == 'price' :
        finalArr.sort(key=lambda x: x.price, reverse=False)
    productArr = []
    for i in finalArr:
        product_dict = {}
        product_dict['id'] = i.product_id
        product_dict['name'] = i.product_name
        product_dict['price'] = int(i.price)
        product_dict['category'] = i.category
        product_dict['description'] = i.details
        product_dict['stock'] = i.stock
        product_dict['status'] = i.status
        productArr.append(product_dict)
    # print('-------arr product=----------------------',productArr)
    for i in productArr:
            for j in imgData:
                if (i['id'] == j.product_id):
                    i['image'] = j.image
                    # print("images ==============",j.image)
                    break
    return render(request, 'estore/inventory.html',{'products':productArr,'pageTitle':pageTitle,'user':user})


def products(request, productCategory="", searchQuery="", filterQuery="", sortBy=""):
    if(request.user.is_authenticated and request.user.is_admin == True):
        return HttpResponseRedirect('/admin-home')
    current_url = request.path_info
    # print('curnrul;-----',current_url)
    # print('-data------------------------',productCategory,   searchQuery,filterQuery)
    filterArr = []
    finalArr = []
    pageTitle = ''
    imgData = ProductImages.objects.all()
    if(request.POST):
        if request.user.is_authenticated:
            wishlist_id_form = request.POST.get('wishlist_id')
            product_id_form = request.POST.get('product_id')
            wishlistObj = Wishlist(wishlist_id=wishlist_id_form,
                                   product_id=product_id_form)
            wishlistObj.save()

            current_url = request.path_info

            return HttpResponseRedirect(current_url)
        else:
            return HttpResponseRedirect('/signin')
    else:

        






        user = {}
        wishlistData = []
        if request.user.is_authenticated:
            s=False
            if(request.user.is_seller==True):
                sobj=Sellers.objects.get(user=request.user)
                if(sobj.approval_status==True):
                    s=True
            else:
                s=False
            user['firstName'] = request.user.user_name.split(" ")[0]
            user['isSeller'] = s
            user['isinventory']=0
            # Note sending userid as cart id,userid is matched with cart_id in CART model
            user['cart_id'] = request.user.user_id
            # Note sending userid as wishlist id,userid is matched with wishlist_id in CART model
            user['wishlist_id'] = request.user.user_id
            wishlistData = Wishlist.objects.filter(
                wishlist_id=request.user.user_id)
        else:
            user['firstName'] = ''
            user['cart_id'] = ''
        if productCategory == "" and searchQuery == "":
            pageTitle = "Products"
            # print('1--------------')
            filterArr = Products.objects.filter(status='active')
        elif productCategory != "" and searchQuery == "":
            pageTitle = productCategory
            #  print('2--------------')
            filterArr = Products.objects.filter(category=productCategory,status='active')
        elif productCategory == "" and searchQuery != "":
            # print('3--------------')
            pageTitle = "Search Results"
            tempArr = Products.objects.filter(status='active')
            for product in tempArr:
                foundInName = re.search(
                    searchQuery.lower(), product.product_name.lower())
                foundInDes = re.search(
                    searchQuery.lower(), product.details.lower())
                foundInCategory = re.search(
                    searchQuery.lower(), product.category.lower())
                # print('41--------------',foundInName,foundInCategory,foundInDes)
                if(foundInName != None or foundInDes != None or foundInCategory != None):
                    filterArr.append(product)
        if filterQuery != "":
            arrQueries = filterQuery.split('&')
            inStock = arrQueries[2]
            minPrice = arrQueries[4]
            maxPrice = arrQueries[6]
            print('mix---------------', type(filterArr))
            tempArr = filterArr
            for elem in tempArr:
                if int(elem.price) >= int(minPrice) and int(elem.price) <= int(maxPrice):
                    if inStock == 'true':
                        if elem.stock > 0:
                            finalArr.append(elem)
                    else:
                        finalArr.append(elem)
        else:
            finalArr = filterArr
        if sortBy == "A-Z":
            finalArr.sort(key=lambda x: x.product_name, reverse=False)
            print('-sorted arr alpla----', finalArr)
        if sortBy == 'price':
            finalArr.sort(key=lambda x: x.price, reverse=False)
        productArr = []
        for i in finalArr:
            product_dict = {}
            product_dict['id'] = i.product_id
            product_dict['name'] = i.product_name
            product_dict['price'] = int(i.price)
            product_dict['category'] = i.category
            product_dict['fullDescription'] = i.details
            product_dict['description'] = i.details[0:50] + ' ...'
            product_dict['stock'] = i.stock
            product_dict['status'] = i.status
            product_dict['sellerId'] = i.seller_id
            product_dict['inWishlist'] = any(
                obj.product_id == i.product_id for obj in wishlistData)
            productArr.append(product_dict)
        # print('-------arr product=----------------------',productArr)

        for i in productArr:
            for j in imgData:
                if (i['id'] == j.product_id):
                    i['image'] = j.image
                    # print("images ==============",j.image)
                    break

        return render(request, 'estore/productList.html', {'products': productArr, 'pageTitle': pageTitle, 'user': user, 'currentUrl': current_url})


def items(request, item_id):
    if(request.user.is_authenticated and request.user.is_admin == True):
        return HttpResponseRedirect('/admin-home')
    current_url = request.path_info
    wishlistData = []
    if(request.POST):
        user = {}
        if request.user.is_authenticated:
            wishlist_id_form = request.POST.get('wishlist_id')
            product_id_form = request.POST.get('product_id')
            wishlistObj = Wishlist(wishlist_id=wishlist_id_form,
                                   product_id=product_id_form)
            wishlistObj.save()

            current_url = request.path_info

            return HttpResponseRedirect(current_url)
        else:
            return HttpResponseRedirect('/signin')
    else:
        user = {}
        if request.user.is_authenticated:
            user['firstName'] = request.user.user_name.split(" ")[0]
            # Note sending userid as cart id,userid is matched with cart_id in CART model
            user['cart_id'] = request.user.user_id
            user['wishlist_id'] = request.user.user_id
            s=False
            if(request.user.is_seller==True):
                sobj=Sellers.objects.get(user=request.user)
                if(sobj.approval_status==True):
                    s=True
            else:
                s=False
            user['isSeller'] = s
            user['isinventory']=0

            wishlistData = Wishlist.objects.filter(
                wishlist_id=request.user.user_id)
        else:
            user['firstName'] = ''
            user['cart_id'] = ''
            user['wishlist_id'] = ''

        print("id------", item_id)
        productDetails = Products.objects.get(product_id=item_id,status='active')
        imgRes = ProductImages.objects.all()
        images = []
        for img in imgRes:
            if(img.product_id == productDetails.product_id):
                images.append(img.image)
        setattr(productDetails, 'images', images)
        setattr(productDetails, 'price', int(productDetails.price))
        sellerData = Sellers.objects.get(seller_id=productDetails.seller_id)
        sellerDataFromUserDb = Users.objects.get(user_id=sellerData.user_id)
        setattr(productDetails, 'sellerName', sellerDataFromUserDb.user_name)
        setattr(productDetails, 'inWishlist', any(obj.product_id ==
                productDetails.product_id for obj in wishlistData))
        # product_dict['inWishlist'] = any(obj.product_id == i.product_id for obj in wishlistData)

        return render(request, 'estore/itemDetails.html', {'product': productDetails, 'user': user, 'currentUrl': current_url})


def signin(request):
    page = 'signin'
    if request.user.is_authenticated:
        return redirect("/", type="general")
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        try:
            user = Users.objects.get(email == email)
        except:
            a=0
        user=authenticate(request, email=email, password=password)
        

        if user is not None:
            if user.is_active==False or user.deleted==True or user.active==False:
                return redirect('invalid')
            if not user.is_email_verified:
                return redirect('invalid')
            login(request, user)
            if(user.is_admin==True):
                return redirect('buyerList')
            if(user.is_seller==True):
                sobj=Sellers.objects.get(user=user)
                if(sobj.approval_status==True):
                    return redirect('/')
            return redirect('/')
        else:
            messages.error(request, "email or password incorrect")
    return render(request, 'estore/signin.html', )

def invalid(request):
    return render(request, 'estore/invalid.html')
def success(request):
    return render(request, 'estore/success.html')


def addToCart(request):
    if(request.POST):
        if request.user.is_authenticated:
            cart_id_form = request.POST.get('cart_id')
            product_id_form = request.POST.get('product_id')
            print("cart" + cart_id_form + "prod_id" + product_id_form)
            try:
                cartObj = Cart.objects.get(
                    cart_id=cart_id_form, product_id=product_id_form)

                newQuantity = cartObj.quantity + 1
                setattr(cartObj, 'quantity', newQuantity)
                cartObj.save()
            except Cart.DoesNotExist:
                cart = Cart(cart_id=cart_id_form, quantity=1,
                            product_id=product_id_form)
                cart.save()
            return HttpResponse(status=204)
        else:
            return HttpResponseRedirect('/signin')




def registerUser(request):
    if request.user.is_authenticated:
        return redirect("user_profile")
    page='register'
    form=RegisterForm(request.POST or None, request.FILES or None)
    if request.method=='POST':
        # form=RegisterForm(request.POST)
        if form.is_valid():
            u = form.save(commit=False)
            email = request.POST.get('email')
            u.email = u.email.lower()
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
            return redirect('emailverify')
        else:
            messages.error(request, "Error while registration")
    context = {'page': page, 'form': form}
    return render(request, 'estore/signin.html', context)

def emailverify(request):
    return render(request, 'estore/emailverify.html')


@login_required(login_url="signin")
def set_address(request):
    form=AddressForm(request.POST or None, request.FILES or None)
    if request.method=='POST':
        if form.is_valid():
            sell=form.save(commit=False)
            sell.user=request.user
            sell.save()
            return redirect('set_address')
    s=False
    if(request.user.is_seller==True):
        sobj=Sellers.objects.get(user=request.user)
        if(sobj.approval_status==True):
            s=True
    else:
        s=False
    user = {}
    user['firstName'] = request.user.user_name.split(" ")[0]
    user['isSeller'] = s
    user['isinventory']=0
    context={'form':form,'user':user}

    return render(request, 'estore/set_address.html', context)

@login_required(login_url="signin")
def set_pincodes(request):
    if request.user.is_seller==False:
        return redirect('Profile')
    
    try:
        sobject=Sellers.objects.get(user=request.user)
    except :
        return redirect('invalid')

    if sobject.approval_status==False:
        return redirect('Profile')
        
    
    form=PincodeForm(request.POST or None, request.FILES or None)
    if request.method=='POST':
        if form.is_valid():
            sell=form.save(commit=False)
            sell.seller=sobject
            sell.save()
            return redirect('set_pincodes')
    context={'form':form}

    return render(request, 'estore/set_pincodes.html', context)


def activate_user(request, uidb64, token):
    try:
        uid=force_text(urlsafe_base64_decode(uidb64))
        user=Users.objects.get(pk=uid)
        

    except Exception as e:
        user = None
    if user and maketoken.check_token(user, token):
        user.is_email_verified = True
        user.save()
        return redirect('signin')
    return redirect('register')

@login_required(login_url="signin")
def alreadyseller(request):
    s=False
    if(request.user.is_seller==True):
        sobj=Sellers.objects.get(user=request.user)
        if(sobj.approval_status==True):
            s=True
    else:
        s=False
    user = {}
    user['firstName'] = request.user.user_name.split(" ")[0]
    user['isSeller'] = s
    user['isinventory']=0
    return render(request, 'estore/alreadyseller.html', {'user':user})

@login_required(login_url="signin")
def become_seller(request):
    id_user=request.user.user_id
    if request.user.is_seller==True:
        return redirect('alreadyseller')
    form=SellerForm(request.POST or None, request.FILES or None)
    if request.method=='POST':
        if form.is_valid():
            sell = form.save(commit=False)
            sell.user_id = id_user
            sell.save()
            u = Users.objects.get(user_id=id_user)
            u.is_seller = True
            u.save()
            return redirect('/')
    s=False
    if(request.user.is_seller==True):
        sobj=Sellers.objects.get(user=request.user)
        if(sobj.approval_status==True):
            s=True
    else:
        s=False
    user = {}
    user['firstName'] = request.user.user_name.split(" ")[0]
    user['isSeller'] = s
    user['isinventory']=0
    context = {'form': form,'user':user}
    return render(request, 'estore/become_seller.html', context)


@login_required(login_url="signin")
def upload_product(request):
    if(request.user.is_seller==False):
        return redirect("/")
    ImageFormSet = modelformset_factory(ProductImages,form=ProductImagesForm, extra=4)
    id_user=request.user.user_id
    uobject=Users.objects.get(user_id=id_user)
    sobject=Sellers.objects.get(user_id=id_user)
    form1=ProductForm(request.POST, request.FILES)
    formset = ImageFormSet(request.POST, request.FILES,queryset=ProductImages.objects.none())
    if uobject.is_seller==False or sobject.approval_status==False:
        return redirect('signin')
    if request.method == 'POST':
        if form1.is_valid() and formset.is_valid():
            proobj=Products()
            proobj.product_name=form1.cleaned_data.get('product_name')
            proobj.details=form1.cleaned_data.get('details')
            proobj.price=form1.cleaned_data.get('price')
            proobj.stock=form1.cleaned_data.get('stock')
            proobj.category=form1.cleaned_data.get('category')
            proobj.seller=sobject
            proobj.save()
            # pro=form1.save(commit=False)
            # pro.seller=sobject
            # pro.save()
            for form in formset.cleaned_data:
                if form:
                    image = form['image']
                    photo = ProductImages(product=proobj, image=image)
                    photo.save()
            return redirect('inventory')
    # id_user=request.user.user_id
    # uobject=Users.objects.get(user_id=id_user)
    # sobject=Sellers.objects.get(user_id=id_user)
    # form=ProductForm(request.POST, request.FILES)
    # if uobject.is_seller==False or sobject.approval_status==False:
    #     return redirect('signin')
    # if request.method=='POST':
    #     if form.is_valid():
    #         pro=form.save(commit=False)
    #         pro.seller=sobject
    #         pro.save()
    #         return redirect('/upload_product_images/%s/'%pro.product_id)
    else:
        form1 = ProductForm()
        formset = ImageFormSet(queryset=ProductImages.objects.none())
    s=False
    if(request.user.is_seller==True):
        sobj=Sellers.objects.get(user=request.user)
        if(sobj.approval_status==True):
            s=True
    else:
        s=False
    user = {}
    user['firstName'] = request.user.user_name.split(" ")[0]
    user['isSeller'] = s
    user['isinventory']=0
    context={'form1':form1, 'formset':formset,'user':user}
    return render(request, 'estore/upload_product.html', context)
    
@login_required(login_url="signin")
def delete_product(request, proid):
    try:
        s=Sellers.objects.get(user=request.user)
    except :
        return redirect('invalid')

    try:
        prod=Products.objects.get(product_id=proid)
    except :
        return redirect('invalid')
    ss=prod.seller
    if(s==ss and s!=None and prod!=None):
        ProductImages.objects.filter(product=prod).delete()
        instance = Products.objects.get(product_id=proid)
        instance.delete()
        return redirect('inventory')
    return render(request, 'estore/invalid.html')

@login_required(login_url="signin")
def user_address(request):
    resAddData = UserAddress.objects.filter(user=request.user)
    usersArr = []
    for data in resAddData:
        userObj = {}
        userObj['id'] = data.address_id
        userObj["address_line"] = str(data.house_no) + ", " + str(data.address_line1) +", " + str(data.address_line2) + ", " + str(data.landmark) + ", " + str(data.pincode)
        userObj["city"] = data.city_village_name
        userObj["state"] = data.state 
        usersArr.append(userObj)
    s=False
    if(request.user.is_seller==True):
        sobj=Sellers.objects.get(user=request.user)
        if(sobj.approval_status==True):
            s=True
    else:
        s=False
    user = {}
    user['firstName'] = request.user.user_name.split(" ")[0]
    user['isSeller'] = s
    user['isinventory']=0
    context={'users':usersArr,'user':user}
    return render(request, 'estore/user_address.html', context)


@login_required(login_url="signin")
def edit_product(request, proid):
    try:
        s=Sellers.objects.get(user=request.user)
    except :
        return redirect('invalid')
    try:
        prod=Products.objects.get(product_id=proid)
    except :
        return redirect('invalid')
    
    ss=prod.seller
    
    if(s==ss):
        initial_data={
            'product_name':prod.product_name,
            'details':prod.details,
            'price':prod.price,
            'stock':prod.stock,
            'category':prod.category,
        }
        imagearr=[]
        allimages=ProductImages.objects.filter(product=prod)
        for singleimage in allimages:
            d={
                'image':singleimage.image
            }
            imagearr.append(d)
        instance = get_object_or_404(Products, product_id=proid)
        form1=ProductForm(request.POST or None,request.FILES or None,initial=initial_data, instance=instance)
        ImageFormSet = modelformset_factory(ProductImages,form=ProductImagesForm, extra=4)
        formset = ImageFormSet(request.POST or None, request.FILES or None, initial=imagearr,queryset=ProductImages.objects.none())
        
        if form1.is_valid() and formset.is_valid():
            form1.save()
            images = formset.save(commit=False)
            # for obj in formset.deleted_objects:
            #     obj.delete()
            for image in images:
                image.product = prod
                image.save()
            return HttpResponseRedirect(request.path_info)
    s=False
    if(request.user.is_seller==True):
        sobj=Sellers.objects.get(user=request.user)
        if(sobj.approval_status==True):
            s=True
    else:
        s=False
    user = {}
    user['firstName'] = request.user.user_name.split(" ")[0]
    user['isSeller'] = s
    user['isinventory']=0

    context={'form1':form1,
            'formset':formset,
            'proid':proid,
            'product_name':prod.product_name,
            'details':prod.details,
            'price':prod.price,
            'stock':prod.stock,
            'category':prod.category,
            'user':user}
    return render(request, 'estore/edit_product.html', context)







@login_required(login_url="signin")
def signout(request):
    logout(request)
    return redirect('signin')

# @login_required(login_url="signin")


def shop(request):
    if(request.user.is_authenticated and request.user.is_admin == True):
        return HttpResponseRedirect('/admin-home')
    if(request.POST):
        if request.user.is_authenticated:
            wishlist_id_form = request.POST.get('wishlist_id')
            product_id_form = request.POST.get('product_id')
            print('-wish---------------', wishlist_id_form, product_id_form)
            wishlistObj = Wishlist(wishlist_id=wishlist_id_form,
                                   product_id=product_id_form)
            wishlistObj.save()
            return HttpResponseRedirect('/')
        else:
            return HttpResponseRedirect('/signin')
    else:
        user = {}
        wishlistData = []
        if request.user.is_authenticated:
            user['firstName'] = request.user.user_name.split(" ")[0]
            # Note sending userid as cart id,userid is matched with cart_id in CART model
            user['cart_id'] = request.user.user_id
            # Note sending userid as wishlist id,userid is matched with wishlist_id in CART model
            user['wishlist_id'] = request.user.user_id
            s=False
            if(request.user.is_seller==True):
                sobj=Sellers.objects.get(user=request.user)
                if(sobj.approval_status==True):
                    s=True
            else:
                s=False
            user['isSeller'] = s
            user['isinventory']=0
            wishlistData = Wishlist.objects.filter(
                wishlist_id=request.user.user_id)
        else:
            user['firstName'] = ''
            user['cart_id'] = ''
        resData = Products.objects.filter(status='active')
        # print('prod data--------',wishlistData[0].product_id)
        imgData = ProductImages.objects.all()
        productArr = []
        for i in resData:
            print('-------------pid-----', i, i.product_id)
            product_dict = {}
            product_dict['id'] = i.product_id
            product_dict['name'] = i.product_name
            product_dict['price'] = int(i.price)
            product_dict['category'] = i.category
            product_dict['fullDescription'] = i.details
            product_dict['description'] = i.details[0:50] + ' ...'
            product_dict['stock'] = i.stock
            product_dict['status'] = i.status
            product_dict['inWishlist'] = any(
                obj.product_id == i.product_id for obj in wishlistData)
            productArr.append(product_dict)
        print("data =========", productArr)
        for i in productArr:
            for j in imgData:
                if (i['id'] == j.product_id):
                    i['image'] = j.image
                    break
        dest = productArr[:]
        random.shuffle(dest)
        productsFeatured = dest[0:6]
        # print(productsFeatured)

        return render(request, 'estore/shop.html', {'product_array': productsFeatured, 'user': user})


def clearMessages(request):
    storage = messages.get_messages(request)
    for _ in storage:
        pass
    print(storage._loaded_messages[0])
    for _ in list(storage._loaded_messages):
        del storage._loaded_messages[0]


@login_required(login_url="signin")
def profile(request, type="general"):
    if(request.user.is_authenticated and request.user.is_admin == True):
        return HttpResponseRedirect('/admin-home')
    if(request.user.is_authenticated and request.user.is_seller == True):
        return HttpResponseRedirect('/invalid') 
    userId = request.user.user_id
    user = {}
    user['firstName'] = request.user.user_name.split(" ")[0]
    user['isSeller'] = request.user.is_seller
    current_user_profile_pic = Users.objects.filter(user_id=userId)[
        0].profile_photo.url
    current_user_email_id = Users.objects.filter(user_id=userId)[0].email
    if(type == "general"):
        user_profile = get_object_or_404(Users, user_id=userId)
        if (request.POST):
            form = BuyerGeneralProfileForm(request.POST, instance=user_profile)
            if form.is_valid():
                user_profile = form.save(commit=False)
                print(form)
                user_profile.user_name = form['user_name'].value()
                not_dig = False
                i_s = 0
                print(list(form['phone'].value()))
                for i in list(form['phone'].value()):
                    if(i.isdigit() or i == '+' and i_s < 2):
                        if(i == '+'):
                            i_s += 1
                        continue
                    else:
                        not_dig = True
                        break
                if(not_dig == True):

                    try:
                        clearMessages(request)
                    except:
                        pass

                    messages.error(
                        request, "Phone number should only contain digits or +")
                    # return HttpResponseRedirect('/profile/general')
                    # return redirect('profile',type = 'general')
                else:
                    if(len(form['phone'].value()) >= 10 and len(form['phone'].value()) <= 12):
                        user_profile.phone = form['phone'].value()
                    else:
                        try:
                            clearMessages(request)
                        except:
                            pass
                        messages.error(
                            request, "Does not look like a real number!")
                        # return HttpResponseRedirect('')
                        return redirect('profile', type='general')

                user_profile.save()
                # return HttpResponseRedirect('')
                # return redirect('profile',type = 'general')
        else:
            form = BuyerGeneralProfileForm(instance=user_profile)

        return render(request, 'estore/profile.html', {
            'profile': form, 'address_profile': False,
            'pic': current_user_profile_pic,
            'email': current_user_email_id,
            'user': user})
    elif(type == "address"):
        try:
            address_profile = get_object_or_404(UserAddress, user_id=userId)
        except:
            data = UserAddress.objects.filter(user_id=userId)
            if(len(data) == 0):
                address_profile_instance = UserAddress.objects.create(user_id=userId, address_line1='',
                                                                      state='', pincode=0,
                                                                      city_village_name='', house_no='')

                address_profile_instance.save()
                address_profile_instance.refresh_from_db()
                address_profile = get_object_or_404(
                    UserAddress, user_id=userId)

        if (request.POST):
            form = BuyerAddressProfileForm(
                request.POST, instance=address_profile)
            if form.is_valid():
                address_profile = form.save(commit=False)
                address_profile.house_no = form['house_no'].value()
                address_profile.address_line1 = form['address_line1'].value()
                address_profile.address_line2 = form['address_line1'].value()
                address_profile.landmark = form['landmark'].value()
                address_profile.city_village_name = form['city_village_name'].value(
                )
                address_profile.state = form['state'].value()

                if(len(form['pincode'].value()) == 6 and form['pincode'].value().isdigit()):
                    address_profile.pincode = form['pincode'].value()
                else:
                    try:
                        clearMessages(request)
                    except:
                        pass
                    messages.error(request, "Enter a 6 digit pin-code")
                    # return HttpResponseRedirect('')
                    # return HttpResponseRedirect('%s' % '')

                address_profile.save()
                # return HttpResponseRedirect('%s' % '')
        else:
            form = BuyerAddressProfileForm(instance=address_profile)
        return render(request, 'estore/profile.html', {'general_profile': False, 'profile': form,
                                                       'pic': current_user_profile_pic, 'email': current_user_email_id, 'user': user})


@login_required(login_url="signin")
def checkout(request):
    return render(request, 'estore/checkout.html')




@login_required(login_url="signin")
def cart(request):
    if(request.user.is_authenticated and request.user.is_admin == True):
        return HttpResponseRedirect('/admin-home')
    if(request.POST):
        cart_id_form = request.POST.get('cart_id')
        product_id_form = request.POST.get('product_id')

        Cart.objects.filter(cart_id=cart_id_form,
                            product_id=product_id_form).delete()
        return HttpResponseRedirect('/cart')
    else:
        s=False
        if(request.user.is_seller==True):
            sobj=Sellers.objects.get(user=request.user)
            if(sobj.approval_status==True):
                s=True
        else:
            s=False
        user = {}
        user['firstName'] = request.user.user_name.split(" ")[0]
        user['isSeller'] = s
        user['isinventory']=0
        cartid = request.user.user_id
        data = Cart.objects.filter(cart_id=cartid.hex)
        product_id_list = []
        productArr= []
        for cart in data:
            
            productToAdd = Products.objects.get(product_id = cart.product_id)
            productArr.append(productToAdd)
        # for i in range(len(data)):
        #     product_id_list.append(data[i].product_id)
        # data2 = Products.objects.filter(product_id__in=product_id_list)
        data2 = []
        for product in productArr:
            if(product.status == 'active'):
                data2.append(product)
                product_id_list.append(product.product_id)
        
        product_list = []
        seller_id_list = []
        for i in data:
            product_dict = {}
            for j in data2:
                if(i.product_id.int == j.product_id.int):
                    product_dict['product_id'] = i.product_id
                    product_dict['product_name'] = j.product_name
                    product_dict['price'] = j.price
                    product_dict['quantity'] = i.quantity
                    if(j.stock > i.quantity):
                        product_dict['stock_status'] = i.quantity
                    elif(j.stock > 0):
                        product_dict['stock_status'] = j.stock
                    elif(j.stock == 0):
                        product_dict['stock_status'] = 0
                    seller_id_list.append(j.seller_id)
                    product_dict['seller_id'] = j.seller_id
                    product_dict['total_price'] = product_dict['stock_status']*j.price
                    product_list.append(product_dict)
        productImagesData = ProductImages.objects.filter(product_id__in=product_id_list)
        for i in product_list:
            for j in productImagesData:
                if(i['product_id'].int == j.product_id.int):
                    i['product_image'] = j.image.url
                    break
        data2 = Sellers.objects.filter(seller_id__in=seller_id_list)
        userIds = []
        for i in product_list:
            for j in data2:
                if(i['seller_id'] == j.seller_id):
                    userIds.append(j.user_id)
        data3 = Users.objects.filter(user_id__in=userIds)
        for i in product_list:
            for j in data2:
                for k in data3:
                    if j.user_id == k.user_id and i['seller_id'] == j.seller_id:
                        i['product_seller_name'] = k.user_name
        
        cart_total = 0
        for i in product_list:
            cart_total += i['total_price']
        return render(request, 'estore/cart.html', {'product_list': product_list, 'cart_total': cart_total, 'cart': cartid, 'user': user})


@login_required(login_url="signin")
def epayment(request):
    return render(request, 'estore/epayment.html')


def base(request):
    return render(request, 'estore/base.html')


@login_required(login_url="signin")
def admin(request):
    return render(request, 'estore/adminBase.html')

@login_required(login_url="signin")
def adminBuyer(request):
    if(request.user.is_authenticated and request.user.is_admin == False):
        return HttpResponseRedirect('/signin')
    resUserData = Users.objects.all()
    resAddData = UserAddress.objects.all()
    usersArr = []
    for data in resUserData:
        if(data.deleted != 1 and data.is_admin != 1 and data.is_seller!=1 ):
            
            userObj = {}
            userObj['id'] = data.user_id
            userObj['name'] = data.user_name
            userObj['email'] = data.email
            userObj['phone'] = data.phone
            userObj['isPhoneVerified'] = data.is_phone_verified
            userObj['isEmailVerified'] = data.is_email_verified
            userObj['cartId'] = data.cart_id
            userObj['wishlistId'] = data.wishlist_id
            userObj['active'] = data.active  # need to be updated
            for address in resAddData:
                if (address.user_id == data.user_id):
                    userObj["address_line"] = str(address.house_no) + ", " + str(address.address_line1) + ", " + str(
                        address.address_line2) + ", " + str(address.landmark) + ", " + str(address.pincode)
                    userObj["city"] = address.city_village_name
                    userObj["state"] = address.state
            usersArr.append(userObj)
    # print('----user data----', usersArr)
    return render(request, 'estore/adminBuyer.html', {'users': usersArr})


@login_required(login_url="signin")
def adminSeller(request):
    if(request.user.is_authenticated and request.user.is_admin == False):
        return HttpResponseRedirect('/signin')
    resUserData = Users.objects.all()
    resAddData = UserAddress.objects.all()
    resSellerData = Sellers.objects.all()
    print(resSellerData)
    usersArr = []
    for data in resUserData:
        if (data.deleted != 1 and data.is_seller == 1 and data.is_admin == 0):
            userObj = {}
            userObj['id'] = data.user_id
            userObj['name'] = data.user_name
            userObj['email'] = data.email
            userObj['phone'] = data.phone
            userObj['isPhoneVerified'] = data.is_phone_verified
            userObj['isEmailVerified'] = data.is_email_verified
            userObj['active'] = data.active  # need to be updated
            for address in resAddData:
                if (address.user_id == data.user_id):
                    userObj["address_line"] = str(address.house_no) + ", " + str(address.address_line1) + ", " + str(
                        address.address_line2) + ", " + str(address.landmark) + ", " + str(address.pincode)
                    userObj["city"] = address.city_village_name
                    userObj["state"] = address.state

            for each in resSellerData:
                if (each.user_id == data.user_id):
                    userObj['seller_approval_status'] = each.approval_status
                    try:
                        userObj['seller_pdf'] = each.pdf.url
                    except:
                        userObj['seller_pdf'] = False
            usersArr.append(userObj)
    # print('----user data----', usersArr)
    return render(request, 'estore/adminSeller.html', {'users': usersArr})


@login_required(login_url="signin")
def wishlist(request):
    if(request.user.is_authenticated and request.user.is_admin == True):
        return HttpResponseRedirect('/admin-home')
    if (request.POST):
        wishlist_id_form = request.POST.get('wishlist_id')
        product_id_form = request.POST.get('product_id')
        Wishlist.objects.filter(
            wishlist_id=wishlist_id_form, product_id=product_id_form).delete()
        return HttpResponseRedirect('/wishlist')
    else:
        user = {}
        s=False
        if(request.user.is_seller==True):
            sobj=Sellers.objects.get(user=request.user)
            if(sobj.approval_status==True):
                s=True
        else:
            s=False
        user['firstName'] = request.user.user_name.split(" ")[0]
        user['isSeller'] = s
        user['isinventory']=0
        wishlistid = request.user.user_id
        data = Wishlist.objects.filter(wishlist_id=wishlistid)
        product_id_list = []
        productArr= []
        for cart in data:
            # print('12=====================',cart.product_id,cart,len(data))
            productToAdd = Products.objects.get(product_id = cart.product_id)
            productArr.append(productToAdd)
        data2 = []
        for product in productArr:
            if(product.status == 'active'):
                data2.append(product)
                product_id_list.append(product.product_id)
        # print("data2=========================",data2)
        # for i in range(len(data)):
        #     product_id_list.append(data[i].product_id)
        # data2 = Products.objects.filter(product_id__in=product_id_list)
        product_list = []
        seller_id_list = []
        for i in data:
            product_dict = {}
            for j in data2:
                if (i.product_id == j.product_id):
                    product_dict['product_id'] = i.product_id
                    product_dict['product_name'] = j.product_name
                    product_dict['price'] = j.price
                    if (j.stock > 0):
                        product_dict['stock_status'] = True
                    else:
                        product_dict['stock_status'] = False
                    seller_id_list.append(j.seller_id)
                    product_dict['seller_id'] = j.seller_id
                    product_list.append(product_dict)

        data2 = ProductImages.objects.filter(product_id__in=product_id_list)
        for i in product_list:
            for j in data2:
                if (i['product_id'] == j.product_id):
                    i['product_image'] = j.image.url
                    break
        # 33
        data2 = Sellers.objects.filter(seller_id__in=seller_id_list)
        userIds = []
        for i in product_list:
            for j in data2:
                if(i['seller_id'] == j.seller_id):
                    userIds.append(j.user_id)
        data3 = Users.objects.filter(user_id__in=userIds)
        for i in product_list:
            for j in data2:
                for k in data3:
                    if j.user_id == k.user_id and i['seller_id'] == j.seller_id:
                        i['product_seller_name'] = k.user_name

        return render(request, 'estore/wishlist.html',
                      {'product_list': product_list, 'wishlist': wishlistid, 'user': user})


@login_required(login_url="signin")
def makeUserActive(request):
    # Apply check for authenticated admin
    if(request.user.is_authenticated and request.user.is_admin == False):
        return HttpResponseRedirect('/signin')
    if(request.POST):
        userIdToActive = request.POST.get('user_id')
        userData = Users.objects.get(user_id=userIdToActive)
        setattr(userData, 'is_active', 1)
        setattr(userData, 'active', 1)
        userData.save()
    return HttpResponseRedirect('/admin-home/buyer-list')

@login_required(login_url="signin")
def makeUserInactive(request):
    # Apply check for authenticated admin
    if(request.user.is_authenticated and request.user.is_admin == False):
        return HttpResponseRedirect('/signin')
    if(request.POST):
        userIdToInactive = request.POST.get('user_id')
        userData = Users.objects.get(user_id=userIdToInactive)
        setattr(userData, 'is_active', 0)
        setattr(userData, 'active', 0)
        userData.save()
    return HttpResponseRedirect('/admin-home/buyer-list')

@login_required(login_url="signin")
def makeSellerUserActive(request):
    # Apply check for authenticated admin
    if(request.user.is_authenticated and request.user.is_admin == False):
        return HttpResponseRedirect('/signin')
    if (request.POST):
        userIdToActive = request.POST.get('user_id')
        userData = Users.objects.get(user_id=userIdToActive)
        setattr(userData, 'is_active', 1)
        setattr(userData, 'active', 1)
        userData.save()
    return HttpResponseRedirect('/admin-home/seller-list')

@login_required(login_url="signin")
def makeSellerUserInactive(request):
    # Apply check for authenticated admin
    if(request.user.is_authenticated and request.user.is_admin == False):
        return HttpResponseRedirect('/signin')
    if (request.POST):
        userIdToInactive = request.POST.get('user_id')
        userData = Users.objects.get(user_id=userIdToInactive)
        setattr(userData, 'is_active', 0)
        setattr(userData, 'active', 0)
        userData.save()
    return HttpResponseRedirect('/admin-home/seller-list')

@login_required(login_url="signin")
def approveSeller(request):
    # Apply check for authenticated admin
    if(request.user.is_authenticated and request.user.is_admin == False):
        return HttpResponseRedirect('/signin')
    if(request.user.is_authenticated):
        get_role = Users.objects.filter(user_id=request.user.user_id)[0]
        print("hello", get_role)
        if(get_role.is_admin == 1):
            if (request.POST):
                userIdToActive = request.POST.get('user_id')
                sellerData = Sellers.objects.get(user_id=userIdToActive)
                setattr(sellerData, 'approval_status', 1)
                sellerData.save()
            return HttpResponseRedirect('/admin-home/seller-list')

@login_required(login_url="signin")
def disapproveSeller(request):
    # Apply check for authenticated admin
    if(request.user.is_authenticated and request.user.is_admin == False):
        return HttpResponseRedirect('/signin')
    if(request.user.is_authenticated):
        get_role = Users.objects.filter(user_id=request.user.user_id)[0]
        if(get_role.is_admin == 1):
            if (request.POST):
                userIdToActive = request.POST.get('user_id')
                sellerData = Sellers.objects.get(user_id=userIdToActive)
                setattr(sellerData, 'approval_status', 0)
                sellerData.save()
            return HttpResponseRedirect('/admin-home/seller-list')

@login_required(login_url="signin")
def viewPDF(request):
    if(request.user.is_authenticated and request.user.is_admin == False):
        return HttpResponseRedirect('/signin')
    if(request.user.is_authenticated):
        get_role = Users.objects.filter(user_id=request.user.user_id)[0]
        if (get_role.is_admin == 1):
            if (request.POST):
                userIdToActive = request.POST.get('user_id')
                try:
                    filepath = os.path.join(
                        'static/media/pdf', userIdToActive, 'proof.pdf')
                    return FileResponse(open(filepath, 'rb'), content_type='application/pdf')
                except:
                    raise Http404()
    else:
        redirect('signin')

@login_required(login_url="signin")
def deleteUser(request):
    # Apply check for authenticated admin
    if(request.user.is_authenticated and request.user.is_admin == False):
        return HttpResponseRedirect('/signin')
    if(request.POST):
        userIdToDelete = request.POST.get('user_id')
        userData = Users.objects.get(user_id=userIdToDelete)
        setattr(userData, 'deleted', 1)
        userData.save()
    return HttpResponseRedirect('/admin-home/buyer-list')

@login_required(login_url="signin")
def deleteSeller(request):
    #Apply check for authenticated admin
    if(request.user.is_authenticated and request.user.is_admin == False):
        return HttpResponseRedirect('/signin')
    if(request.POST and request.user.is_authenticated and request.user.is_admin == 1):
        userIdToDelete = request.POST.get('user_id')
        userData = Users.objects.get(user_id=userIdToDelete)
        sellerid = Sellers.objects.get(user_id = userData.user_id)
        products = Products.objects.filter(seller_id = sellerid)
        setattr(userData, 'deleted', 1)
        userData.save()
        for i in products:
            i.status = "inactive"
            i.save()
    return HttpResponseRedirect('/admin-home/seller-list')

@login_required(login_url="signin")
def dropProduct(request):
    #Apply check for authenticated admin
    if(request.user.is_authenticated and request.user.is_admin == False):
        return HttpResponseRedirect('/signin')
    if(request.POST and request.user.is_authenticated and request.user.is_admin == 1):
        userIdToDelete = request.POST.get('pro_id')
        proobj=Products.objects.get(product_id=userIdToDelete)
        pro2=deactivatedProducts(product_name=proobj.product_name, details=proobj.details, category=proobj.category, price=proobj.price, stock=proobj.stock, seller=proobj.seller, status='active' )
        pro2.save()
        Products.objects.get(product_id=userIdToDelete).delete()

    return HttpResponseRedirect('deactivate_product')

@login_required(login_url="signin")
def addProduct(request):
    #Apply check for authenticated admin
    if(request.user.is_authenticated and request.user.is_admin == False):
        return HttpResponseRedirect('/signin')
    if(request.POST and request.user.is_authenticated and request.user.is_admin == 1):
        userIdToDelete = request.POST.get('pro_id')
        proobj=deactivatedProducts.objects.get(product_id=userIdToDelete)
        pro2=Products(product_name=proobj.product_name, details=proobj.details, category=proobj.category, price=proobj.price, stock=proobj.stock, seller=proobj.seller, status='active' )
        pro2.save()
        deactivatedProducts.objects.get(product_id=userIdToDelete).delete()

    return HttpResponseRedirect('activate_product')