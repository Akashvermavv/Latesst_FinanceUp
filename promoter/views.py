from django.shortcuts import render

# Create your views here.


def promoter_registration(request):
    return render(request,'promoter/promoter_registration.html')

