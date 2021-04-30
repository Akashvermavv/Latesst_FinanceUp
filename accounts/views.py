from django.shortcuts import render
from datetime import datetime, timedelta
from django.http import HttpResponse
from django.shortcuts import render,redirect
from django.contrib.auth import login,authenticate,logout,get_user_model
from django.utils.http import is_safe_url
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import CreateView,FormView,DetailView,View,UpdateView
from django.views.generic.edit import FormMixin
from django.urls import reverse
from django.contrib import  messages
from django.utils.safestring import mark_safe
from financeup.mixins import NextUrlMixin,RequestFormAttachMixin
from . forms import LoginForm,RegisterForm,GuestForm,ReactivateEmailForm,UserDetailChangeForm
#,UserProfileForm
import json


from django.contrib import auth
from .models import GuestEmail,EmailActivation,User
from dashboard.models import balance,PurchasedPackage,InvestmentPlans
# from social_django.models import UserSocialAuth
from .signals import user_logged_in


# @login_required  # /accounts/login/?next=/some/path
# def account_home_view(request):
#     return render(request,"accounts/home.html",{})

# class LoginRequiredMixin(object):
#     @method_decorator(login_required)
#     def dispatch(self, request, *args, **kwargs):
#         return super(LoginRequiredMixin,self).dispatch(request,*args, **kwargs)

# LoginRequiredMixin,


class AccountHomeView(LoginRequiredMixin,DetailView):
    template_name = 'accounts/home.html'
    def get_object(self, queryset=None):
        return self.request.user

    # @method_decorator(login_required)
    # def dispatch(self,  *args, **kwargs):
    #     return super(AccountHomeView,self).dispatch(*args, **kwargs)

class AccountEmailActivateView(FormMixin,View):
    success_url = '/login/'
    form_class = ReactivateEmailForm
    def get(self,request,key=None,*args,**kwargs):
        self.key = key
        if key is not None:
            qs = EmailActivation.objects.filter(key__iexact=key)
            confirm_qs = qs.confirmable()
            if confirm_qs.count()==1:
                obj = confirm_qs.first()
                obj.activate()
                messages.success(request,"Your email has been confirmed. Please login. ")
                return redirect("login")
            else:
                activated_qs = qs.filter(activated= True)
                if activated_qs.exists():
                    reset_link = reverse("password_reset")
                    msg ="""Your email has already been confirmed Do you need to <a href="{link}"> reset your password </a>?""".format(
                        link = reset_link
                    )
                    messages.success(request,mark_safe(msg))
                    return redirect("login")

            # if activated
            # return redirect
            # if already activated
            # return redirect
            # if error
        context ={'form':self.get_form(),'key':key}
        return render(request,'registration/activation-error.html',context)

    def post(self,request,*args,**kwargs):
        print('post data --',request.POST)
        # create form to receive an email
        form = self.get_form()
        print('in post form  is valid --',form.is_valid())
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self,form):
        msg="""  Activation link sent, please check your email."""
        request = self.request
        messages.success(request,msg)
        email = form.cleaned_data.get("email")
        obj = EmailActivation.objects.email_exists(email).first()
        user = obj.user
        new_activation = EmailActivation.objects.create(user=user,email=email)
        new_activation.send_activation()
        return super(AccountEmailActivateView,self).form_valid(form)

    def form_invalid(self,form):
        context = {'form':form,"key":self.key}
        return render(self.request,'registration/activation-error.html',context)



def guest_register_view(request):
    form = GuestForm(request.POST or None)

    context ={
        "form":form
    }
    next_ = request.GET.get('next')
    next_post = request.POST.get('next')
    redirect_path = next_ or next_post or None

    if form.is_valid():
        email = form.cleaned_data.get("email")
        print('email in guest_register_view -->',email)
        new_guest_email = GuestEmail.objects.create(email=email)
        request.session['guest_email_id'] = new_guest_email.id

        if is_safe_url(redirect_path,request.get_host()):
            return redirect(redirect_path)
        else:
            return redirect("/register/")
    return redirect("/register/")


class GuestRegisterView(NextUrlMixin,RequestFormAttachMixin,FormView):
    form_class = GuestForm
    default_next = '/register/'

    def get_success_url(self):
        return self.get_next_url()

    def form_invalid(self, form):
        return redirect(self.default_next)

    def form_valid(self, form):
        request = self.request
        email = form.cleaned_data.get('email')
        new_guest_email = GuestEmail.objects.create(email=email)
        request.session['guest_email_id'] = new_guest_email.id
        return redirect(self.get_next_url())



# def login_view(request):
#     form = LoginForm(request=request)




class LoginView(NextUrlMixin,RequestFormAttachMixin,FormView):
    form_class = LoginForm
    success_url = '/dashboard/'
    template_name = 'accounts/login.html'
    default_next ='/'


    def form_valid(self, form):
        next_path = self.get_next_url()
        request = self.request
        if (request.user.staff == True  and request.user.is_active == True):
            return redirect('admin_dashboard')
        return redirect('dashboard')

    success_message = 'Welcome to the dashboard'


class RegisterView(CreateView):
    form_class = RegisterForm
    template_name = 'accounts/register.html'
    success_url = '/login/'


class UserDetailUpdateView(LoginRequiredMixin,UpdateView):
    form_class = UserDetailChangeForm
    template_name = 'accounts/detail-update-view.html'

    def get_object(self, queryset=None):
        print('queryset in UserDetailUpdateView ',queryset)
        return self.request.user

    def get_context_data(self,**kwargs):
        context = super(UserDetailUpdateView, self).get_context_data(**kwargs)
        context['title'] = 'Change Your Account Details'
        return context

    def get_success_url(self):
        return reverse("account:home")


# User = get_user_model()
def register_page(request):
    print('in register page method is ',request.method)
    form = RegisterForm()
    if request.method=='POST':
        form =RegisterForm(request.POST,request.FILES or None)
        # form_1 = UserProfileForm(request.POST, request.FILES)
        # print('dir(form)--',dir(form))
        # print('user is auth or not --',request.user.is_authenticated)
        # print('post data --',request.POST)
        # print('post data --',request.FILES)
        # print('form1 user --', form_1.user)
        # print('form is valid or not --',form.is_valid())
        if form.is_valid():
            import requests
            response = request.POST['g-recaptcha-response']
            secret_key = '6LdVsPEUAAAAABucQvaYu3TSb20v1ynbq8gJUokK'

            sending_request = requests.post('https://www.google.com/recaptcha/api/siteverify',
                                            data={'response': response, 'secret': secret_key})
            status = json.loads(sending_request.text)['success']

            if status == False:
                return render(request, 'accounts/register.html', {'form': form, 'captcha': 'false'})


            print('### user --',request.user.id)

            messages.success(request,'Account Created Successfully Please check your email '+request.POST.get('email')+ ' for activate your account.',)
            print('cleaned data --',form.cleaned_data)
            obj = User.objects.filter(email=form.cleaned_data['email'])
            form.save()
            print('obj ##',obj.exists())

            if(obj.exists()):
                balance.objects.create(user=obj.first())
                
            obj1 = InvestmentPlans.objects.filter(package='starter').first()
            initial = obj1.invest_start
            final = obj1.invest_end
            start_date = datetime.now().date()
            days = obj1.total_days
            end_date = start_date + timedelta(days=4000)
            PurchasedPackage.objects.create(user=obj.first(), investment_package=obj1,end_package=end_date,invest_amount=0,package_start=start_date
                                            )

            
            # refer.objects.create(user=create_user, referer=referer_id)
            # sendConfirm(create_user)
            return render(request, 'accounts/activation.html')
            # return redirect('login')
        else:


            context = {
                'form': form,

            }
            print('form erros ###',form.errors)
            # messages.error(request,'Please provide a valid referral id or placement id')
            return render(request, "accounts/register.html",context)


    form = RegisterForm()

    context = {
        'form': form,

    }
    return render(request,"accounts/register.html",context)


def logout(request):
    auth.logout(request)
    return redirect('/')
