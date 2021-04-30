
from django.contrib import admin
from django.urls import path,re_path,include
from django.views.generic import  TemplateView,RedirectView
from django.conf import settings
from django.contrib.auth.views import LogoutView
from django.conf.urls.static import static
from accounts.views import (
                    # login_page,
logout,
                    register_page,
                    LoginView,

                            )
from .views import (
                    home_page,
                    about_page,
                    contact_page,
                    business,
                    faq,
                    ret_home,
                    investment,
                    investment_plans,
                    investor,
                    payment_method,
                    policy,
                    pricing_plans,
                    success_story,
                    terms,
                    testimonial,news,location,
support,
blog,work
)

urlpatterns = [
    path('', home_page,name='home'),
    path('payments/',include('payments.urls')),
    re_path(r'^logout/$', logout, name='logout'),
    re_path(r'^register/$', register_page, name='register'),
    re_path(r'^login/$', LoginView.as_view(), name='login'),
    path('admin/', admin.site.urls),
    path('dashboard/',include('dashboard.urls')),
    re_path(r'^about/$', about_page,name='about'),
    re_path(r'^support/$', support,name='support'),
    re_path(r'^blog/$', blog,name='blog'),
    re_path(r'^contact_page/$', contact_page,name='contact_page'),
    path('work/',work,name='work'),

    re_path(r'^business/$', business,name='business'),
    re_path(r'^ret_home/', ret_home),
    re_path(r'^faq/$', faq,name='faq'),
    re_path(r'^investment/$', investment,name='investment'),
    re_path(r'^investment_plans/$', investment_plans,name='investment_plans'),
    re_path(r'^investor/$', investor,name='investor'),
    re_path(r'^payment_method/$', payment_method,name='payment_method'),
    re_path(r'^policy/$', policy,name='policy'),
    re_path(r'^pricing_plans/$', pricing_plans,name='pricing_plans'),
    re_path(r'^success_story/$', success_story,name='success_story'),
    re_path(r'^terms/$', terms,name='terms'),
    re_path(r'^testimonial/$', testimonial,name='testimonial'),
    re_path(r'^news/$', news,name='news'),
    re_path(r'^location/$', location,name='location'),

     re_path(r'^accounts/$', RedirectView.as_view(url='/account')),
    re_path(r'^account/', include("accounts.urls")),
    re_path(r'^accounts/', include("accounts.passwords.urls")),
    re_path(r'^promoter/', include("promoter.urls")),

]

if settings.DEBUG:
    urlpatterns = urlpatterns + static(settings.STATIC_URL,document_root=settings.STATIC_ROOT)
    urlpatterns = urlpatterns + static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)