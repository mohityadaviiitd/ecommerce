from django.shortcuts import render, redirect, get_object_or_404

from django.contrib.auth import login, authenticate, logout
from .models import Users, Sellers, ProductImages, Products, Cart, UserAddress, Users, Wishlist, DelliverablePincodes, UserAddress
from django.contrib.auth.decorators import login_required
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
import re
from django.forms import modelformset_factory

@login_required(login_url="signin")
def user_profile(request):
    
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
    context={'form1':form1,}
    if(request.user.is_seller==False):
        return render(request, 'estore/user_profile.html', context)
    if(request.user.is_seller==True):
        return render(request, 'estore/seller_profile.html', context)

def deleteAddress(request):
    if(request.POST):
        addr = request.POST.get('address_id')
        u = UserAddress.objects.get(address_id=addr)
        u.delete()
    return redirect('user_address')


def inventory(request,productCategory = "",searchQuery="",filterQuery="",sortBy=""):
    print('-data------------------------',productCategory,   searchQuery,filterQuery)
    filterArr= []
    finalArr = []
    pageTitle = ''
    s=Sellers.objects.get(user=request.user)
    imgData = ProductImages.objects.all()
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
    return render(request, 'estore/inventory.html',{'products':productArr,'pageTitle':pageTitle})

def products(request,productCategory = "",searchQuery="",filterQuery="",sortBy=""):
    print('-data------------------------',productCategory,   searchQuery,filterQuery)
    filterArr= []
    finalArr = []
    pageTitle = ''
    imgData = ProductImages.objects.all()
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
    return render(request, 'estore/productList.html',{'products':productArr,'pageTitle':pageTitle})


def items(request,item_id):
    productDetails = Products.objects.get(product_id=item_id)
    imgDetails = ProductImages.objects.filter(product_id=item_id).first()
    
    setattr(productDetails,'image',imgDetails.image)
    # print("ietem id ========", item_id)
    return render(request, 'estore/itemDetails.html',{'product':productDetails})


def signin(request):
    page= 'signin'
    list(messages.get_messages(request))
    if request.user.is_authenticated:
        return redirect("profile")
    if request.method=='POST':
        email=request.POST['email']
        password=request.POST['password']
        try:
            user=Users.objects.get(email==email)
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
                return redirect('admin')
            if(user.is_seller==True):
                sobj=Sellers.objects.get(user=user)
                if(sobj.approval_status==True):
                    return redirect('inventory')
            return redirect('/')
        else:
            messages.error(request, "email or password incorrect")
        
    return render(request, 'estore/signin.html')

def invalid(request):
    return render(request, 'estore/invalid.html')
def success(request):
    return render(request, 'estore/success.html')
def addToCart(request):
    print('req-------------',request)
    if(request.POST):
        cart_id_form = request.POST.get('cart_id')
        product_id_form = request.POST.get('product_id')
        print("cart" + cart_id_form + "prod_id" + product_id_form)
        try:
            cartObj = Cart.objects.get(
                cart_id=cart_id_form, product_id=product_id_form)
            
            newQuantity = cartObj.quantity + 1
            # print("new =======",newQuantity)
            setattr(cartObj,'quantity',newQuantity)
            # print('inside trty',cartObj)
            # cart = Cart(cart_id=cart_id_form, quantity=1,
            #             product_id=product_id_form)
            cartObj.save()
        except Cart.DoesNotExist:
            # cartObj = Cart.objects.get(
            #     cart_id=cart_id_form, product_id=product_id_form)
            cart = Cart(cart_id=cart_id_form, quantity=1,
                        product_id=product_id_form)
            # cartObj['quantity'] += 1
            # print("quantity=======")
            cart.save()   
    return HttpResponse(status=204)  

# TO_DO--->

# def addToWishlist(request):
#     if(request.POST):
#         wishlist_id_form = request.POST.get('wishlist_id')
#         product_id_form = request.POST.get('product_id')
#         print("cart" + wishlist_id_form + "prod_id" + product_id_form)
#         try:
#             wishlistObj = Wishlist.objects.get(
#                 wish_id=wishlist_id_form, product_id=product_id_form)
            
#             newQuantity = wishlistObj.quantity + 1
#             # print("new =======",newQuantity)
#             setattr(wishlistObj,'quantity',newQuantity)
#             # print('inside trty',cartObj)
#             # cart = Cart(cart_id=cart_id_form, quantity=1,
#             #             product_id=product_id_form)
#             wishlistObj.save()
#         except Cart.DoesNotExist:
#             # cartObj = Cart.objects.get(
#             #     cart_id=cart_id_form, product_id=product_id_form)
#             cart = Cart(wishlist_id=cart_id_form, quantity=1,
#                         product_id=product_id_form)
#             # cartObj['quantity'] += 1
#             # print("quantity=======")
#             cart.save()   
#     return HttpResponse(status=204)



def registerUser(request):
    if request.user.is_authenticated:
        return redirect("profile")
    page='register'
    form=RegisterForm(request.POST or None, request.FILES or None)
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
            return redirect('emailverify')
        else:
            messages.error(request, "Error while registration")
    context={'page': page, 'form':form}
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
    context={'form':form}

    return render(request, 'estore/set_address.html', context)

@login_required(login_url="signin")
def set_pincodes(request):
    if request.user.is_seller==False:
        return redirect('Profile')
    
    sobject=Sellers.objects.get(user=request.user)

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
        user=None
    if user and maketoken.check_token(user, token):
        user.is_email_verified=True
        user.save()
        return redirect('signin')
    return redirect('register')

@login_required(login_url="signin")
def become_seller(request):
    id_user=request.user.user_id
    # if request.user.is_seller==True:
    #     return redirect('profile')
    form=SellerForm(request.POST or None, request.FILES or None)
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
def upload_product_images(request, pk):
    # ImageFormSet = modelformset_factory(ProductImages,form=ProductImagesForm, extra=3)
    # id_user=request.user.user_id
    # uobject=Users.objects.get(user_id=id_user)
    # sobject=Sellers.objects.get(user_id=id_user)
    # form1=ProductForm(request.POST, request.FILES)
    # formset = ImageFormSet(request.POST, request.FILES,queryset=ProductImages.objects.none())
    # if uobject.is_seller==False or sobject.approval_status==False:
    #     return redirect('signin')
    # if request.method == 'POST':
    #     if form1.is_valid() and formset.is_valid():
    #         pro=form1.save(commit=False)
    #         pro.seller=sobject
    #         pro.save()
    #         for form in formset.cleaned_data:
    #             if form:
    #                 image = form['image']
    #                 photo = ProductImages(product=pro, image=image)
    #         return redirect('profile')
        
    
    
    return render(request, 'estore/signin.html')


@login_required(login_url="signin")
def upload_product(request):
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
    context={'form1':form1, 'formset':formset}
    return render(request, 'estore/upload_product.html', context)
    
@login_required(login_url="signin")
def delete_product(request, proid):
    s=Sellers.objects.get(user=request.user)
    prod=Products.objects.get(product_id=proid)
    ss=prod.seller
    if(s==ss):
        ProductImages.objects.filter(product=prod).delete()
        instance = Products.objects.get(product_id=proid)
        instance.delete()
    return render(request, 'estore/upload_product.html')

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
    context={'users':usersArr,}
    return render(request, 'estore/user_address.html', context)


@login_required(login_url="signin")
def edit_product(request, proid):
    s=Sellers.objects.get(user=request.user)
    prod=Products.objects.get(product_id=proid)
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
    context={'form1':form1,
            'formset':formset,
            'proid':proid,
            'product_name':prod.product_name,
            'details':prod.details,
            'price':prod.price,
            'stock':prod.stock,
            'category':prod.category,}
    return render(request, 'estore/edit_product.html', context)







@login_required(login_url="signin")
def signout(request):
    logout(request)
    return redirect('signin')

@login_required(login_url="signin")
def shop(request):
    if(request.POST):
        cart_id_form = request.POST.get('cart_id')
        product_id_form = request.POST.get('product_id')
        print("cart" + cart_id_form + "prod_id" + product_id_form)
        try:
            cartObj = Cart.objects.get(
                cart_id=cart_id_form, product_id=product_id_form)
            
            newQuantity = cartObj.quantity + 1
            # print("new =======",newQuantity)
            setattr(cartObj,'quantity',newQuantity)
            # print('inside trty',cartObj)
            # cart = Cart(cart_id=cart_id_form, quantity=1,
            #             product_id=product_id_form)
            cartObj.save()
           
        except Cart.DoesNotExist:
            # cartObj = Cart.objects.get(
            #     cart_id=cart_id_form, product_id=product_id_form)
            cart = Cart(cart_id=cart_id_form, quantity=1,
                        product_id=product_id_form)
            # cartObj['quantity'] += 1
            # print("quantity=======")
            cart.save()
        
        return HttpResponseRedirect('/')
    else:
        resData = Products.objects.all()
        imgData = ProductImages.objects.all()
        productArr = []
        for i in resData:
            product_dict = {}
            product_dict['id'] = i.product_id
            product_dict['name'] = i.product_name
            product_dict['price'] = int(i.price)
            product_dict['category'] = i.category
            product_dict['description'] = i.details
            product_dict['stock'] = i.stock
            product_dict['status'] = i.status
            productArr.append(product_dict)
        # print("data =========",productArr)
        for i in productArr:
            for j in imgData:
                if (i['id'] == j.product_id):
                    i['image'] = j.image
                    break
        dest = productArr[:]
        random.shuffle(dest)
        productsFeatured = dest[0:6]
        # print(productsFeatured)
        return render(request, 'estore/shop.html', {'product_array': productsFeatured})


@login_required(login_url="signin")
def profile(request):
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
    resUserData = Users.objects.all()
    resAddData = UserAddress.objects.all()
    usersArr = []
    for data in resUserData:
        if(data.deleted != 1):
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
