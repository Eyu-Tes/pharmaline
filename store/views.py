from django.shortcuts import render


def index(request):
    return render(request, 'store/index.html')


def cart(request):
    return render(request, 'store/cart.html')


def about(request):
    return render(request, 'store/about.html')
