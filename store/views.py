from django.shortcuts import render
from django.shortcuts import get_object_or_404
from .models import Medication


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


def details(request, med_id):
    med = get_object_or_404(Medication, pk=med_id)
    return render(request, 'store/details.html', context={'med': med})


def checkout(request):
    return render(request, 'store/checkout.html')


def thankyou(request):
    return render(request, 'store/thankyou.html')
