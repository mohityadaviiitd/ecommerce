from django.shortcuts import render
from estore.models import Cart
from estore.models import Products
from estore.models import ProductImages
from estore.models import Sellers
from estore.models import Wishlist
from django.http import HttpResponseRedirect

def signin(request):
    return render(request, 'estore/signin.html')

def shop(request):
    return render(request, 'estore/shop.html')

def profile(request):
    return render(request, 'estore/profile.html')

def checkout(request):
    return render(request, 'estore/checkout.html')

def cart(request):
    if(request.POST):
        cart_id_form = request.POST.get('cart_id')
        product_id_form = request.POST.get('product_id')
        Cart.objects.filter(cart_id=cart_id_form, product_id=product_id_form).delete()
        return HttpResponseRedirect('')
    else:
        cartid = 1
        data = Cart.objects.filter(cart_id = cartid)
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
                    if(j.stock>i.quantity):
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

        return render(request, 'estore/cart.html', {'product_list': product_list, 'cart_total': cart_total,'cart':cartid})



def epayment(request):
    return render(request, 'estore/epayment.html')

def wishlist(request):
    if (request.POST):
        wishlist_id_form = request.POST.get('wishlist_id')
        product_id_form = request.POST.get('product_id')
        Wishlist.objects.filter(wishlist_id=wishlist_id_form, product_id=product_id_form).delete()
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

