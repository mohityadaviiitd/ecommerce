from django.http.response import HttpResponse
from django.shortcuts import render
from estore.models import Cart, UserAddress, Users
from estore.models import Products
from estore.models import ProductImages
from estore.models import Sellers
from estore.models import Wishlist
from django.http import HttpResponseRedirect
import random
import re

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
    imgDetails = ProductImages.objects.get(product_id=item_id)
    
    setattr(productDetails,'image',imgDetails.image)
    # print("ietem id ========", item_id)
    return render(request, 'estore/itemDetails.html',{'product':productDetails})


def signin(request):
    return render(request, 'estore/signin.html')
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


def profile(request):
    return render(request, 'estore/profile.html')


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
