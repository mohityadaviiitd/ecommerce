import uuid
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from .models import Users, Sellers, ProductImages, Products, Cart, UserAddress, Users, Wishlist
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .forms import RegisterForm, SellerForm, ProductForm, ProductImagesForm
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
from django.urls import resolve
import re

def products(request,productCategory = "",searchQuery="",filterQuery="",sortBy=""):
    if(request.user.is_authenticated and request.user.is_admin == True):
        return HttpResponseRedirect('/admin-home')
    current_url = request.path_info
    # print('curnrul;-----',current_url)
    # print('-data------------------------',productCategory,   searchQuery,filterQuery)
    filterArr= []
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
            user['firstName'] = request.user.user_name.split(" ")[0]
            #Note sending userid as cart id,userid is matched with cart_id in CART model
            user['cart_id'] = request.user.user_id
            #Note sending userid as wishlist id,userid is matched with wishlist_id in CART model
            user['wishlist_id'] = request.user.user_id
            wishlistData = Wishlist.objects.filter(wishlist_id = request.user.user_id)
        else:
            user['firstName'] =''
            user['cart_id'] =''
        if productCategory=="" and searchQuery == "" :
            pageTitle="Products"
            # print('1--------------')
            filterArr = Products.objects.all()
        elif productCategory != "" and searchQuery == ""  :
            pageTitle = productCategory
            #  print('2--------------')
            filterArr = Products.objects.filter(category=productCategory)
        elif productCategory == "" and searchQuery != "":
            # print('3--------------')
            pageTitle = "Search Results"
            tempArr = Products.objects.all()
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
            print('mix---------------', type(filterArr))
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
            print('-sorted arr alpla----',finalArr)
        if sortBy == 'price' :
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
            product_dict['inWishlist'] = any(obj.product_id == i.product_id for obj in wishlistData)
            productArr.append(product_dict)
        # print('-------arr product=----------------------',productArr)

        for i in productArr:
                for j in imgData:
                    if (i['id'] == j.product_id):
                        i['image'] = j.image
                        # print("images ==============",j.image)
                        break

        return render(request, 'estore/productList.html',{'products':productArr,'pageTitle':pageTitle,'user':user,'currentUrl':current_url})


def items(request,item_id):
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
            #Note sending userid as cart id,userid is matched with cart_id in CART model
            user['cart_id'] = request.user.user_id
            user['wishlist_id'] = request.user.user_id
            wishlistData = Wishlist.objects.filter(wishlist_id = request.user.user_id)  
        else:
            user['firstName'] =''
            user['cart_id'] =''    
            user['wishlist_id'] =''    

        print("id------", item_id)
        productDetails = Products.objects.get(product_id=item_id)
        imgRes = ProductImages.objects.all()
        images= []
        for img in imgRes:
            if(img.product_id==productDetails.product_id):
                images.append(img.image)
        setattr(productDetails,'images',images)
        setattr(productDetails,'price',int(productDetails.price))
        sellerData = Sellers.objects.get(seller_id = productDetails.seller_id)
        sellerDataFromUserDb = Users.objects.get(user_id = sellerData.user_id )
        setattr(productDetails,'sellerName',sellerDataFromUserDb.user_name)
        setattr(productDetails,'inWishlist',any(obj.product_id == productDetails.product_id for obj in wishlistData))
        # product_dict['inWishlist'] = any(obj.product_id == i.product_id for obj in wishlistData)
        
        return render(request, 'estore/itemDetails.html',{'product':productDetails,'user':user,'currentUrl':current_url})


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
                setattr(cartObj,'quantity',newQuantity)
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

# @login_required(login_url="signin")
def shop(request):
    if(request.user.is_authenticated and request.user.is_admin == True):
        return HttpResponseRedirect('/admin-home')
    if(request.POST):
        if request.user.is_authenticated: 
            wishlist_id_form = request.POST.get('wishlist_id')
            product_id_form = request.POST.get('product_id')
            print('-wish---------------',wishlist_id_form,product_id_form)
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
            #Note sending userid as cart id,userid is matched with cart_id in CART model
            user['cart_id'] = request.user.user_id
            #Note sending userid as wishlist id,userid is matched with wishlist_id in CART model
            user['wishlist_id'] = request.user.user_id
            wishlistData = Wishlist.objects.filter(wishlist_id = request.user.user_id)
        else:
            user['firstName'] =''
            user['cart_id'] =''
        resData = Products.objects.all()
        # print('prod data--------',wishlistData[0].product_id)
        imgData = ProductImages.objects.all()
        productArr = []
        for i in resData:
            print('-------------pid-----',i,i.product_id)
            product_dict = {}
            product_dict['id'] = i.product_id
            product_dict['name'] = i.product_name
            product_dict['price'] = int(i.price)
            product_dict['category'] = i.category
            product_dict['fullDescription'] = i.details
            product_dict['description'] = i.details[0:50] + ' ...'
            product_dict['stock'] = i.stock
            product_dict['status'] = i.status
            product_dict['inWishlist'] = any(obj.product_id == i.product_id for obj in wishlistData)
            productArr.append(product_dict)
        print("data =========",productArr)
        for i in productArr:
            for j in imgData:
                if (i['id'] == j.product_id):
                    i['image'] = j.image
                    break
        dest = productArr[:]
        random.shuffle(dest)
        productsFeatured = dest[0:6]
        # print(productsFeatured)
       
        return render(request, 'estore/shop.html', {'product_array': productsFeatured,'user': user})


@login_required(login_url="signin")
def profile(request):
    if(request.user.is_authenticated and request.user.is_admin == True):
        return HttpResponseRedirect('/admin-home')
    userId = request.user.user_id
    return render(request, 'estore/profile.html')

@login_required(login_url="signin")
def checkout(request):
    return render(request, 'estore/checkout.html')

@login_required(login_url="signin")

def checkout(request):
    return render(request, 'estore/checkout.html')


def cart(request):
    if(request.POST):
        cart_id_form = request.POST.get('cart_id')
        product_id_form = request.POST.get('product_id')

        Cart.objects.filter(cart_id=cart_id_form,
                            product_id=product_id_form).delete()
        return HttpResponseRedirect('')
    else:
        cartid = 1
        data = Cart.objects.filter(cart_id=cartid)
        product_id_list = []
        for i in range(len(data)):
            product_id_list.append(data[i].product_id)
        data2 = Products.objects.filter(product_id__in=product_id_list)
        product_list = []
        seller_id_list = []
        for i in data:
            product_dict = {}
            for j in data2:
                if(i.product_id == j.product_id):
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

        data2 = ProductImages.objects.filter(product_id__in=product_id_list)
        for i in product_list:
            for j in data2:
                if(i['product_id'] == j.product_id):
                    i['product_image'] = j.image
                    break
        data2 = Sellers.objects.filter(seller_id__in=seller_id_list)
        for i in product_list:
            for j in data2:
                if(i['seller_id'] == j.seller_id):
                    i['product_seller_name'] = j.seller_name
        cart_total = 0
        for i in product_list:
            cart_total += i['total_price']
        # print("1=================================", product_list)
        return render(request, 'estore/cart.html', {'product_list': product_list, 'cart_total': cart_total, 'cart': cartid})


@login_required(login_url="signin")
def epayment(request):
    return render(request, 'estore/epayment.html')


def base(request):
    return render(request, 'estore/base.html')

def admin(request):
    return render(request, 'estore/adminBase.html')

def adminBuyer(request):
    if(request.user.is_authenticated and request.user.is_admin == False):
        return HttpResponseRedirect('/signin')
    resUserData = Users.objects.all()
    resAddData = UserAddress.objects.all()
    usersArr = []
    for data in resUserData:
        if(data.deleted != 1 and data.is_seller != 1 and data.is_admin != 1):
            userObj = {}
            userObj['id'] = data.user_id
            userObj['name'] = data.user_name
            userObj['email'] = data.email
            userObj['phone'] = data.phone
            userObj['isPhoneVerified'] = data.is_phone_verified
            userObj['isEmailVerified'] = data.is_email_verified
            userObj['cartId'] = data.cart_id
            userObj['wishlistId'] = data.wishlist_id
            userObj['active'] = data.active #need to be updated
            for address in resAddData:
                if (address.user_id == data.user_id):
                    userObj["address_line"] = str(address.house_no) + ", " + str(address.address_line1) +", " + str(address.address_line2) + ", " + str(address.landmark) + ", " + str(address.pincode)
                    userObj["city"] = address.city_village_name
                    userObj["state"] = address.state
            usersArr.append(userObj) 
    print('----user data----',usersArr)   
    return render(request, 'estore/adminBuyer.html',{'users':usersArr })

def adminSeller(request):
    return render(request, 'estore/adminSeller.html')


def wishlist(request):
    if (request.POST):
        wishlist_id_form = request.POST.get('wishlist_id')
        product_id_form = request.POST.get('product_id')
        Wishlist.objects.filter(
            wishlist_id=wishlist_id_form, product_id=product_id_form).delete()
        return HttpResponseRedirect('')
    else:
        wishlistid = 1
        data = Wishlist.objects.filter(wishlist_id=wishlistid)
        product_id_list = []
        for i in range(len(data)):
            product_id_list.append(data[i].product_id)
        data2 = Products.objects.filter(product_id__in=product_id_list)
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
                    i['product_image'] = j.image
                    break
        data2 = Sellers.objects.filter(seller_id__in=seller_id_list)
        for i in product_list:
            for j in data2:
                if (i['seller_id'] == j.seller_id):
                    i['product_seller_name'] = j.seller_name

        return render(request, 'estore/wishlist.html',
                      {'product_list': product_list, 'wishlist': wishlistid})
def makeUserActive(request):
    #Apply check for authenticated admin
    if(request.POST):
        userIdToActive = request.POST.get('user_id')
        userData = Users.objects.get(user_id = userIdToActive) 
        setattr(userData,'is_active',1)
        setattr(userData,'active',1)
        userData.save()
    return HttpResponseRedirect('/admin-home/buyer-list')
        
def makeUserInactive(request):
    #Apply check for authenticated admin
    if(request.POST):
        userIdToInactive = request.POST.get('user_id')
        userData = Users.objects.get(user_id = userIdToInactive) 
        setattr(userData,'is_active',0)
        setattr(userData,'active',0)
        userData.save()
    return HttpResponseRedirect('/admin-home/buyer-list')


def deleteUser(request):
    #Apply check for authenticated admin
    if(request.POST):
        userIdToDelete = request.POST.get('user_id')
        userData = Users.objects.get(user_id = userIdToDelete) 
        setattr(userData,'deleted',1)
        userData.save()
    return HttpResponseRedirect('/admin-home/buyer-list')
