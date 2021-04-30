
from django.contrib import admin
from django.urls import path,re_path,include
from django.views.generic import  TemplateView,RedirectView
from django.conf import settings
from django.conf.urls.static import static

from .views import (
promoter_registration

)

urlpatterns = [


    re_path(r'^promoter_registration/$', promoter_registration, name='promoter_registration'),

]

