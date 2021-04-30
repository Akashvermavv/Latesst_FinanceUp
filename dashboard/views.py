from django.views.decorators.csrf import csrf_exempt
from django.http import Http404,HttpResponse,JsonResponse
from django.db.models import Q
from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.http import HttpRequest
from django.contrib import messages
from datetime import datetime, timedelta
from django.contrib.auth.hashers import check_password
from django.db.models import Q, Avg, Sum
from . import models
import random
from .models import *
# from accounts.models import User
from accounts.models import User
from accounts.forms import UserDetailChangeForm
from .forms import AllUserNoticeForm,KycForm
from django.views import generic
from django.urls import reverse_lazy, reverse



from pandas.tseries.offsets import BDay
from datetime import timedelta, date

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



def date_by_adding_business_days(from_date, add_days):

    business_days_to_add = add_days
    current_date = from_date
    while business_days_to_add > 0:
        current_date += timedelta(days=1)
        weekday = current_date.weekday()
        if weekday >= 5: # sunday = 6
            continue
        business_days_to_add -= 1
    return current_date






@login_required(login_url='/login/')
def kyc_verification_user_info(request):
    if (not (request.user.staff == True and request.user.admin == True and request.user.is_active == True)):
        messages.error(request, 'You have not  admin access')
        return render(request, 'accounts/login.html', )


    if request.method=='POST':
        # form = UserDetailChangeForm(request.POST,request.FILES,instance=request.user)
        print('in kyc info form valid ---',)
        # if form.is_valid():
        #     form.save()
        #     messages.success(request,f'Your account has been updated successfully')

    else:
        obj = KycVerification.objects.filter(id = request.GET.get('id')).first()


    return render(request,'dashboard/kyc_verification_user_info.html',{'form':obj})



@login_required(login_url='/login/')
def kyc_verification_request(request):

    if (not (request.user.staff == True and request.user.admin == True and request.user.is_active == True)):
        messages.error(request, 'You have not  admin access')
        return render(request, 'accounts/login.html', )
    if(request.method=='POST'):
        id = request.POST.get('id',None)
        action = request.POST.get('action',None)
        print('id @@@',id)
        print('acton @@###',action)

        if(id and action):
            if(action=='approve'):
                try:
                    obj = KycVerification.objects.get(id=id)
                    obj.pending=False
                    obj.approved=True
                    obj.rejected=False
                    obj.save()
                except:
                    obj = None

            elif(action=='reject'):
                print('in reject func')

                obj = KycVerification.objects.filter(id=id)
                if(obj.exists()):
                    obj = obj.first()
                    obj.pending = False
                    obj.approved = False
                    obj.rejected = True
                    obj.save()
                    print('reject testing --',obj.pending,
                    obj.approved ,
                    obj.rejected )

    all_users = KycVerification.objects.filter(pending=True)#.exclude(user__email=request.user.email)
    print('all users data FranchiseWithdraw --',all_users)

    # if len(all_users) == 0:
    #     return render(request, 'dashboard/franchise_request.html',
    #                   {'message': 'you dont have user  record', })
    users_data = []

    for req in all_users:

        first_name = str(req.first_name)
        last_name = str(req.last_name)
        email = req.email
        state = req.state
        city = req.city
        dob = req.dob
        mobile = req.mobile
        nationality = req.nationality
        zipcode = req.zipcode
        passport_image = req.passport_image
        national_id_front_image = req.national_id_front_image
        national_id_back_image = req.national_id_back_image
        driver_license_image = req.driver_license_image
        # country = req.user.country
        pending = req.pending
        obj = req
        print('passprot image ###',passport_image.url)


        # print('users data @@ id  ',users_data,req.id)
        users_data.append({
                            'first_name': first_name,
                            'last_name': last_name,
                            'state': state,
                            'city': city,
                            'dob': dob,
                            'mobile': mobile,
                            'nationality': nationality,
                            'zipcode': zipcode,

                           'email': email,
                           'passport_image':passport_image,
                           'national_id_front_image':national_id_front_image,
                           'national_id_back_image':national_id_back_image,
                           'driver_license_image':driver_license_image,
                            'id':req.id,'pending':pending,
                           })
    print('all users data franchise withdraw --', users_data)

    page = request.GET.get('page', 1)
    paginator = Paginator(users_data, 10)

    try:
        hist = paginator.page(page)
    except PageNotAnInteger:
        hist = paginator.page(1)
    except EmptyPage:
        hist = paginator.page(paginator.num_pages)


    return  render(request,'dashboard/kyc_verification_request.html',{'history': hist, })



@login_required(login_url='/login/')
def kyc_verification2(request):
   
    form = KycForm()
    if request.method == 'POST':
        print('post data @@',request.POST)
        form = KycForm(request.POST, request.FILES or None)
        if form.is_valid():
            messages.success(request, 'kyc form submit successfully', )
            zipcode = form.cleaned_data.get('zipcode')
            
            # form.save(commit=False)
            # form
            obj = form.save(commit=False)
            obj.zipcode = int(zipcode)
            obj.user = request.user
            obj.save()
            return redirect('dashboard')
        else:
            context = {
                'form': form,
            }
            return render(request, "dashboard/kyc_verification2.html", context)
    kyc_obj = None
    kyc_objs = KycVerification.objects.filter(user = request.user)

    if(kyc_objs):
        kyc_obj = kyc_objs.first()
    form = KycForm()
    context = {
        'form': form,
        'kyc_obj':kyc_obj
    }
    return  render(request,'dashboard/kyc_verification2.html',context)











def test(request):
	return  render(request,'accounts/activation.html')
	
	




@login_required(login_url='/login/')
def withdraw_pending(request):
    exist = check_exist_or_not(request)
    if (not exist):
        return redirect('add_premium_plan')
    exist=False

    all_withdraw_data = FranchiseWithdraw.objects.filter(
                                                        user=request.user,
                                                         payment_pending=True,
                                                        payment_rejected=False,
                                                        payment_approved=False
                                                         )
    record=False
    if len(all_withdraw_data) == 0:
        return render(request, 'dashboard/withdraw-pending.html',
                      {'message': 'you dont have any pending withdraw request', 'exist': exist,'record':record})

    withdraw_data = []

    for req in all_withdraw_data:
        record=True
        status='pending'
        name = req.user.first_name
        date = req.date
        amount = req.amount
        method = req.payment_method
        payment_address = req.payment_address


        # payment_done = req.payment_done
        # payment_error = req.payment_error
        withdraw_data.append({
                            'name':name,
                            'date': date,
                              'amount': amount,
                              'method': method,
                              'payment_address': payment_address,
                              'status': status,
            'record':record
                              })

    page = request.GET.get('page', 1)
    paginator = Paginator(withdraw_data, 10)

    try:
        hist = paginator.page(page)
    except PageNotAnInteger:
        hist = paginator.page(1)
    except EmptyPage:
        hist = paginator.page(paginator.num_pages)

    return render(request, 'dashboard/withdraw-pending.html', {'hist': hist, 'exist': exist,'record':record})



@login_required(login_url='/login/')
def deposit_money(request):
    # exist = check_exist_or_not(request)
    # if (not exist):
    #     return redirect('add_premium_plan')
    if request.method == 'GET':
        try:
            obj = balance.objects.get(user=request.user)
            bal = obj.current_balance

            print('bal in try is --', bal)
        except:
            bal = 0
        return render(request, 'dashboard/add_fund.html',{'bal':bal})



def dfs_tree(visited, node,html_code,level):
    if node not in visited and level<4:
        print (node)
        if level==1:
            level_str="first"
        if level==2:
            level_str="second"
        if level==3:
            level_str="third"

        url="#"
        if node==None:
            html_code += """<li class="tree-%s-user">
                                    <a href="%s">%s</a>""" % (level_str, url, "None")
            return html_code
        visited.add(node)
        left=node.left
        right=node.right
        url = "/dashboard/binary_tree/%d" % (node.id)
        html_code += """<li class="tree-%s-user">
                        <a href="%s">%s</a> <ul>""" % (level_str, url, node.username)

        html_code=dfs_tree(visited,left,html_code,level+1)
        html_code += "</li>"
        html_code=dfs_tree(visited,right,html_code,level+1)
        html_code += "</li>"
        html_code+="</ul>"
    return html_code








def all_user_notice(request):
    if (not (request.user.staff == True and request.user.admin == True and request.user.is_active == True)):
        messages.error(request, 'You have not  admin access')
        return render(request, 'accounts/login.html', )
    if(request.method=='POST'):
        form = AllUserNoticeForm(request.POST)
        if form.is_valid():
            messages.success(request,'All users notice add successfully')
            form.save()



    form = AllUserNoticeForm()
    return render(request,'dashboard/admin_notice.html',{'form':form})

def check_amount(amount):

    if amount<99:
        return 0
    if amount>=100 and amount <499:
        return 100
    if amount>=500 and amount <999:
        return 500
    if amount>=1000 and amount <1999:
        return 1000
    if amount>=2000 and amount <4999:
        return 2000
    if amount>=5000 and amount <9999:
        return 5000
    if amount>=10000 and amount <19999:
        return 10000
    if amount>=20000 and amount <49999:
        return 20000
    if amount>=50000 and amount <99999:
        return 50000
    if amount>=100000 :
        return 100000


def dfs(visited, node,total_amount=0):
    if node.left == None or node.right==None:
        return node.investment_carry
    if node not in visited:
        print (node)
        visited.add(node)
        investment_package=False
        left_amount=dfs(visited, node.left,total_amount)
        right_amount=dfs(visited, node.right,total_amount)

        parent_amount=0
        if left_amount <= right_amount :
            amount=check_amount(left_amount)
            obj = PurchasedPackage.objects.filter(user=node).order_by(
                '-partnership_package__matching_bonus_in_per').first()
            if obj is not None and obj.partnership_package is None:
                obj = PurchasedPackage.objects.filter(user=node).order_by(
                '-investment_package__matching_bonus_in_per').first()
                investment_package=True
            if obj is not None:
                if investment_package==True:
                    parent_amount = (amount * (obj.investment_package.matching_bonus_in_per / 100))
                else:
                    parent_amount = (amount * (obj.partnership_package.matching_bonus_in_per / 100))

            if node.left!=None:
                node.left.investment_carry -= left_amount
                node.left.save()
            if node.right!=None:
                node.right.investment_carry -= amount
                node.right.save()
        else:
            amount = check_amount(right_amount)
            obj = PurchasedPackage.objects.filter(user=node).order_by(
                '-partnership_package__matching_bonus_in_per').first()
            if obj is not None and obj.partnership_package is None:
                obj = PurchasedPackage.objects.filter(user=node).order_by(
                    '-investment_package__matching_bonus_in_per').first()
                investment_package=True
            if obj is not None:
                if investment_package==True:
                    parent_amount = (amount * (obj.investment_package.matching_bonus_in_per / 100))
                else:
                    parent_amount = (amount * (obj.partnership_package.matching_bonus_in_per / 100))
            if node.left!=None:
                node.left.investment_carry -= amount
                node.left.save()
            if node.right!=None:
                node.right.investment_carry -= right_amount
                node.right.save()
        parent_balance = balance.objects.get(user=node)
        if parent_amount>0:
            parent_balance.current_balance += (parent_amount)
            parent_balance.save()
            deposit_history.objects.create(user=node, amount=parent_amount)
    return node.investment_carry


def dfs_matching(request):
    visited=set()
    users=User.objects.all()
    for user in users:
        if user not in visited:
            result=dfs(visited,user)
    return  HttpResponseRedirect(reverse('dashboard'))



def ban_user(request):
    print('in ban user method is ',request.method)
    id = None
    if (not (request.user.staff == True and request.user.admin == True and request.user.is_active == True)):
        messages.error(request, 'You have not  admin access')
        return render(request, 'accounts/login.html', )
    if(request.method=='POST'):

        id = request.POST.get('id',None)
        print('id $$$$',id)
        try:
            if(request.user.admin):
                obj  = User.objects.get(id=id)
                obj.ban=True
                obj.save()
                messages.info(request, 'User ban successfully')
        except:
            pass




    all_users = User.objects.all().exclude(email=request.user.email)
    print('all users data --', all_users)

    if len(all_users) == 0:
        return render(request, 'dashboard/sendmoney_history.html',
                      {'message': 'you dont have user  record', })
    users_data = []
    for req in all_users:
        name = str(req.first_name) + ' ' + str(req.last_name)
        email = req.email
        country = req.country
        ban = req.ban
        obj = req
        print('users data @@', users_data)
        users_data.append({'name': name, 'email': email,'ban':ban, 'country': country.name, 'id':req.id})
    print('all users data --', users_data)

    page = request.GET.get('page', 1)
    paginator = Paginator(users_data, 10)

    try:
        hist = paginator.page(page)
    except PageNotAnInteger:
        hist = paginator.page(1)
    except EmptyPage:
        hist = paginator.page(paginator.num_pages)

    return render(request, 'dashboard/manage_users.html', {'history': hist, })




def unban_user(request):
    print('in unban user method is ',request.method)
    id = None
    if (not (request.user.staff == True and request.user.admin == True and request.user.is_active == True)):
        messages.error(request, 'You have not  admin access')
        return render(request, 'accounts/login.html', )
    if(request.method=='POST'):

        id = request.POST.get('id',None)
        print('id $$$$',id)
        try:
            if(request.user.admin):
                obj  = User.objects.get(id=id)
                obj.ban=False
                obj.save()
                messages.info(request, 'User unban successfully')
        except:
            pass




    all_users = User.objects.all().exclude(email=request.user.email)
    print('all users data --', all_users)

    if len(all_users) == 0:
        return render(request, 'dashboard/sendmoney_history.html',
                      {'message': 'you dont have user  record', })
    users_data = []
    for req in all_users:
        name = str(req.first_name) + ' ' + str(req.last_name)
        email = req.email
        country = req.country
        ban = req.ban
        obj = req
        print('users data @@', users_data)
        users_data.append({'name': name, 'email': email,'ban':ban, 'country': country.name, 'id':req.id})
    print('all users data --', users_data)

    page = request.GET.get('page', 1)
    paginator = Paginator(users_data, 10)

    try:
        hist = paginator.page(page)
    except PageNotAnInteger:
        hist = paginator.page(1)
    except EmptyPage:
        hist = paginator.page(paginator.num_pages)

    return render(request, 'dashboard/manage_users.html', {'history': hist, })


@login_required
def add_premium_plan(request):
	if request.session.has_key('order_number'):
		del request.session['order_number']
		del request.session['user_id']
	user_id=request.user.id
	order_number=random.randint(100,999)
	request.session['user_id']=user_id
	request.session['order_number']=order_number
	objs = PremiumPlan.objects.filter(user=request.user)
	activate=False
	exist=False
	if (objs.exists() and objs.count() == 1):
		obj = objs.first()
		if (obj.plan == False):
			activate = obj.plan
			return render(request,'dashboard/add_premium_plan.html',{'user_id':user_id,'order_number':order_number,'activate':activate,'exist':exist})
		else:
			activate=True
			exist = True
			return render(request, 'dashboard/add_premium_plan.html',
						  {'user_id': user_id, 'order_number': order_number, 'activate': activate,'exist':exist})
	else:
		activate=False
		return render(request, 'dashboard/add_premium_plan.html',
					  {'user_id': user_id, 'order_number': order_number, 'activate': activate,'exist':exist})







# def binary_tree(request):
#     exist = check_exist_or_not(request)
#     if (not exist):
#         return redirect('add_premium_plan')
#     return render(request, 'dashboard/binary_tree.html')

# def bfs(visited,queue, node):
#     visited.append(node)
#     queue.append(node)
#     user_dict = {}
#     while queue:
#         parent = queue.pop(0)
#         level=(parent.level)+1
#         if level not in user_dict:
#             user_dict[level]=[]
#         left=parent.left
#         right=parent.right
#         visited.append(parent)
#         if left==None:
#             user_dict[level].append(None)
#         else :
#             user_dict[level ].append(left)
#             queue.append(left)
#         if right==None:
#             user_dict[level].append(None)
#         else:
#             user_dict[level].append(right)
#
#     # level_power=1
#     # for key,value in user_dict.items():
#     #     check=2**level_power
#     #     level_power+=1
#     #     if len(user_dict[key])<check:
#     #         for x in range(check-len(user_dict[key])):
#     #             user_dict[key].append(None)
#     return user_dict

def binary_tree(request,pk):
    exist = check_exist_or_not(request)
    if (not exist):
        return redirect('add_premium_plan')
    html_code = dfs_tree(set(), User.objects.filter(id=pk).first(), "<ul>",1)

    return render(request, 'dashboard/binary_tree.html', {'html_code': html_code})

def add_carry_to_parent(user,amount):
    while(user !=None and user.parent!=user):
        user.investment_carry+=amount
        user.save()
        user=user.parent
    return

def plans(request,package=None):

    exist = check_exist_or_not(request)
    if (not exist):
        return redirect('add_premium_plan')

    objs = PurchasedPackage.objects.filter(user=request.user)
    package_list = []
    for obj in objs:
        if (obj.investment_package):
            package_list.append(obj.investment_package.package)
        elif (obj.partnership_package):
            package_list.append(obj.partnership_package.package)

    if(request.method=='POST'):
        print('package is ####', request.POST['package'])
        package_type = request.POST.get('package_type')
        amount = float(request.POST.get('amount'))
        if (package_type == 'investment'):
            package = request.POST['package']
            if (request.POST['package']):
                obj = InvestmentPlans.objects.filter(package=package).first()
                initial = obj.invest_start
                final = obj.invest_end
                print('amount --', amount)
                print('initial --', initial)
                print('final --', final)
                if (package == 'starter'):
                    cond = True
                else:
                    cond = amount >= initial and amount <= final

                if (cond):
                    # b = balance.objects.get(user=request.user)
                    # b.current_balance = (b.current_balance - amount)
                    # b.save()
                    try:
                        bal = balance.objects.get(user=request.user).current_balance
                        bal = round(bal, 2)
                    except:
                        bal = 0
                    if (bal > 0 and bal >= amount):
                        b = balance.objects.get(user=request.user)
                        b.current_balance = (b.current_balance - amount)
                        b.save()
                        start_date = datetime.now().date()
                        days = obj.total_days
                        
                        end_date =start_date + BDay(int(days))
                        PurchasedPackage.objects.create(user=request.user, investment_package=obj,end_package=end_date,
                                                        invest_amount= amount,last_benefit_date=start_date,package_start = start_date)
                        messages.success(request, 'Package Successfully Added..')
                        user = request.user
                        amount_in_float = float(amount)
                        add_carry_to_parent(user,amount_in_float)
                        parent = User.objects.filter(username=user.parent_refer_id).first()
                        print(user.parent_refer_id)
                        which_package='partnership'
                        parent_obj = PurchasedPackage.objects.filter(user=parent).order_by(
                            '-partnership_package__matching_bonus_in_per').first()

                        if parent_obj is not None and parent_obj.partnership_package is None:
                            parent_obj = PurchasedPackage.objects.filter(user=parent).order_by(
                                '-investment_package__matching_bonus_in_per').first()
                            which_package = 'investment'

                        print(parent_obj)
                        left_amount = 0
                        right_amount = 0
                        if parent != None:
                            try:
                                parent_balance = balance.objects.get(user=parent)
                            except:
                                parent_balance = balance.objects.create(user=parent)
                            if parent_obj!=None:
                                if which_package=='investment':
                                    sponser_amount = (amount_in_float * (parent_obj.investment_package.sponsor_bonus_in_per / 100))
                                else:
                                    sponser_amount = (amount_in_float * (parent_obj.partnership_package.sponsor_bonus_in_per / 100))

                                parent_balance.current_balance += (sponser_amount)
                                parent_balance.save()
                                deposit_history.objects.create(user=request.user.parent, amount=sponser_amount)

                        superuser = User.objects.filter(admin=True).first()
                        superuser_balance = balance.objects.get(user=superuser)

                        superuser_balance.current_balance += (amount_in_float)

                        superuser_balance.save()
                        deposit_history.objects.create(user=superuser, amount=amount_in_float)

                        # PurchasedPackage.objects.create(user=request.user, investment_package=obj)
                        messages.success(request, f'{obj.package} package Successfully Added..')
                        return redirect('dashboard')
                        # print('starter package is these')
                    else:
                        messages.error(request, 'You have insufficient Money for buy Package')
                        return render(request, 'dashboard/plans.html')
                else:
                    messages.error(request, 'You have enter invalid Money for buy  ' + package + ' Package')
                    return render(request, 'dashboard/plans.html')

        elif (package_type == 'partnership'):
            package = request.POST['package']
            if (request.POST['package']):
                obj = PartnershipPlans.objects.filter(package=package).first()
                initial_price = obj.invest_price
                request.user.monthly_royality+=obj.monthly_royality_in_per
                if(request.user.monthly_royality_last_date==None):
                    request.user.monthly_royality_last_date = datetime.now().date()

                # b = balance.objects.get(user=request.user)
                # b.current_balance = (b.current_balance - amount)
                # b.save()
                if (amount >= initial_price):
                    try:
                        bal = balance.objects.get(user=request.user).current_balance
                        bal = round(bal, 2)
                    except:
                        bal = 0
                    if (bal > 0 and bal >= amount):
                        b = balance.objects.get(user=request.user)
                        b.current_balance = (b.current_balance - amount)
                        b.save()
                        if (obj):
                            parent = User.objects.filter(username=request.user.parent_refer_id).first()
                            amount_in_float = float(amount)
                            if parent != None:
                                parent_balance = balance.objects.get(user=parent)
                                sponser_amount = (amount_in_float * (10 / 100))
                                request.user.investment_carry+=0
                                request.user.save()
                                parent_balance.current_balance += (sponser_amount)
                                parent_balance.save()
                                deposit_history.objects.create(user=request.user.parent, amount=sponser_amount)
                            superuser = User.objects.filter(admin=True).first()
                            superuser_balance = balance.objects.get(user=superuser)
                            superuser_balance.current_balance += (amount_in_float)
                            superuser_balance.save()
                            deposit_history.objects.create(user=superuser, amount=amount_in_float)
                        start_date = datetime.now().date()
                        days = obj.total_days
                        end_date = start_date + BDay(int(days))
                        PurchasedPackage.objects.create(user=request.user, partnership_package=obj, end_package=end_date,
                                                        invest_amount= amount,last_benefit_date=start_date,package_start = start_date)

                        # PurchasedPackage.objects.create(user=request.user, partnership_package=obj)

                        messages.success(request, 'Package Successfully Added..')
                        return redirect('dashboard')
                        # print('starter package is these')
                    else:
                        messages.error(request, 'You have insufficient Money for buy Package')
                        return render(request, 'dashboard/plans.html')
                else:
                    messages.error(request, 'You have enter invalid Money for buy  ' + package + ' Package')
                    return render(request, 'dashboard/plans.html')

        return render(request, 'dashboard/plans.html')
    return render(request, 'dashboard/plans.html', {'package_list': package_list})






def purchased_plans(request):
    objs = PurchasedPackage.objects.filter(user=request.user)
    package_list_investment = []
    package_list_partnership = []
    for obj in objs:
        if (obj.investment_package):
            package_list_investment.append(obj.investment_package.package)
        elif (obj.partnership_package):
            package_list_partnership.append(obj.partnership_package.package)
    return render(request,'dashboard/purchased_plans.html',{
        'package_list_investment':package_list_investment,
        'package_list_partnership':package_list_partnership,
                                                            })

def test(request):
    return render(request, 'accounts/activation.html')


def check_exist_or_not(request):
    objs = PremiumPlan.objects.filter(user=request.user)
    exist = False
    if (objs.exists() and objs.count() == 1):
        obj = objs.first()
        if (obj.plan == True):
            exist = True
    return exist

@login_required(login_url='/login/')
def admin_dashboard(request):
    if(not (request.user.staff==True and request.user.admin==True and request.user.is_active==True )):
        messages.error(request,'You have admin access')
        return render(request,'accounts/login.html',)

    return render(request,'dashboard/admin_dashboard.html',{})


@login_required(login_url='/login/')
def manage_user(request):
    if (not (request.user.staff == True and request.user.admin == True and request.user.is_active == True)):
        messages.error(request, 'You have not  admin access')
        return render(request, 'accounts/login.html', )
    all_users = User.objects.all().exclude(email=request.user.email)
    print('all users data --',all_users)

    if len(all_users) == 0:
        return render(request, 'dashboard/sendmoney_history.html',
                      {'message': 'you dont have user  record', })
    users_data = []
    for req in all_users:
        name = str(req.first_name)+' '+str(req.last_name)
        email = req.email
        country = req.country
        obj = req
        print('users data @@ id  ',users_data,req.id)
        users_data.append({'name': name, 'email': email, 'country': country.name,'id':req.id})
    print('all users data --', users_data)

    page = request.GET.get('page', 1)
    paginator = Paginator(users_data, 10)

    try:
        hist = paginator.page(page)
    except PageNotAnInteger:
        hist = paginator.page(1)
    except EmptyPage:
        hist = paginator.page(paginator.num_pages)

    return render(request, 'dashboard/manage_users.html',  {'history': hist, })








# @login_required(login_url='/login/')
# def franchise_request(request):
#     if (not (request.user.staff == True and request.user.admin == True and request.user.is_active == True)):
#         messages.error(request, 'You have not  admin access')
#         return render(request, 'accounts/login.html', )
#     if(request.method=='POST'):
#         id = request.POST.get('id',None)
#         action = request.POST.get('action',None)

#         if(id and action):
#             if(action=='approve'):
#                 obj = FranchiseWithdraw.objects.get(id=id)
#                 obj.payment_pending=False
#                 obj.payment_approved=True
#                 obj.payment_rejected=False
#                 obj.save()
#             elif(action=='reject'):
#                 obj = FranchiseWithdraw.objects.get(id=id)
#                 obj.payment_pending = False
#                 obj.payment_approved = False
#                 obj.payment_rejected = True
#                 obj.save()






#     all_users = FranchiseWithdraw.objects.filter(payment_pending=True).exclude(user__email=request.user.email)
#     print('all users data --',all_users)

#     if len(all_users) == 0:
#         return render(request, 'dashboard/franchise_request.html',
#                       {'message': 'you dont have user  record', })
#     users_data = []
#     for req in all_users:
#         name = str(req.user.first_name)+' '+str(req.user.last_name)
#         email = req.user.email
#         country = req.user.country
#         pending = req.payment_pending
#         obj = req
#         amount = req.amount
#         payment_method = req.payment_method
#         # print('users data @@ id  ',users_data,req.id)
#         users_data.append({'name': name, 'email': email,'amount':amount,'payment_method':payment_method, 'country': country.name,'id':req.id,'pending':pending})
#     print('all users data --', users_data)

#     page = request.GET.get('page', 1)
#     paginator = Paginator(users_data, 10)

#     try:
#         hist = paginator.page(page)
#     except PageNotAnInteger:
#         hist = paginator.page(1)
#     except EmptyPage:
#         hist = paginator.page(paginator.num_pages)

#     return render(request, 'dashboard/franchise_request.html',  {'history': hist, })











@login_required(login_url='/login/')
def franchise_request(request):
    if (not (request.user.staff == True and request.user.admin == True and request.user.is_active == True)):
        messages.error(request, 'You have not  admin access')
        return render(request, 'accounts/login.html', )
    if(request.method=='POST'):
        id = request.POST.get('id',None)
        action = request.POST.get('action',None)
        print('id @@@',id)
        print('acton @@###',action)

        if(id and action):
            if(action=='approve'):
                obj = FranchiseWithdraw.objects.get(id=id)
                obj.payment_pending=False
                obj.payment_approved=True
                obj.payment_rejected=False
                
                
                try:
                    target_user = obj.user
                    objss = balance.objects.filter(user = target_user)
                    admin_objss = balance.objects.filter(user__admin=True)
                    if(objss.exists()):
                        if(admin_objss.exists()):
                            admin_objss = admin_objss.first()
                            if(admin_objss.current_balance>0):
                                admin_objss.current_balance = (admin_objss.current_balance + obj.amount)
                                admin_objss.save()
                            else:
                                messages.error(request,'Admin account not have sufficient fund to approve this request')
                                return render(request, 'dashboard/franchise_request.html', )

                        objss = objss.first()
                        objss.current_balance = (objss.current_balance - obj.amount)
                        objss.save()
                except:
                    pass
                
                obj.save()
            elif(action=='reject'):
                print('in reject func')

                obj = FranchiseWithdraw.objects.filter(id=id)
                if(obj.exists()):
                    obj = obj.first()
                    obj.payment_pending = False
                    obj.payment_approved = False
                    obj.payment_rejected = True
                    obj.save()

                    print('reject testing --',obj.payment_pending,
                    obj.payment_approved ,
                    obj.payment_rejected )





    all_users = FranchiseWithdraw.objects.filter(payment_pending=True,payment_rejected=False,payment_approved=False)#.exclude(user__email=request.user.email)
    print('all users data FranchiseWithdraw --',all_users)

    # if len(all_users) == 0:
    #     return render(request, 'dashboard/franchise_request.html',
    #                   {'message': 'you dont have user  record', })
    users_data = []

    for req in all_users:
        payment_method = None
        payment_address = None
        name = str(req.user.first_name)+' '+str(req.user.last_name)
        email = req.user.email
        # country = req.user.country
        pending = req.payment_pending
        obj = req
        amount = req.amount
        if(req.payment_method):
            payment_method = req.payment_method
            payment_address = req.payment_address

        # print('users data @@ id  ',users_data,req.id)
        users_data.append({'name': name, 'email': email,'amount':amount,'payment_method':payment_method, 'id':req.id,'pending':pending,
                           'payment_address':payment_address})
    print('all users data franchise withdraw --', users_data)

    # all_users = withdraw_requests.objects.filter(
    #     payment_pending=True,
    #     payment_rejected=False
    # ).exclude(user__admin=True)
    # print('all users withdraw requests data --', all_users)
    #
    # if len(all_users) == 0:
    #     return render(request, 'dashboard/franchise_request.html',
    #                   {'message': 'you dont have user  record', })
    # users_data = []
    # for req in all_users:
    #     name = str(req.user.first_name) + ' ' + str(req.user.last_name)
    #     email = req.user.email
    #     # country = req.user.country
    #     pending = req.payment_pending
    #     payment_address = req.payment_address
    #     obj = req
    #     amount = req.amount
    #     payment_method = req.method
    #     # print('users data @@ id  ',users_data,req.id)
    #     users_data.append(
    #         {'name': name, 'email': email, 'amount': amount, 'payment_method': payment_method,
    #          'id': req.id, 'pending': pending,'payment_address':payment_address})
    # print('all users data --', users_data)




    page = request.GET.get('page', 1)
    paginator = Paginator(users_data, 10)

    try:
        hist = paginator.page(page)
    except PageNotAnInteger:
        hist = paginator.page(1)
    except EmptyPage:
        hist = paginator.page(paginator.num_pages)

    return render(request, 'dashboard/franchise_request.html',  {'history': hist, })




@login_required(login_url='/login/')
def franchise_deposit_request(request):
    if (not (request.user.staff == True and request.user.admin == True and request.user.is_active == True)):
        messages.error(request, 'You have not  admin access')
        return render(request, 'accounts/login.html', )
    if(request.method=='POST'):
        id = request.POST.get('id',None)
        action = request.POST.get('action',None)
        print('id @@@',id)
        print('acton @@###',action)

        if(id and action):
            if(action=='approve'):
                obj = DepositMoney.objects.get(id=id)
                obj.payment_pending=False
                obj.payment_approved=True
                obj.payment_rejected=False
                
                
                try:
                    target_user = obj.user
                    objss = balance.objects.filter(user = target_user)
                    admin_objss = balance.objects.filter(user__admin=True)
                    if(objss.exists()):
                        if(admin_objss.exists()):
                            admin_objss = admin_objss.first()
                            if(admin_objss.current_balance>0):
                                admin_objss.current_balance = (admin_objss.current_balance - obj.amount)
                                admin_objss.save()
                            else:
                                messages.error(request,'Admin account not have sufficient fund to approve this request')
                                return render(request, 'dashboard/franchise_deposit_request.html', )

                        objss = objss.first()
                        objss.current_balance = (objss.current_balance + obj.amount)
                        objss.save()
                except:
                    pass    
                
                obj.save()
            elif(action=='reject'):
                print('in reject func')

                obj = DepositMoney.objects.filter(id=id)
                if(obj.exists()):
                    obj = obj.first()
                    obj.payment_pending = False
                    obj.payment_approved = False
                    obj.payment_rejected = True
                    obj.save()

                    print('reject testing --',obj.payment_pending,
                    obj.payment_approved ,
                    obj.payment_rejected )





    all_users = DepositMoney.objects.filter(payment_pending=True,payment_rejected=False,payment_approved=False)#.exclude(user__email=request.user.email)
    print('all users data FranchiseWithdraw --',all_users)

    # if len(all_users) == 0:
    #     return render(request, 'dashboard/franchise_request.html',
    #                   {'message': 'you dont have user  record', })
    users_data = []

    for req in all_users:
        payment_method = None
        payment_address = None
        name = str(req.user.first_name)+' '+str(req.user.last_name)
        email = req.user.email
        # country = req.user.country
        pending = req.payment_pending
        obj = req
        amount = req.amount
        if(req.payment_method):
            payment_method = req.payment_method
            payment_address = req.payment_address

        # print('users data @@ id  ',users_data,req.id)
        users_data.append({'name': name, 'email': email,'amount':amount,'payment_method':payment_method, 'id':req.id,'pending':pending,
                           'payment_address':payment_address})
    print('all users data franchise withdraw --', users_data)

    # all_users = withdraw_requests.objects.filter(
    #     payment_pending=True,
    #     payment_rejected=False
    # ).exclude(user__admin=True)
    # print('all users withdraw requests data --', all_users)
    #
    # if len(all_users) == 0:
    #     return render(request, 'dashboard/franchise_request.html',
    #                   {'message': 'you dont have user  record', })
    # users_data = []
    # for req in all_users:
    #     name = str(req.user.first_name) + ' ' + str(req.user.last_name)
    #     email = req.user.email
    #     # country = req.user.country
    #     pending = req.payment_pending
    #     payment_address = req.payment_address
    #     obj = req
    #     amount = req.amount
    #     payment_method = req.method
    #     # print('users data @@ id  ',users_data,req.id)
    #     users_data.append(
    #         {'name': name, 'email': email, 'amount': amount, 'payment_method': payment_method,
    #          'id': req.id, 'pending': pending,'payment_address':payment_address})
    # print('all users data --', users_data)




    page = request.GET.get('page', 1)
    paginator = Paginator(users_data, 10)

    try:
        hist = paginator.page(page)
    except PageNotAnInteger:
        hist = paginator.page(1)
    except EmptyPage:
        hist = paginator.page(paginator.num_pages)

    return render(request, 'dashboard/franchise_deposit_request.html',  {'history': hist, })
    
@login_required(login_url='/login/')
def deposit_request(request):
    # exist = check_exist_or_not(request)
    # if (not exist):
    #     return redirect('add_premium_plan')
    print('get --',request.GET)
    print('post --',request.POST)
    try:
        obj = balance.objects.get(user=request.user)
        bal = obj.current_balance

        print('bal in try is --', bal)
    except:
        bal = 0
    data= request.POST
    if request.method == 'POST':
        # method = None

        payment_method = data.get('method')
        payment_address = data.get('payment_address_input')
        try:
            amount = float(data.get('amount'))
        except:
            amount=0
        password = data.get('password')
        print('no error ')

        # if via == 'pm':
        #     method = pm_accounts
        #     str_method = 'perfectMoney'
        # elif via == 'bt':
        #     method = bank_accounts
        #     str_method = 'Bank transfer'
        # elif via == 'at':
        #     method = agent_accounts
        #     str_method = 'agent transfer'
        # elif via == 'bkash':
        #     method = bkash_accounts
        #     str_method = 'bkash transfer'
        # elif via == 'rocket':
        #     method = rocket_accounts
        #     str_method = 'rocket transfer'
        # elif via == 'nagad':
        #     method = nagad_accounts
        #     str_method = 'nagad transfer'
        # else:
        #     method = None

        check = balance.objects.get(user=request.user).current_balance
        if amount <= 0:
            # return JsonResponse({'message': 'not enough funds to withdraw'})
            messages.error(request,'invalid range of money for deposit')
            return render(request, 'dashboard/add_fund.html',{'bal':bal})
        print('no error 2')

        # if amount < 100 and str_method == 'Bank transfer':
        #     return JsonResponse({'message': 'minimum withdraw for bank is 100$'})
        #
        # if amount < 10 and str_method == 'agent transfer':
        #     return JsonResponse({'message': 'minimum withdraw for agent transfer is 10$'})

        # if amount < 50 and str_method == 'perfectMoney':
        #     return JsonResponse({'message': 'minimum withdraw for perfectMoney is 50$'})
        # if amount < 15 and (
        #         str_method == 'bkash transfer' or str_method == 'rocket transfer' or str_method == 'nagad transfer'):
        #     return JsonResponse({'message': 'minimum withdraw for mobile bank is 15$'})

        if check_password(password, request.user.password) != True:
            messages.error(request,'password did not match')
            return render(request, 'dashboard/add_fund.html',{'bal':bal})
            # return JsonResponse({'message': 'password did not match'})
        print('no error 3')

        # try:
        #     method.objects.get(user=request.user)
        # except method.DoesNotExist:
        #     return JsonResponse({'message': 'payment account is not added'})

        # b = balance.objects.get(user=request.user)
        # print('no error 4')
        #
        # print('no error 5')
        # b.current_balance = (b.current_balance + amount)
        # b.save()
        print('no error 6')
        try:


            # if(not payment_address):
            DepositMoney.objects.create(user=request.user, amount=amount,
                                             payment_method = payment_method,
                                             payment_address = payment_address,
                                        payment_pending=True

                                             )
            print('no error 9')
            # messages.success(request, 'Your withdrawal request is sent to admin successfully')


        except Exception as e:
            print('exception #@@@ --',e)
            pass
        print('no error 9.5',payment_method,payment_address)

        return redirect('deposits_history')

        # return JsonResponse({'message': 'payment request successful'})
    else:
        return render(request,'dashboard/add_fund.html',{'bal':bal})

@login_required(login_url='/login/')
def franchise_deposit_request_rejected(request):
    if (not (request.user.staff == True and request.user.admin == True and request.user.is_active == True)):
        messages.error(request, 'You have not  admin access')
        return render(request, 'accounts/login.html', )
    all_users = DepositMoney.objects.filter(payment_pending=False,payment_approved=False,payment_rejected=True)#.exclude(user__email=request.user.email)
    print('all users data --',all_users)

    if len(all_users) == 0:
        return render(request, 'dashboard/franchise_request_deposit_rejected.html',
                      )
    users_data = []
    for req in all_users:
        name = str(req.user.first_name)+' '+str(req.user.last_name)
        email = req.user.email
        # country = req.user.country
        pending = req.payment_pending
        payment_method = None
        payment_address=None

        amount = req.amount
        if (req.payment_method):
            payment_method = req.payment_method
            payment_address = req.payment_address

        # print('users data @@ id  ',users_data,req.id)
        # users_data.append(
        #     {'name': name, 'email': email, 'amount': amount, 'payment_method': payment_method, 'id': req.id,
        #      'pending': pending,
        #      'payment_address': payment_address})
        obj = req
        # print('users data @@ id  ',users_data,req.id)
        users_data.append({'name': name, 'email': email, 'payment_method': payment_method, 'id': req.id,
             'pending': pending,'amount': amount,
             'payment_address': payment_address})
    print('all users data --', users_data)

    page = request.GET.get('page', 1)
    paginator = Paginator(users_data, 10)

    try:
        hist = paginator.page(page)
    except PageNotAnInteger:
        hist = paginator.page(1)
    except EmptyPage:
        hist = paginator.page(paginator.num_pages)

    return render(request, 'dashboard/franchise_request_deposit_rejected.html',  {'history': hist, })

@login_required(login_url='/login/')
def franchise_deposit_request_approved(request):
    if (not (request.user.staff == True and request.user.admin == True and request.user.is_active == True)):
        messages.error(request, 'You have not  admin access')
        return render(request, 'accounts/login.html', )
    all_users = DepositMoney.objects.filter(payment_approved=True)#.exclude(user__email=request.user.email)
    print('all users data --',all_users)

    if len(all_users) == 0:
        return render(request, 'dashboard/franchise_request_deposit_approved.html',
                      )
    users_data = []
    for req in all_users:
        name = str(req.user.first_name)+' '+str(req.user.last_name)
        email = req.user.email
        country = req.user.country
        pending = req.payment_pending
        payment_method = None
        payment_address = None

        amount = req.amount
        if (req.payment_method):
            payment_method = req.payment_method
            payment_address = req.payment_address

        # print('users data @@ id  ',users_data,req.id)
        # users_data.append(
        #     {'name': name, 'email': email, 'amount': amount, 'payment_method': payment_method, 'id': req.id,
        #      'pending': pending,
        #      'payment_address': payment_address})
        obj = req
        # print('users data @@ id  ',users_data,req.id)
        users_data.append({'name': name, 'email': email, 'payment_method': payment_method, 'id': req.user.id,
                           'pending': pending, 'amount': amount,
                           'payment_address': payment_address})


        # obj = req
        # print('users data @@ id  ',users_data,req.id)
        # users_data.append({'name': name, 'email': email, 'country': country.name,'id':req.user.id,'pending':pending})
    # print('all users data --', users_data)

    page = request.GET.get('page', 1)
    paginator = Paginator(users_data, 10)

    try:
        hist = paginator.page(page)
    except PageNotAnInteger:
        hist = paginator.page(1)
    except EmptyPage:
        hist = paginator.page(paginator.num_pages)
    return render(request, 'dashboard/franchise_request_deposit_approved.html',  {'history': hist, })








@login_required(login_url='/login/')
def franchise_request_rejected(request):
    if (not (request.user.staff == True and request.user.admin == True and request.user.is_active == True)):
        messages.error(request, 'You have not  admin access')
        return render(request, 'accounts/login.html', )
    all_users = FranchiseWithdraw.objects.filter(payment_pending=False,payment_approved=False,payment_rejected=True)#.exclude(user__email=request.user.email)
    print('all users data --',all_users)

    if len(all_users) == 0:
        return render(request, 'dashboard/franchise_request_rejected.html',
                      )
    users_data = []
    for req in all_users:
        name = str(req.user.first_name)+' '+str(req.user.last_name)
        email = req.user.email
        # country = req.user.country
        pending = req.payment_pending
        payment_method = None
        payment_address=None

        amount = req.amount
        if (req.payment_method):
            payment_method = req.payment_method
            payment_address = req.payment_address

        # print('users data @@ id  ',users_data,req.id)
        # users_data.append(
        #     {'name': name, 'email': email, 'amount': amount, 'payment_method': payment_method, 'id': req.id,
        #      'pending': pending,
        #      'payment_address': payment_address})
        obj = req
        # print('users data @@ id  ',users_data,req.id)
        users_data.append({'name': name, 'email': email, 'payment_method': payment_method, 'id': req.id,
             'pending': pending,'amount': amount,
             'payment_address': payment_address})
    print('all users data --', users_data)

    page = request.GET.get('page', 1)
    paginator = Paginator(users_data, 10)

    try:
        hist = paginator.page(page)
    except PageNotAnInteger:
        hist = paginator.page(1)
    except EmptyPage:
        hist = paginator.page(paginator.num_pages)

    return render(request, 'dashboard/franchise_request_rejected.html',  {'history': hist, })

@login_required(login_url='/login/')
def franchise_request_approved(request):
    if (not (request.user.staff == True and request.user.admin == True and request.user.is_active == True)):
        messages.error(request, 'You have not  admin access')
        return render(request, 'accounts/login.html', )
    all_users = FranchiseWithdraw.objects.filter(payment_approved=True)#.exclude(user__email=request.user.email)
    print('all users data --',all_users)

    if len(all_users) == 0:
        return render(request, 'dashboard/franchise_request_approved.html',
                      )
    users_data = []
    for req in all_users:
        name = str(req.user.first_name)+' '+str(req.user.last_name)
        email = req.user.email
        country = req.user.country
        pending = req.payment_pending
        payment_method = None
        payment_address = None

        amount = req.amount
        if (req.payment_method):
            payment_method = req.payment_method
            payment_address = req.payment_address

        # print('users data @@ id  ',users_data,req.id)
        # users_data.append(
        #     {'name': name, 'email': email, 'amount': amount, 'payment_method': payment_method, 'id': req.id,
        #      'pending': pending,
        #      'payment_address': payment_address})
        obj = req
        # print('users data @@ id  ',users_data,req.id)
        users_data.append({'name': name, 'email': email, 'payment_method': payment_method, 'id': req.user.id,
                           'pending': pending, 'amount': amount,
                           'payment_address': payment_address})


        # obj = req
        # print('users data @@ id  ',users_data,req.id)
        # users_data.append({'name': name, 'email': email, 'country': country.name,'id':req.user.id,'pending':pending})
    # print('all users data --', users_data)

    page = request.GET.get('page', 1)
    paginator = Paginator(users_data, 10)

    try:
        hist = paginator.page(page)
    except PageNotAnInteger:
        hist = paginator.page(1)
    except EmptyPage:
        hist = paginator.page(paginator.num_pages)
    return render(request, 'dashboard/franchise_request_approved.html',  {'history': hist, })


# @login_required(login_url='/login/')
# def dashboard(request):
#     if (request.user.staff == True and request.user.admin == True and request.user.is_active == True):
#         return redirect('admin_dashboard')
#     objs = PremiumPlan.objects.filter(user=request.user)
#     if (objs.exists() and objs.count() == 1):
#         obj = objs.first()
#         if (obj.plan == True):
#             exist = True
#         else:
#             return redirect('add_premium_plan')
#     else:
#         return redirect('add_premium_plan')

#     objs1 = PurchasedPackage.objects.filter(user=request.user)
#     for obj in objs1:
#         today_date = datetime.now().date()
#         end_date = obj.end_package
#         diff = end_date - today_date

#         diff = diff.days

#         if (diff == 0):
#             try:

#                 invest_obj = InvestmentPlans.objects.get(package=obj.investment_package.package)
#                 obj1 = PurchasedPackage.objects.filter(user=request.user, investment_package=invest_obj, )
#                 if (obj1.exists()):
#                     obj1.delete()
#             except Exception as e:

#                 print('exception when delete something --', e)
#                 partner_obj = PartnershipPlans.objects.get(package=obj.partnership_package.package)
#                 obj2 = PurchasedPackage.objects.filter(user=request.user, partnership_package=partner_obj, )
#                 if (obj2.exists()):
#                     obj2.delete()

#         # print('diff in days is ###', diff)

#     total_amount_of_packages = 0

#     highest_invest_package = 'none'
#     highest_partner_package = 'none'
#     pur_invest_packages=[]
#     pur_partner_packages=[]

#     objs = PurchasedPackage.objects.filter(user=request.user)
#     if (objs.exists()):
#         for ebj in objs:
#             total_amount_of_packages+=ebj.invest_amount
#             if (ebj.investment_package):
#                 pur_invest_packages.append(ebj.investment_package.package)
#             elif (ebj.partnership_package):
#                 pur_partner_packages.append(ebj.partnership_package.package)


#     invest={'starter':1,'silver':2,'gold':3,'platinum':4,'diamond':5,'titanium':6,'vip':7}
#     partner={'basic':1,'standard':2,'royal':3,}
#     new_pur_invest_packages = []
#     new_pur_partner_packages = []
#     for e in pur_invest_packages:
#         new_pur_invest_packages.append(invest[e])
#     for e1 in pur_partner_packages:
#         new_pur_partner_packages.append(partner[e1])
#     try:
#         high_invest = max(new_pur_invest_packages)

#     except:
#         high_invest='none'
#     try:
#         high_partner = max(new_pur_partner_packages)
#     except:
#         high_partner='none'


#     for k,v in invest.items():
#         if(v==high_invest):
#             highest_invest_package = str(k).title()

#     for k,v in partner.items():
#         if(v==high_partner):
#             highest_partner_package = str(k).title()



#     total_transfer_money = 0
#     all_sendmoney_data = send_money_history.objects.filter(sent_from=request.user)

#     for req in all_sendmoney_data:
#         total_transfer_money += req.sent_amount
#     # all_withdraw_data = withdraw_requests.objects.filter(user=request.user)
#     all_withdraw_data = FranchiseWithdraw.objects.filter(user=request.user,

#                                                          payment_approved=True,
#                                              )


#     total_withdraw_amount =0
#     total_deposit_amount = 0

#     for req in all_withdraw_data:

#         total_withdraw_amount += req.amount
#     all_deposit_data = deposit_history.objects.filter(user=request.user)

#     for req in all_deposit_data:
#         total_deposit_amount += req.amount



#     try:
#         total_deposit_amount = total_deposit_amount+request.user.daily_earnings
#     except:
#         pass

#     twithdraw = 0
#     obj = FranchiseWithdraw.objects.filter(user=request.user,payment_approved=True)
#     if (obj.exists()):
#         for ob in obj:
#             try:
#                 twithdraw+=float(ob.amount)
#             except:
#                 pass




#     obj = FranchiseWithdraw.objects.filter(user = request.user)
#     complete_withdraw = 0
#     pending_withdraw = 0
#     reject_withdraw = 0
#     if(obj.exists()):
#         complete_withdraw = obj.filter(payment_approved=True).count()

#         pending_withdraw = obj.filter(payment_pending=True).count()
#         reject_withdraw = obj.filter(payment_rejected=True).count()

#     try:
#         msg = AllUserNotice.objects.last().notice
#     except:
#         msg=''



#     all_withdraw_data = User.objects.filter(referral_id=request.user.referral_id)
#     all_withdraw_data = all_withdraw_data.exclude(email=request.user.email)
#     #refer_count = User.objects.filter(parent=request.user).count()
#     refer_count = User.objects.filter(parent_refer_id=request.user.referral_id).count()
#     # refer_count = all_withdraw_data.count()
#     objs = PurchasedPackage.objects.filter(user=request.user)
#     obj111 = User.objects.filter(email=request.user.email)
#     obj22=None
#     if(obj111.exists()):
#         obj22=obj111.first()
#     package_list = []
#     total_remaining_amount= 0
#     for obj in objs:
#         if (obj.investment_package):
#             last_benefit_d = obj.last_benefit_date
#             end_date       = obj.end_package
#             t_days_count   = 0
#             weekdays       = [5, 6]
#             for dt in daterange(datetime.today().date(), end_date):
#                 if dt.weekday() not in weekdays:  # to print only the weekdates
#                     t_days_count+=1
#             diff = end_date - datetime.today().date()
#             t_days = diff.days
#             t_days =t_days_count
#             pert = (obj.investment_package.daily_earn_per * obj.invest_amount)/100
#             print('pert %%%',pert)
#             t_amount  = round(t_days*pert,2)
#             datetime.today().date() - obj.package_start
#             total_remaining_amount+=t_amount
#             a = datetime.today().date()
#             b = last_benefit_d #+timedelta(days=1)

#             rem_days_count = 0
#             weekdays = [5, 6]
#             for dt in daterange(b, a):
#                 if dt.weekday() not in weekdays:  # to print only the weekdates
#                     # if (obj.investment_package.package.lower() != 'starter'):
#                     #     print(dt.strftime("%Y-%m-%d"))
#                     rem_days_count += 1

#             rem_days = (a-b).days
#             # print('rem days @@',rem_days)
#             # print('rem days _count @@',rem_days_count)
#             rem_days = rem_days_count


#             if(obj.last_benefit_date!=datetime.today().date() and rem_days>0):
#                 balss = balance.objects.filter(user= request.user)
#                 if(balss.exists()):
#                     objec = balss.first()
#                     cl = (obj.investment_package.daily_earn_per * obj.invest_amount)/100
#                     bonus_am = round(cl*rem_days,2)
#                     objec.current_balance += float(bonus_am)
#                     if(obj22):
#                         obj22.daily_earnings+=float(bonus_am)
#                         request.user.daily_earnings = round(obj22.daily_earnings,2)
#                         obj22.save()
#                     objec.save()
#                 obj.last_benefit_date = datetime.today().date()
#                 obj.save()
#             package_list.append(obj.investment_package.package)

#         elif (obj.partnership_package):
#             last_benefit_d = obj.last_benefit_date
#             end_date = obj.end_package
#             # diff = end_date - last_benefit_d

#             t_days_count = 0
#             weekdays = [5, 6]
#             for dt in daterange(datetime.today().date(), end_date):
#                 if dt.weekday() not in weekdays:  # to print only the weekdates
#                     # if (obj.investment_package.package.lower() != 'starter'):
#                     #     print(dt.strftime("%Y-%m-%d"))
#                     t_days_count += 1

#             diff = end_date - datetime.today().date()
#             t_days = diff.days
#             t_days = t_days_count
#             pert = (obj.partnership_package.daily_earn_per * obj.invest_amount) / 100
#             t_amount = round(t_days * pert, 2)
#             total_remaining_amount += t_amount

#             a = datetime.today().date()
#             b = last_benefit_d #+ timedelta(days=1)
#             rem_days_count = 0
#             weekdays = [5, 6]

#             for dt in daterange(b, a):
#                 if dt.weekday() not in weekdays:  # to print only the weekdates
#                     # if (obj.partnership_package.package.lower() != 'starter'):
#                     #     print(dt.strftime("%Y-%m-%d"))
#                     rem_days_count += 1

#             rem_days = (a - b).days
#             rem_days = rem_days_count

#             if (obj.last_benefit_date != datetime.today().date() and rem_days > 0):

#                 balss = balance.objects.filter(user=request.user)
#                 if (balss.exists()):
#                     objec = balss.first()
#                     cl = (obj.partnership_package.daily_earn_per * obj.invest_amount) / 100
#                     bonus_am = round(cl * rem_days, 2)
#                     # bonus_am = (obj.investment_package.daily_earn_per * obj.invest_amount)  100
#                     # bonus_am = round((obj.partnership_package.daily_earn_per * obj.invest_amount) / 100, 2)
#                     objec.current_balance += float(bonus_am)
#                     if (obj22):
#                         obj22.daily_earnings += float(bonus_am)
#                         request.user.daily_earnings = round(obj22.daily_earnings,2)
#                         obj22.save()
#                     objec.save()
#                 obj.last_benefit_date = datetime.today().date()
#                 obj.save()
#             package_list.append(obj.partnership_package.package)

    
#     objs = PremiumPlan.objects.filter(user=request.user)
#     exist = False
#     delete_package = []


#     try:
#         bal = balance.objects.get(user=request.user).current_balance
#         bal = round(bal, 2)
#     except:
#         bal = 0

#     total_active_adpacks = \
#     bought_adpack.objects.filter(Q(expiration_date__gt=datetime.now()) & Q(user=request.user)).aggregate(
#         total_act_ad=Sum('total_quantity'))['total_act_ad']

#     if total_active_adpacks == None:
#         total_active_adpacks = 0
#     total_referal = len(refer.objects.filter(referer=request.user.id))
#     # twithdraw = withdraw_requests.objects.filter(user=request.user).aggregate(s=Sum('amount'))['s']


#     return render(request, 'dashboard/dashboard.html',
#                   {'balance': bal, 'active_adpacks': total_active_adpacks, 'total_referal': total_referal,
#                   'total_withdraw': total_withdraw_amount,
#                   'total_deposit': total_deposit_amount,
#                   'refer_count':refer_count ,'msg':msg,
#                   'complete_withdraw':complete_withdraw,
#     'pending_withdraw':pending_withdraw,
#     'reject_withdraw':reject_withdraw,
#                   'total_withdraw_amount':total_withdraw_amount,
#     'total_deposit_amount' :total_deposit_amount,
#                   'total_transfer_money':total_transfer_money,
#                   'highest_partner_package':highest_partner_package,
#                   'highest_invest_package':highest_invest_package,
#                   'total_amount_of_packages':total_amount_of_packages,
#                   'total_remaining_amount':total_remaining_amount

#                   })







@login_required(login_url='/login/')
def dashboard(request):
    if (request.user.staff == True and request.user.admin == True and request.user.is_active == True):
        return redirect('admin_dashboard')
    objs = PremiumPlan.objects.filter(user=request.user)
    if (objs.exists() and objs.count() == 1):
        obj = objs.first()
        if (obj.plan == True):
            exist = True
        else:
            return redirect('add_premium_plan')
    else:
        return redirect('add_premium_plan')

    objs1 = PurchasedPackage.objects.filter(user=request.user)
    for obj in objs1:
        today_date = datetime.now().date()
        end_date = obj.end_package
        diff = end_date - today_date

        diff = diff.days

        if (diff == 0):
            try:

                invest_obj = InvestmentPlans.objects.get(package=obj.investment_package.package)
                obj1 = PurchasedPackage.objects.filter(user=request.user, investment_package=invest_obj, )
                if (obj1.exists()):
                    obj1.delete()
            except Exception as e:

                print('exception when delete something --', e)
                partner_obj = PartnershipPlans.objects.get(package=obj.partnership_package.package)
                obj2 = PurchasedPackage.objects.filter(user=request.user, partnership_package=partner_obj, )
                if (obj2.exists()):
                    obj2.delete()

        # print('diff in days is ###', diff)

    total_amount_of_packages = 0

    highest_invest_package = 'none'
    highest_partner_package = 'none'
    pur_invest_packages=[]
    pur_partner_packages=[]

    objs = PurchasedPackage.objects.filter(user=request.user)
    if (objs.exists()):
        for ebj in objs:
            total_amount_of_packages+=ebj.invest_amount
            if (ebj.investment_package):
                pur_invest_packages.append(ebj.investment_package.package)
            elif (ebj.partnership_package):
                pur_partner_packages.append(ebj.partnership_package.package)


    invest={'starter':1,'silver':2,'gold':3,'platinum':4,'diamond':5,'titanium':6,'vip':7}
    partner={'basic':1,'standard':2,'royal':3,}
    new_pur_invest_packages = []
    new_pur_partner_packages = []
    for e in pur_invest_packages:
        new_pur_invest_packages.append(invest[e])
    for e1 in pur_partner_packages:
        new_pur_partner_packages.append(partner[e1])
    try:
        high_invest = max(new_pur_invest_packages)
    except:
        high_invest='none'
    try:
        high_partner = max(new_pur_partner_packages)
    except:
        high_partner='none'


    for k,v in invest.items():
        if(v==high_invest):
            highest_invest_package = str(k).title()

    for k,v in partner.items():
        if(v==high_partner):
            highest_partner_package = str(k).title()



    total_transfer_money = 0
    all_sendmoney_data = send_money_history.objects.filter(sent_from=request.user)

    for req in all_sendmoney_data:
        total_transfer_money += req.sent_amount
    # all_withdraw_data = withdraw_requests.objects.filter(user=request.user)
    all_withdraw_data = FranchiseWithdraw.objects.filter(user=request.user,
                                                         payment_approved=True,
                                             )

    total_withdraw_amount =0
    total_deposit_amount = 0

    for req in all_withdraw_data:
        total_withdraw_amount += req.amount
    all_deposit_data = deposit_history.objects.filter(user=request.user)

    for req in all_deposit_data:
        total_deposit_amount += req.amount

    

    twithdraw = 0
    obj = FranchiseWithdraw.objects.filter(user=request.user,payment_approved=True)
    if (obj.exists()):
        for ob in obj:
            try:
                twithdraw+=float(ob.amount)
            except:
                pass




    obj = FranchiseWithdraw.objects.filter(user = request.user)
    complete_withdraw = 0
    pending_withdraw = 0
    reject_withdraw = 0
    if(obj.exists()):
        complete_withdraw = obj.filter(payment_approved=True).count()

        pending_withdraw = obj.filter(payment_pending=True).count()
        reject_withdraw = obj.filter(payment_rejected=True).count()

    try:
        msg = AllUserNotice.objects.last().notice
    except:
        msg=''



    all_withdraw_data = User.objects.filter(referral_id=request.user.referral_id)
    all_withdraw_data = all_withdraw_data.exclude(email=request.user.email)
    #refer_count = User.objects.filter(parent=request.user).count()
    refer_count = User.objects.filter(parent_refer_id=request.user.referral_id).count()
    # refer_count = all_withdraw_data.count()
    objs = PurchasedPackage.objects.filter(user=request.user)
    obj111 = User.objects.filter(email=request.user.email)
    obj22=None
    if(obj111.exists()):
        obj22=obj111.first()
    package_list = []
    total_remaining_amount= 0
    for obj in objs:
        if (obj.investment_package):
            last_benefit_d = obj.last_benefit_date
            end_date = obj.end_package
            print('last_benefit_d ######',last_benefit_d,end_date)
            a = datetime.today().date()#+timedelta(days=1)
            b = last_benefit_d  # +timedelta(days=1)
            rem_days_count = workdays(b, a)
            rem_days = rem_days_count
            print('rem days ####',rem_days)
            print('obj.last_benefit_days @@',obj.last_benefit_date,datetime.today().date())

            if ((last_benefit_d < datetime.today().date() and rem_days > 0 ) ):
                balss = balance.objects.filter(user=request.user)
                if (balss.exists()):
                    objec = balss.first()
                    cl = (obj.investment_package.daily_earn_per * obj.invest_amount) / 100
                    bonus_am = round(cl * rem_days, 2)
                    objec.current_balance += float(bonus_am)
                    if (obj22):
                        obj22.daily_earnings += float(bonus_am)
                        request.user.daily_earnings = round(obj22.daily_earnings, 2)
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
            if (obj.user.monthly_royality_last_date == None):
                obj22.monthly_royality_last_date = datetime.now().date()
            mon_date_obj = obj22.monthly_royality_last_date
            balss = balance.objects.filter(user=obj.user)
            cl = 0
            objec = None

            if (balss.exists()):
                objec = balss.first()
                cl = (obj.partnership_package.daily_earn_per * obj.invest_amount) / 100
                # print("mon_date_obj.month < datetime.today().month --",mon_date_obj.month, datetime.today().month)
                if (mon_date_obj.month < datetime.today().month):
                    cl_royal = (request.user.monthly_royality * obj.invest_amount) / 100
                    # print('cl_royal ##',cl_royal)
                    # print('request.user.monthly_royality_last_date before --',request.user.monthly_royality_last_date)
                    objec.current_balance += round(float(cl_royal), 2)
                    # print('daily ear --',obj22.daily_earnings)
                    obj22.daily_earnings += round(float(cl_royal), 2)
                    obj22.monthly_royality_last_date = datetime.today().date()
                    obj.save()
                    obj22.save()
                    objec.save()

            # if (obj.last_benefit_date != date_for_last_benefit and rem_days > 0):
            if ((last_benefit_d < datetime.today().date() and rem_days > 0)):
                if (balss.exists()):
                    bonus_am = round(cl * rem_days, 2)
                    # bonus_am = (obj.investment_package.daily_earn_per * obj.invest_amount)  100
                    # bonus_am = round((obj.partnership_package.daily_earn_per * obj.invest_amount) / 100, 2)
                    # print('daily bonus per--',cl,'amount--',bonus_am)
                    objec.current_balance += float(bonus_am)
                    if (obj22):
                        obj22.daily_earnings += float(bonus_am)
                        obj.user.daily_earnings = round(obj22.daily_earnings, 2)
                        obj22.save()
                    objec.save()

            obj.last_benefit_date = datetime.today().date()
            obj.save()
            obj22.save()
            objec.save()
            t_days_count = workdays(obj.last_benefit_date, end_date)
            pert = (obj.partnership_package.daily_earn_per * obj.invest_amount) / 100
            total_remaining_amount += round(t_days_count * pert, 2)
            package_list.append(obj.partnership_package.package)

    
    objs = PremiumPlan.objects.filter(user=request.user)
    exist = False
    delete_package = []


    try:
        bal = balance.objects.get(user=request.user).current_balance
        bal = round(bal, 2)
    except:
        bal = 0

    total_active_adpacks = \
    bought_adpack.objects.filter(Q(expiration_date__gt=datetime.now()) & Q(user=request.user)).aggregate(
        total_act_ad=Sum('total_quantity'))['total_act_ad']

    if total_active_adpacks == None:
        total_active_adpacks = 0
    total_referal = len(refer.objects.filter(referer=request.user.id))
    # twithdraw = withdraw_requests.objects.filter(user=request.user).aggregate(s=Sum('amount'))['s']
    
    obj111 = User.objects.filter(email=request.user.email)
    obj22_new = None
    if (obj111.exists()):
        obj22_new = obj111.first()

    try:
        total_deposit_amount = total_deposit_amount + obj22_new.daily_earnings
    except:
        pass


    return render(request, 'dashboard/dashboard.html',
                  {'balance': bal, 'active_adpacks': total_active_adpacks, 'total_referal': total_referal,
                   'total_withdraw': total_withdraw_amount,
                   'total_deposit': round(total_deposit_amount,2),
                   'refer_count':refer_count ,'msg':msg,
                   'complete_withdraw':complete_withdraw,
    'pending_withdraw':pending_withdraw,
    'reject_withdraw':reject_withdraw,
                   'total_withdraw_amount':total_withdraw_amount,
    'total_deposit_amount' :total_deposit_amount,
                   'total_transfer_money':total_transfer_money,
                   'highest_partner_package':highest_partner_package,
                   'highest_invest_package':highest_invest_package,
                   'total_amount_of_packages':total_amount_of_packages,
                   'total_remaining_amount':total_remaining_amount

                   })


@login_required(login_url='/login/')
def withdraw_request_premium(request):

    if request.method=='GET':
        amount = 15
        try:
            check=balance.objects.get(user=request.user).current_balance
        except:
            balance.objects.create(user=request.user)
            check = balance.objects.get(user=request.user).current_balance

        if amount>check:
            messages.info(request, 'not enough funds to pay activation fee')
            # return JsonResponse({'message':'not enough funds to activate premium plan'})
            return redirect('dashboard')
        try:
            amount_for_admin = 12
            obj1 = User.objects.get(admin=True, staff=True, is_active=True)
            b2 = balance.objects.get(user=obj1)
            b2.current_balance = (b2.current_balance + amount_for_admin)
            objd = User.objects.filter(username = request.user.parent_refer_id)
            if(objd.exists()):
                objd = objd.first()
            else:
                objd = None

            b2.save()
            # parent_user =request.user.parent

            b3 = balance.objects.get(user=objd)
            b3.current_balance = (b3.current_balance + 3)
            b3.save()
        except:
            pass

        try:
            b=balance.objects.get(user=request.user)
            b.current_balance=(b.current_balance-amount)
            b.save()
        except:
            balance.objects.create(user = request.user)
            b = balance.objects.get(user=request.user)
            b.current_balance = (b.current_balance - amount)
            b.save()

        obj = PremiumPlan.objects.filter(user=request.user)
        if(obj.exists()):
            obj = obj.first()
            obj.plan=True
            obj.save()
        else:
            PremiumPlan.objects.create(user=request.user, plan=True)
        messages.info(request, 'You paid activation fee successfully')
        return redirect('dashboard')
    else:
        messages.info(request, "you have not pay the activation fee")
        return redirect('add_premium_plan')




# @login_required(login_url='/login/')
# def withdraw_request_premium(request):
#     print('in withdraw_request_premium')
#     print("request.method",request.method)
#     if request.method=='GET':
#         amount = 15
#         try:
#             check=balance.objects.get(user=request.user).current_balance
#         except:
#             balance.objects.create(user=request.user)
#             check = balance.objects.get(user=request.user).current_balance

#         if amount>check:
#             messages.info(request, 'not enough funds to activate premium plan')
#             # return JsonResponse({'message':'not enough funds to activate premium plan'})
#             return redirect('dashboard')
#         try:
#             amount_for_admin = 12
#             obj1 = User.objects.get(admin=True, staff=True, is_active=True)
#             b2 = balance.objects.get(user=obj1)
#             b2.current_balance = (b2.current_balance + amount_for_admin)
#             b2.save()
#             parent_user =request.user.parent
#             b3 = balance.objects.get(user__referral_id = request.user.referral_id)
#             b3.current_balance = (b3.current_balance + 3)
#             b3.save()

#         except:
#             pass
#         try:
#             b=balance.objects.get(user=request.user)
#             b.current_balance=(b.current_balance-amount)
#             b.save()
#         except:
#             balance.objects.create(user = request.user)
#             b = balance.objects.get(user=request.user)
#             b.current_balance = (b.current_balance - amount)
#             b.save()

#         obj = PremiumPlan.objects.filter(user=request.user)
#         if(obj.exists()):
#             obj = obj.first()
#             obj.plan=True
#             obj.save()
#         else:
#             PremiumPlan.objects.create(user=request.user, plan=True)
#         messages.info(request, 'Your premium plan activated successfully')
#         return redirect('dashboard')

#         # return JsonResponse({'message':'Your premium plan activated successfully'})
#     else:
#         messages.info(request, 'Your premium plan not activated ')
#         return redirect('add_premium_plan')


@csrf_exempt
def premium_plan_success(request):
	if request.method=="POST":
		payee_account=request.POST['PAYEE_ACCOUNT']
		if payee_account == 'U29488895':
			objs = PremiumPlan.objects.filter(user=request.user)
			if (objs.exists() and objs.count() == 1):
				obj = objs.first()
				obj.user=request.user
				obj.plan=True
				obj.save()
			else:
				PremiumPlan.objects.create(user=request.user,plan=True)
			return render(request,'dashboard/add_premium_plan_successfully.html')
		else:
			HttpResponse('sorry,something went wrong')
	else:
		return HttpResponse('wrong destination')





@csrf_exempt
def payment_success(request):
    if request.method == "POST":
        payee_account = request.POST['PAYEE_ACCOUNT']
        if payee_account == 'U24170548':
            return render(request, 'dashboard/funding_success.html')
        else:
            HttpResponse('sorry,something went wrong')
    else:
        return HttpResponse('wrong destination')





@csrf_exempt
def payment_failed(request):
    if request.method == "POST":

        return render(request, 'dashboard/funding_failed.html')

    else:
        return HttpResponse('wrong destination')


# @login_required
# def add_fund(request):
#     exist = check_exist_or_not(request)


#     if request.session.has_key('order_number'):
#         del request.session['order_number']
#         del request.session['user_id']

#     user_id = request.user.id
#     order_number = random.randint(100, 999)
#     request.session['user_id'] = user_id
#     request.session['order_number'] = order_number
#     return render(request, 'dashboard/add_fund.html', {'user_id': user_id, 'order_number': order_number})


@login_required
def add_fund(request):
    exist = check_exist_or_not(request)


    if request.session.has_key('order_number'):
        del request.session['order_number']
        del request.session['user_id']

    user_id = request.user.id
    order_number = random.randint(100, 999)
    request.session['user_id'] = user_id
    request.session['order_number'] = order_number
    return render(request, 'dashboard/add_fund.html', {'user_id': user_id, 'order_number': order_number})

@csrf_exempt
def payment_status(request):
    if request.method == "POST":

        payee_account = request.POST['PAYEE_ACCOUNT']
        amount = float(request.POST['PAYMENT_AMOUNT'])
        payeer_account = request.POST['PAYER_ACCOUNT']
        order_number = request.POST['ORDER_NUM']
        user_id = request.POST['CUST_NUM']

        if payee_account == 'U29488895':
            usr = User.objects.get(id=int(user_id))
            balance.objects.create(user=request.user)
            try:
                bal = balance.objects.get(user=usr)
            except:
                balance.objects.create(user=request.user)
                bal = balance.objects.get(user=usr)

            amount_for_admin = round((5 * amount) / 100, 2)

            try:
                obj1 = User.objects.get(admin=True, staff=True, is_active=True)
                b2 = balance.objects.get(user=obj1)
                b2.current_balance = (b2.current_balance + amount_for_admin)
                b2.save()

            except:
                pass

            curr_bal = float(bal.current_balance)
            bal.current_balance = (curr_bal + amount - amount_for_admin)
            bal.save()
            deposit_history.objects.create(user=request.user, amount=amount)
            return HttpResponse('success')
        else:
            return HttpResponse('failed payment')
    else:
        return HttpResponse('failed')
@login_required(login_url='/login/')
def admin_balance_transfer(request):
    if (not (request.user.staff == True and request.user.admin == True and request.user.is_active == True)):
        messages.error(request, 'You have not  admin access')
        return render(request, 'accounts/login.html', )

    try:
        if request.method == 'POST':
            toemail = request.POST.get('toemail')
            amount = float(request.POST.get('amount'))
            userbalancedata = balance.objects.get(user=request.user)
            userbalance = userbalancedata.current_balance
            if amount > userbalance:
                messages.warning(request, "sorry you don't have enough funds")
                return redirect('admin_send_money')
            try:
                to = balance.objects.get(user__email=toemail)
                userbalancedata.current_balance = round(float(userbalancedata.current_balance - amount), 2)

                userbalancedata.save()
                to.current_balance = round(float(to.current_balance + amount), 2)
                to.save()

                send_money_history.objects.create(sent_from=request.user, sent_to=toemail, sent_amount=amount)
                messages.success(request, 'balance transfer successfully')
                return redirect('admin_send_money')
            except balance.DoesNotExist:
                messages.info(request, 'sorry! user does not exist')
                return redirect('admin_send_money')
    except:
        messages.info(request, 'sorry! some error occur')
        return redirect('admin_send_money')

@csrf_exempt
def cal_charge(request):
    if request.method == 'POST':
        # print('request post --', request.POST)
        # print('request body --', request.body)
        if request.is_ajax():
            data = request.POST
            # print('request post --',request.POST)
            # print('request body --',request.body)
            data = request.POST

            toemail = data['toemail']
            amount = float(data['amount'])
            userbalancedata = balance.objects.get(user=request.user)
            userbalance = userbalancedata.current_balance
            amount_for_admin = round((5 * amount) / 100, 2)

            if amount_for_admin:
                return JsonResponse({'is_valid': True,'amount':amount_for_admin+amount,'amount_for_admin':amount_for_admin,'toemail':toemail})
            return JsonResponse({'is_valid': False})
        raise Http404

@login_required(login_url='/login/')
def balance_transfer(request):
    exist = check_exist_or_not(request)
    if (not exist):
        return redirect('add_premium_plan')
    try:
        if request.method == 'POST':
            toemail = request.POST.get('toemail')
            amount = float(request.POST.get('amount'))
            amount_for_admin = float(request.POST.get('amount_for_admin'))

            userbalancedata = balance.objects.get(user=request.user)
            userbalance = userbalancedata.current_balance
            if amount > userbalance:
                messages.warning(request, 'sorry! dont have enough funds')
                return redirect('send_money')
            try:

                try:
                    obj1 = User.objects.filter(admin=True, staff=True, is_active=True).first()

                    b1 = balance.objects.get(user=obj1)
                    b1.current_balance = (b1.current_balance + amount_for_admin)

                    b1.save()
                except Exception as e:
                    print('Exception in balaance transfer func', e)
                    pass
                userbalancedata.current_balance = round(float(userbalancedata.current_balance - amount), 2)
                userbalancedata.save()
                to = balance.objects.get(user__email=toemail)

                to.current_balance = round(float(to.current_balance + (amount - amount_for_admin)), 2)
                to.save()
                send_money_history.objects.create(sent_from=request.user, sent_to=toemail, sent_amount=amount)
                messages.success(request, 'balance transfer successfully')
                return redirect('send_money')
            except balance.DoesNotExist:
                messages.info(request, 'sorry! user does not exist')
                return redirect('send_money')
    except:
        messages.info(request, 'sorry! some error occur')
        return redirect('send_money')


@login_required(login_url='/login/')

def adpack_list(request):
    exist = check_exist_or_not(request)
    if (not exist):
        return redirect('add_premium_plan')

    adp_list = adpack.objects.all()
    return render(request, 'dashboard/adpack-list.html', {'adp_list': adp_list, 'exist': exist})


@login_required(login_url='/login/')
def refer_page(request):
    exist = check_exist_or_not(request)
    if (not exist):
        return redirect('add_premium_plan')
    rfrid = request.user.referral_id
    # refered_user = refer.objects.filter(referer=int(usrid))
    return render(request, 'dashboard/refer.html', {'rfrid': rfrid})


@login_required(login_url='/login/')
def refer_list(request):
    exist = check_exist_or_not(request)
    if (not exist):
        return redirect('add_premium_plan')
    obj = User.objects.filter(referral_id=request.user.username)
    try:
        #all_withdraw_data = User.objects.filter(parent=obj.first())
        all_withdraw_data =  User.objects.filter(parent_refer_id=request.user.referral_id)
    except:
        all_withdraw_data=[]

    # all_withdraw_data = User.objects.filter(parent=request.user.referral_id)
    # all_withdraw_data = all_withdraw_data.exclude(email = request.user.email)
    if len(all_withdraw_data) == 0:
        return render(request, 'dashboard/refer_list.html',
                      {'message': 'you dont have any referral user data', 'exist': exist})

    withdraw_data = []

    for req in all_withdraw_data:
        name=''
        email=''
        country=''
        try:
            name  = req.first_name + ' '+req.last_name
        except:
            name = ''

        try:
            email  = req.email
        except:
            email = ''

        try:
            country = req.country
        except:
            country = ''

        withdraw_data.append({'name': name, 'email': email, 'country': country,
                              })

    page = request.GET.get('page', 1)
    paginator = Paginator(withdraw_data, 10)

    try:
        hist = paginator.page(page)
    except PageNotAnInteger:
        hist = paginator.page(1)
    except EmptyPage:
        hist = paginator.page(paginator.num_pages)

    return render(request, 'dashboard/refer_list.html', {'hist': hist, 'exist': exist})


    # usrid = request.user.id
    # refered_user = refer.objects.filter(referer=int(usrid))
    # return render(request, 'dashboard/refer_list.html', {'referdata': refered_user})


@login_required(login_url='/login/')
def buy_adpack(request, level):
    exist = check_exist_or_not(request)
    if (not exist):
        return redirect('add_premium_plan')


    if request.method == 'GET':
        adpdetails = adpack.objects.get(level=level)

        return render(request, 'dashboard/buy-adpack.html', {'adpack_details': adpdetails})

    if request.method == 'POST':
        level = request.POST['level']
        quantity = int(request.POST['quantity'])
        user = request.user

        adp = adpack.objects.get(level=int(level))
        total_price = round(float(adp.value * quantity), 2)
        total_revenue = round(float(adp.perday_revenue * 60 * quantity), 2)
        perday_revenue = round(float(adp.perday_revenue * quantity), 2)
        affiliate_commission = round(float(adp.affiliate_earn * quantity), 2)
        affiliate_id = refer.objects.get(user=request.user).referer
        expiration_date = datetime.now() + timedelta(days=60)
        bal = balance.objects.get(user=request.user).current_balance
        max_buy = int(adp.max_buy)
        recent_bought = []
        for i in range(0, int(level)):
            recent_bought.append(i)

        try:

            prev_max_buy = adpack.objects.get(level=int(recent_bought[-1])).max_buy

        except adpack.DoesNotExist:
            prev_max_buy = 0

        check = bought_adpack.objects.filter(Q(user=request.user) & Q(expiration_date__gt=datetime.now()) & Q(
            bought_adpacks__level=int(recent_bought[-1]))).aggregate(s=Sum('total_quantity'))['s']
        if check == None:
            check = 0

        check_max = bought_adpack.objects.filter(Q(user=request.user) & Q(expiration_date__gt=datetime.now()) & Q(
            bought_adpacks__level=int(level))).aggregate(s=Sum('total_quantity'))['s']

        if check_max == None:
            check_max = 0

        if bal < total_price:
            messages.info(request, 'insufficient fund')
            return redirect('buy_adpack', int(level))

        elif check < prev_max_buy and int(level) != 1:
            messages.warning(request, 'you can not buy before buying(max) previous level adpack')
            return redirect('buy_adpack', int(level))

        elif (max_buy - (check_max)) < quantity:
            string = 'you are allowed to buy only ' + str((max_buy - (check_max))) + ' more adpacks with this package'
            messages.error(request, string)
            return redirect('buy_adpack', int(level))
        else:
            usrbalance = balance.objects.get(user=request.user)
            usrbalance.current_balance = (usrbalance.current_balance) - total_price
            usrbalance.save()
            adpack_database = bought_adpack()
            adpack_database.user = request.user
            adpack_database.expiration_date = expiration_date
            adpack_database.buying_date = datetime.now()
            adpack_database.total_quantity = quantity
            adpack_database.bought_adpacks = adp
            adpack_database.adpack_totalreturn = total_revenue
            adpack_database.everyday_revenue = perday_revenue
            adpack_database.affiliate_commission = affiliate_commission
            adpack_database.total_price = total_price

            adpack_database.save()

            rupdate = refer.objects.get(user=request.user)
            adding_bal = balance.objects.get(user_id=affiliate_id)
            adding_bal.current_balance = round((float(adding_bal.current_balance) + affiliate_commission), 2)
            adding_bal.save()
            rupdate.refer_earn = round(float(rupdate.refer_earn + affiliate_commission), 2)
            rupdate.save()
            messages.success(request, 'successfully bought adpack')
            return redirect('buy_adpack', int(level))


@login_required(login_url='/login/')
def revenue_history(request):
    exist = check_exist_or_not(request)
    if (not exist):
        return redirect('add_premium_plan')

    sel_all_adpack = bought_adpack.objects.filter(user=request.user)
    if len(sel_all_adpack) == 0:
        return render(request, 'dashboard/revenue_history.html',
                      {'message': 'you dont have revenue history', 'exist': exist})
    history = []
    for pack in sel_all_adpack:
        updated_adp = adpack_update.objects.filter(bought_adpack_name_id=pack.id).aggregate(
            paid_rev=Sum('today_revenue'))
        paid_so_far = updated_adp['paid_rev']
        history.append({'pack': pack.bought_adpacks.title, 'buying_date': pack.buying_date,
                        'expiration_date': pack.expiration_date, 'total_paid': paid_so_far,
                        'total_quantity': pack.total_quantity})

    page = request.GET.get('page', 1)
    history.reverse()
    paginator = Paginator(history, 10)

    try:
        hist = paginator.page(page)
    except PageNotAnInteger:
        hist = paginator.page(1)
    except EmptyPage:
        hist = paginator.page(paginator.num_pages)
    return render(request, 'dashboard/revenue_history.html', {'history': hist, 'exist': exist})


'''
	try:
		hist=paginator.page(page)

    except PageNotAnInteger:

    	hist=paginator.page(1)

    except EmptyPage:

        hist=paginator.page(paginator.num_pages)

 '''


@login_required(login_url='/login/')
def adpack_history(request):
    exist = check_exist_or_not(request)
    if (not exist):
        return redirect('add_premium_plan')

    sel_all_adpack = bought_adpack.objects.filter(user=request.user).order_by('-buying_date')
    if len(sel_all_adpack) == 0:
        return render(request, 'dashboard/adpack_history.html',
                      {'message': 'you dont have adpack history', 'exist': exist})

    page = request.GET.get('page', 1)
    paginator = Paginator(sel_all_adpack, 10)

    try:
        hist = paginator.page(page)
    except PageNotAnInteger:
        hist = paginator.page(1)
    except EmptyPage:
        hist = paginator.page(paginator.num_pages)
    return render(request, 'dashboard/adpack_history.html', {'history': hist, 'exist': exist})

#
# class personal_info(generic.UpdateView):
#     model = User
#     fields = [ 'email', 'image','address','first_name','last_name','mobile' ]
#     template_name = 'dashboard/update-personal-info.html'
#     success_url = reverse_lazy('dashboard')
#
#     context_object_name = 'info'
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         exist = check_exist_or_not(self.request)
#         context['exist'] = exist
#         print('context in personal info ##', context)
#         return context
@login_required(login_url='/login/')
def personal_info(request):
    exist = check_exist_or_not(request)
    if (not exist):
        return redirect('add_premium_plan')
    if request.method=='POST':
        form = UserDetailChangeForm(request.POST,request.FILES,instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request,f'Your account has been updated successfully')
    else:
        form = UserDetailChangeForm(instance=request.user)
    return render(request,'dashboard/update-personal-info.html',{'form':form})




@login_required(login_url='/login/')
def payment_info(request):
    exist = check_exist_or_not(request)
    if (not exist):
        return redirect('add_premium_plan')

    pm_info = ''
    bank_info = ''
    agent_info = ''
    bkash_info = ''
    rocket_info = ''
    nagad_info = ''
    try:
        pm_info = pm_accounts.objects.get(user=request.user)
    except:
        added = False
    try:
        bank_info = bank_accounts.objects.get(user=request.user)
    except:
        added = False
    try:
        agent_info = agent_accounts.objects.get(user=request.user)
    except:
        added = False
    try:
        bkash_info = bkash_accounts.objects.get(user=request.user)
    except:
        added = False
    try:
        rocket_info = rocket_accounts.objects.get(user=request.user)
    except:
        added = False
    try:
        nagad_info = nagad_accounts.objects.get(user=request.user)
    except:
        added = False

    return render(request, 'dashboard/payment_info.html', {'pm_info': pm_info,
                                                           'bank_info': bank_info,
                                                           'agent_info': agent_info,
                                                           'bkash_info': bkash_info,
                                                           'rocket_info': rocket_info,
                                                           'nagad_info': nagad_info,
                                                           'exist': exist
                                                           })


@login_required(login_url='/login/')
def pm_add(request):
    exist = check_exist_or_not(request)
    if (not exist):
        return redirect('add_premium_plan')
    if request.method == 'POST':
        account = request.POST['pm_account']

        try:
            check = pm_accounts.objects.get(user=request.user)
            check.pm_account = account
            check.save()
            messages.info(request, 'payment information added successfully')
            return redirect('payment_info')

        except pm_accounts.DoesNotExist:
            pm_accounts.objects.create(user=request.user, pm_account=account)
            messages.info(request, 'payment information added successfully')
            return redirect('payment_info')


@login_required(login_url='/login/')
def agent_account_add(request):
    exist = check_exist_or_not(request)
    if (not exist):
        return redirect('add_premium_plan')
    if request.method == 'POST':
        account = request.POST['agent_email']

        try:
            check = agent_accounts.objects.get(user=request.user)
            check.agent_email = account
            check.save()
            messages.info(request, 'payment information added successfully')
            return redirect('payment_info')

        except agent_accounts.DoesNotExist:
            agent_accounts.objects.create(user=request.user, agent_email=account)
            messages.info(request, 'payment information added successfully')
            return redirect('payment_info')


@login_required(login_url='/login/')
def bank_info_add(request):
    exist = check_exist_or_not(request)
    if (not exist):
        return redirect('add_premium_plan')
    if request.method == 'POST':

        account_number = request.POST['bank_account_number']
        account_holder = request.POST['account_holder_name']
        bank_name = request.POST['bank_name']
        branch_name = request.POST['branch_name']
        ifsccode = request.POST['ifsccode']
        description = request.POST['description']

        try:
            check = bank_accounts.objects.get(user=request.user)
            check.account_holder_name = account_holder
            check.bank_name = bank_name
            check.account_number = account_number
            check.branch_name = branch_name
            check.ifsc_code = ifsccode
            check.description = description
            check.save()
            messages.info(request, 'payment information added successfully')
            return redirect('payment_info')

        except bank_accounts.DoesNotExist:
            bank_accounts.objects.create(user=request.user, account_holder_name=account_holder, bank_name=bank_name,
                                         branch_name=branch_name, ifsc_code=ifsccode, description=description)
            messages.info(request, 'payment information added successfully')
            return redirect('payment_info')


@login_required(login_url='/login/')
def bkash_add(request):
    exist = check_exist_or_not(request)
    if (not exist):
        return redirect('add_premium_plan')
    if request.method == 'POST':
        account = request.POST['bkash_account']

        try:
            check = bkash_accounts.objects.get(user=request.user)
            check.bkash_number = account
            check.save()
            messages.info(request, 'payment information added successfully')
            return redirect('payment_info')

        except bkash_accounts.DoesNotExist:
            bkash_accounts.objects.create(user=request.user, bkash_number=account)
            messages.info(request, 'payment information added successfully')
            return redirect('payment_info')


@login_required(login_url='/login/')
def rocket_add(request):
    exist = check_exist_or_not(request)
    if (not exist):
        return redirect('add_premium_plan')
    if request.method == 'POST':
        account = request.POST['rocket_account']

        try:
            check = rocket_accounts.objects.get(user=request.user)
            check.rocket_number = account
            check.save()
            messages.info(request, 'payment information added successfully')
            return redirect('payment_info')

        except rocket_accounts.DoesNotExist:
            rocket_accounts.objects.create(user=request.user, rocket_number=account)
            messages.info(request, 'payment information added successfully')
            return redirect('payment_info')


@login_required(login_url='/login/')
def nagad_add(request):
    exist = check_exist_or_not(request)
    if (not exist):
        return redirect('add_premium_plan')
    if request.method == 'POST':
        account = request.POST['nagad_account']

        try:
            check = nagad_accounts.objects.get(user=request.user)
            check.nagad_number = account
            check.save()
            messages.info(request, 'payment information added successfully')
            return redirect('payment_info')

        except nagad_accounts.DoesNotExist:
            nagad_accounts.objects.create(user=request.user, nagad_number=account)
            messages.info(request, 'payment information added successfully')
            return redirect('payment_info')

@login_required(login_url='/login/')
def withdraw(request):
    exist = check_exist_or_not(request)
    if (not exist):
        return redirect('add_premium_plan')
    if request.method == 'GET':
        try:
            obj = balance.objects.get(user=request.user)
            bal = obj.current_balance

            print('bal in try is --', bal)
        except:
            bal = 0
        return render(request, 'dashboard/withdraw.html',{'bal':bal})

@login_required(login_url='/login/')
def franchise_withdraw(request):
    exist = check_exist_or_not(request)
    if (not exist):
        return redirect('add_premium_plan')
    bal=0
    try:
        obj = balance.objects.get(user = request.user)
        bal = obj.current_balance
        print('bal in try is --',bal)
    except:
        bal = 0

    if(request.method=='POST'):
        password = request.POST.get('password')
        if(request.POST.get('country')!='bangladesh'):
            messages.error(request,'Franchise withdraw is not available in this country for you')
            return render(request, 'dashboard/franchise_withdraw.html',{'bal':str(bal)})
        if check_password(password, request.user.password) != True:
            messages.error(request,'password did not match')
            # return render(request, 'dashboard/withdraw.html',{'bal':bal})
            return render(request, 'dashboard/franchise_withdraw.html', {'bal': str(bal)})

        try:
            amount = float(request.POST['amount'])
        except:
            amount =0
        try:
            check = balance.objects.get(user=request.user).current_balance
        except:
            balance.objects.create(user=request.user)
            check = 0
            
        

        if amount > check or check<=0:
            # return JsonResponse({'message': 'not enough funds to withdraw'})
            messages.error(request,'not enough funds to withdraw')
            return render(request, 'dashboard/franchise_withdraw.html', {'bal': str(bal)})
            
        if(request.POST.get('country')=='bangladesh'):
            post_data = request.POST
            try:
                obj1 = balance.objects.get(user=request.user)
                print('current bal --',obj1.current_balance)
                obj1.current_balance = obj1.current_balance - amount
                bal = obj1.current_balance
                print('current bal --', obj1.current_balance)
                obj1.save()
            except:
                pass
            payment_method = None
            payment_address = None
            try:
                payment_through = post_data.get('payment_through')

                if(payment_through.strip().lower()=='online bank transfer'):
                    payment_method ='Franchise, '+str(post_data.get('bank_name')).strip().title()
                    payment_address = str(post_data.get('payee_details')).strip()
                    if(not str(post_data.get('bank_name')).strip().title() or not payment_address):
                        messages.error(request, 'Please fill details in online bank transfer option')
                        return render(request, 'dashboard/franchise_withdraw.html', {'bal': str(bal)})


                elif(payment_through.strip().lower()=='mobile banking'):
                    payment_method = 'Franchise, ' + str(post_data.get('mobile_banking_option')).strip().title()
                    payment_address = str(post_data.get('number_details')).strip()
                    if (not str(post_data.get('mobile_banking_option')).strip().title() or not payment_address):
                        messages.error(request, 'Please fill details in mobile banking option')
                        return render(request, 'dashboard/franchise_withdraw.html', {'bal': str(bal)})

            except:
                pass
            print('stepppp 111')
            print('user --',request.user)
            print('amount --',amount)
            FranchiseWithdraw.objects.create(user = request.user,amount = amount,payment_pending=True,payment_address=payment_address,payment_method=payment_method)
            print('stepppp 22222')
            messages.success(request, 'Your withdrawal request is sent to admin successfully')
            return render(request, 'dashboard/franchise_withdraw.html',{'bal':str(bal)})
    else:
        print('bal in else --',bal)
        return render(request, 'dashboard/franchise_withdraw.html',{'bal':str(bal)})



# @login_required(login_url='/login/')
# def withdraw_request(request):
#     exist = check_exist_or_not(request)
#     if (not exist):
#         return redirect('add_premium_plan')
#     if request.method == 'GET':
#         method = None
#         str_method = ''
#         via = request.GET['via']
#         amount = float(request.GET['amount'])
#         password = request.GET['password']

#         if via == 'pm':
#             method = pm_accounts
#             str_method = 'perfectMoney'
#         # elif via == 'bt':
#         #     method = bank_accounts
#         #     str_method = 'Bank transfer'
#         # elif via == 'at':
#         #     method = agent_accounts
#         #     str_method = 'agent transfer'
#         # elif via == 'bkash':
#         #     method = bkash_accounts
#         #     str_method = 'bkash transfer'
#         # elif via == 'rocket':
#         #     method = rocket_accounts
#         #     str_method = 'rocket transfer'
#         # elif via == 'nagad':
#         #     method = nagad_accounts
#         #     str_method = 'nagad transfer'
#         else:
#             method = None

#         check = balance.objects.get(user=request.user).current_balance
#         if amount > check:
#             return JsonResponse({'message': 'not enough funds to withdraw'})

#         # if amount < 100 and str_method == 'Bank transfer':
#         #     return JsonResponse({'message': 'minimum withdraw for bank is 100$'})
#         #
#         # if amount < 10 and str_method == 'agent transfer':
#         #     return JsonResponse({'message': 'minimum withdraw for agent transfer is 10$'})

#         if amount < 50 and str_method == 'perfectMoney':
#             return JsonResponse({'message': 'minimum withdraw for perfectMoney is 50$'})
#         # if amount < 15 and (
#         #         str_method == 'bkash transfer' or str_method == 'rocket transfer' or str_method == 'nagad transfer'):
#         #     return JsonResponse({'message': 'minimum withdraw for mobile bank is 15$'})

#         if check_password(password, request.user.password) != True:
#             return JsonResponse({'message': 'password did not match'})

#         try:
#             method.objects.get(user=request.user)
#         except method.DoesNotExist:
#             return JsonResponse({'message': 'payment account is not added'})

#         b = balance.objects.get(user=request.user)
#         amount_for_admin = round((10 * amount) / 100, 2)
#         b.current_balance = (b.current_balance - amount)
#         b.save()
#         try:
#             obj1 = User.objects.get(admin=True, staff=True, is_active=True)
#             b1 = balance.objects.get(user=obj1)
#             b1.current_balance = (b1.current_balance + amount_for_admin)
#             b1.save()
#             FranchiseWithdraw.objects.create(user=request.user, amount=amount, payment_pending=True,payment_method=str_method)
#             # messages.success(request, 'Your withdrawal request is sent to admin successfully')


#         except:
#             pass

#         withdraw_requests.objects.create(
#             user=request.user,
#             method=str_method,
#             amount=amount - amount_for_admin,
#             payment_done=True)

#         # return redirect('withdraw_history')

#         return JsonResponse({'message': 'payment request successful'})


@login_required(login_url='/login/')
def withdraw_request(request):
    exist = check_exist_or_not(request)
    if (not exist):
        return redirect('add_premium_plan')
    print('get --',request.GET)
    print('post --',request.POST)
    
    
    
    
    kyc_not_done=False
    obb = KycVerification.objects.filter(user= request.user)
    if(obb.exists()):
        obb  = obb.first()
        if(obb.approved==False):
            # messages.error(request, 'sorry! you cannot withdraw money because your KYC is not done')
            kyc_not_done=True
            return render(request, 'dashboard/withdraw.html', {'kyc_not_done':kyc_not_done})
    else:
        # messages.error(request, 'sorry! you cannot withdraw money because your KYC is not done')
        kyc_not_done=True
        return render(request, 'dashboard/withdraw.html', {'kyc_not_done':kyc_not_done})
    
    try:
        obj = balance.objects.get(user=request.user)
        bal = obj.current_balance

        print('bal in try is --', bal)
    except:
        bal = 0
    data= request.POST
    if request.method == 'POST':
        # method = None

        payment_method = data.get('method')
        payment_address = data.get('payment_address_input')
        try:
            amount = float(data.get('amount'))
        except:
            amount=0
        password = data.get('password')
        print('no error ')

        # if via == 'pm':
        #     method = pm_accounts
        #     str_method = 'perfectMoney'
        # elif via == 'bt':
        #     method = bank_accounts
        #     str_method = 'Bank transfer'
        # elif via == 'at':
        #     method = agent_accounts
        #     str_method = 'agent transfer'
        # elif via == 'bkash':
        #     method = bkash_accounts
        #     str_method = 'bkash transfer'
        # elif via == 'rocket':
        #     method = rocket_accounts
        #     str_method = 'rocket transfer'
        # elif via == 'nagad':
        #     method = nagad_accounts
        #     str_method = 'nagad transfer'
        # else:
        #     method = None

        check = balance.objects.get(user=request.user).current_balance
        if amount > check:
            # return JsonResponse({'message': 'not enough funds to withdraw'})
            messages.error(request,'not enough funds to withdraw')
            return render(request, 'dashboard/withdraw.html',{'bal':bal})
        print('no error 2')

        # if amount < 100 and str_method == 'Bank transfer':
        #     return JsonResponse({'message': 'minimum withdraw for bank is 100$'})
        #
        # if amount < 10 and str_method == 'agent transfer':
        #     return JsonResponse({'message': 'minimum withdraw for agent transfer is 10$'})

        # if amount < 50 and str_method == 'perfectMoney':
        #     return JsonResponse({'message': 'minimum withdraw for perfectMoney is 50$'})
        # if amount < 15 and (
        #         str_method == 'bkash transfer' or str_method == 'rocket transfer' or str_method == 'nagad transfer'):
        #     return JsonResponse({'message': 'minimum withdraw for mobile bank is 15$'})

        if check_password(password, request.user.password) != True:
            messages.error(request,'password did not match')
            return render(request, 'dashboard/withdraw.html',{'bal':bal})
            # return JsonResponse({'message': 'password did not match'})
        print('no error 3')

        # try:
        #     method.objects.get(user=request.user)
        # except method.DoesNotExist:
        #     return JsonResponse({'message': 'payment account is not added'})

        b = balance.objects.get(user=request.user)
        print('no error 4')
        amount_for_admin = round((10 * amount) / 100, 2)
        print('no error 5')
        b.current_balance = (b.current_balance - amount)
        b.save()
        print('no error 6')
        try:
            obj1 = User.objects.get(admin=True, staff=True, is_active=True)
            try:
                b1 = balance.objects.get(user=obj1)
            except:
                b1 = balance.objects.create(user=obj1)
            print('no error 7')
            b1.current_balance = (b1.current_balance + amount_for_admin)
            print('no error 8')
            b1.save()
            # if(not payment_address):
            FranchiseWithdraw.objects.create(user=request.user, amount=amount, payment_pending=True,
                                             payment_method = payment_method,
                                             payment_address = payment_address
                                             )
            print('no error 9')
            # messages.success(request, 'Your withdrawal request is sent to admin successfully')


        except Exception as e:
            print('exception #@@@ --',e)
            pass
        print('no error 9.5',payment_method,payment_address)
        if(payment_address):


            withdraw_requests.objects.create(
                user=request.user,
                method=payment_method,
                payment_pending=True,
                amount=amount - amount_for_admin,
                payment_done=True,
                payment_address=payment_address,
            )
        print('no error 10')

        return redirect('withdraw_history')

        # return JsonResponse({'message': 'payment request successful'})
    else:
        return render(request,'dashboard/withdraw.html',{'bal':bal})

@login_required(login_url='/login/')
def change_password(request):
    exist = check_exist_or_not(request)
    if (not exist):
        return redirect('add_premium_plan')
    exist = check_exist_or_not(request)

    if request.method == 'GET':
        return render(request, 'dashboard/change-password.html', {'exist': exist})

    if request.method == 'POST':
        curr = request.POST['current_pass']
        new = request.POST['new_pass1']
        con = request.POST['new_pass2']

        if check_password(curr, request.user.password) == False:
            messages.info(request, 'current password is not correct')
            return redirect('change_password')

        if new != con:
            messages.info(request, 'password did not match')
            return redirect('change_password')

        u = User.objects.get(email=request.user.email)
        u.set_password(new)
        u.save()
        messages.info(request, 'password has changed successfully')

        return redirect('change_password')

@login_required(login_url='/login/')
def withdraw_history(request):
    exist = check_exist_or_not(request)
    if (not exist):
        return redirect('add_premium_plan')
    exist=False

    all_withdraw_data = FranchiseWithdraw.objects.filter(user=request.user)
    record=False
    if len(all_withdraw_data) == 0:
        return render(request, 'dashboard/withdraw-history.html',
                      {'message': 'you dont have any withdraw request', 'exist': exist,'record':record})

    withdraw_data = []

    for req in all_withdraw_data:
        record=True
        status = None
        name = req.user.first_name
        date = req.date
        amount = req.amount
        method = req.payment_method
        payment_address = req.payment_address
        try:
            if(req.payment_approved):
                status='approved'
            elif(req.payment_pending):
                status='pending'
            elif(req.payment_rejected):
                status = 'rejected'
        except:
            pass

        # payment_done = req.payment_done
        # payment_error = req.payment_error
        withdraw_data.append({
                            'name':name,
                            'date': date,
                              'amount': amount,
                              'method': method,
                              'payment_address': payment_address,
                              'status': status,
            'record':record
                              })

    page = request.GET.get('page', 1)
    paginator = Paginator(withdraw_data, 10)

    try:
        hist = paginator.page(page)
    except PageNotAnInteger:
        hist = paginator.page(1)
    except EmptyPage:
        hist = paginator.page(paginator.num_pages)

    return render(request, 'dashboard/withdraw-history.html', {'hist': hist, 'exist': exist,'record':record})


@login_required(login_url='/login/')
def deposits_history(request):
    exist = check_exist_or_not(request)
    if (not exist):
        return redirect('add_premium_plan')
    exist=False
    all_deposit_data = DepositMoney.objects.filter(user=request.user)
    record= False

    if len(all_deposit_data) == 0:
        return render(request, 'dashboard/deposit-history.html',
                      {'message': 'you dont have any deposit record', 'exist': exist,'record':record})

    deposit_data = []

    for req in all_deposit_data:
        record = True
        status = None
        name = req.user.first_name
        date = req.date
        amount = req.amount
        method = req.payment_method
        payment_address = req.payment_address
        try:
            if (req.payment_approved):
                status = 'approved'
            elif (req.payment_pending):
                status = 'pending'
            elif (req.payment_rejected):
                status = 'rejected'
        except:
            pass

        deposit_data.append({
            'name': name,
            'date': date,
            'amount': amount,
            'method': method,
            'payment_address': payment_address,
            'status': status,
            'record': record
        })
    page = request.GET.get('page', 1)
    paginator = Paginator(deposit_data, 10)
    try:
        hist = paginator.page(page)
    except PageNotAnInteger:
        hist = paginator.page(1)
    except EmptyPage:
        hist = paginator.page(paginator.num_pages)
    return render(request, 'dashboard/deposit-history.html', {'hist': hist, 'exist': exist,'record':record})

@login_required(login_url='/login/')
def send_Money_history(request):
    exist = check_exist_or_not(request)
    if (not exist):
        return redirect('add_premium_plan')
    exist=False

    all_sendmoney_data = send_money_history.objects.filter(sent_from=request.user).order_by('-date')

    if len(all_sendmoney_data) == 0:
        return render(request, 'dashboard/sendmoney_history.html',
                      {'message': 'you dont have any send record', 'exist': exist})

    sendmoney_data = []

    for req in all_sendmoney_data:
        date = req.date
        amount = req.sent_amount
        reciever = req.sent_to

        sendmoney_data.append({'date': date, 'amount': amount, 'reciever': reciever})

    page = request.GET.get('page', 1)
    paginator = Paginator(sendmoney_data, 10)

    try:
        hist = paginator.page(page)
    except PageNotAnInteger:
        hist = paginator.page(1)
    except EmptyPage:
        hist = paginator.page(paginator.num_pages)

    return render(request, 'dashboard/sendmoney_history.html', {'history': hist, 'exist': exist})


@login_required(login_url='/login/')
def receivedmoney_history(request):
    exist = check_exist_or_not(request)
    if (not exist):
        return redirect('add_premium_plan')
    exist=False

    all_receivedmoney_data = send_money_history.objects.filter(sent_to=request.user.email).order_by('-date')

    if len(all_receivedmoney_data) == 0:
        return render(request, 'dashboard/received_money_history.html', {'message': 'you dont have any received record',
                                                                         'exist': exist})

    receivedmoney_data = []

    for req in all_receivedmoney_data:
        date = req.date
        amount = req.sent_amount
        sender = req.sent_from.email

        receivedmoney_data.append({'date': date, 'amount': amount, 'sender': sender})

    page = request.GET.get('page', 1)
    paginator = Paginator(receivedmoney_data, 10)

    try:
        hist = paginator.page(page)
    except PageNotAnInteger:
        hist = paginator.page(1)
    except EmptyPage:
        hist = paginator.page(paginator.num_pages)

    return render(request, 'dashboard/received_money_history.html', {'history': hist, 'exist': exist})

def admin_send_money(request):
    if (not (request.user.staff == True and request.user.admin == True and request.user.is_active == True)):
        messages.error(request, 'You have not  admin access')
        return render(request, 'accounts/login.html', )

    return render(request, 'dashboard/admin-send-fund.html',)


def send_money(request):
    exist = check_exist_or_not(request)
    if (not exist):
        return redirect('add_premium_plan')
    exist=False

    return render(request, 'dashboard/send-fund.html', {'exist': exist})


def payment_gateway(request):
    exist = check_exist_or_not(request)
    if (not exist):
        return redirect('add_premium_plan')
    exist=False
    return render(request, 'dashboard/payment_gateway.html', {'exist': exist})


