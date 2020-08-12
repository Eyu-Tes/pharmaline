from django.shortcuts import render
from medication.models import Medication


def index(request):
    return render(request, 'store/index.html')


def cart(request):
    return render(request, 'store/cart.html')


def about(request):
    return render(request, 'store/about.html')


def store(request):
    try:
        meds = Medication.objects.all()[:12]
    except Medication.DoesNotExist:
        meds = None
    return render(request, 'store/store.html', context={'meds': meds})


def checkout(request):
    return render(request, 'store/checkout.html')


def thankyou(request):
    return render(request, 'store/thankyou.html')
