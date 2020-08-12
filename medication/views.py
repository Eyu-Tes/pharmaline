from django.shortcuts import render
from django.shortcuts import get_object_or_404
from .models import Medication


def details(request, med_id):
    med = get_object_or_404(Medication, pk=med_id)
    return render(request, 'medication/details.html', context={'med': med})
