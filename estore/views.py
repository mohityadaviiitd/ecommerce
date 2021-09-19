from django.shortcuts import render

def signin(request):
    return render(request, 'estore/signin.html')

def shop(request):
    return render(request, 'estore/shop.html')

def profile(request):
    return render(request, 'estore/profile.html')

def checkout(request):
    return render(request, 'estore/checkout.html')

def cart(request):
    return render(request, 'estore/cart.html')

def epayment(request):
    return render(request, 'estore/epayment.html')

