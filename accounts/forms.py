from django import forms
from django.urls import reverse
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from .models import EmailActivation
from django.utils.safestring import mark_safe
from django.contrib.auth import login,authenticate,logout,get_user_model
from .signals import user_logged_in
from .models import GuestEmail,User
from phonenumber_field.formfields import PhoneNumberField
from django_countries.fields import CountryField
from django_countries import countries

COUNTRIES = tuple(countries)


#UserProfile

# User = get_user_model()


# class UserProfileForm(forms.ModelForm):
#     user = forms.EmailField(widget=forms.HiddenInput())
#     class Meta:
#         model = UserProfile
#         fields = ('image','user')
#
#     def save(self, commit=True,email=None):
#         # Save the provided password in hashed format
#         obj = super(UserProfileForm, self).save(commit=False)
#         obj.user= email
#         if commit:
#             obj.save()
#         return obj



class ReactivateEmailForm(forms.Form):
    email = forms.EmailField()

    def clean_email(self):
        email = self.cleaned_data.get('email')
        qs = EmailActivation.objects.email_exists(email)
        if not qs.exists():
            register_link = reverse("register")
            msg = """This email does not exists, would you like to  <a href="{link}"> register? </a>?""".format(
                link=register_link
            )
            raise forms.ValidationError(mark_safe(msg))
        return email


class UserAdminCreationForm(forms.ModelForm):
    """
    A form for creating new users. Includes all the required
    fields, plus a repeated password.
    """
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('email','full_name')  # 'full_name'

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(UserAdminCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserDetailChangeForm(forms.ModelForm):

    first_name = forms.CharField(max_length=25, required=True, widget=forms.TextInput(
        attrs={'class': 'form-control', 'id': 'firstName', 'placeholder': 'First Name'}))
    last_name = forms.CharField(max_length=25, required=True, widget=forms.TextInput(
        attrs={'class': 'form-control', 'id': 'lastName', 'placeholder': 'Last Name'}))
    email = forms.EmailField(max_length=35, required=False,widget=forms.TextInput(
        attrs={'class': 'form-control', 'id': 'emailAddress', 'placeholder': 'Email','readonly' : 'true'}))
    referral_id = forms.CharField(label='Referral Id',max_length=45, required=False, widget=forms.TextInput(
        attrs={'class': 'form-control', 'id': 'address','readonly': 'true' }))
    user_id = forms.IntegerField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control', 'id': 'user_id', 'placeholder': 'User_id ID', 'readonly': 'true'}))
    mobile = PhoneNumberField(max_length=16, required=True, widget=forms.TextInput(
        attrs={'class': 'form-control', 'id': 'mobile', 'placeholder': 'Mobile'}))
    address = forms.CharField(max_length=45, required=True, widget=forms.TextInput(
        attrs={'class': 'form-control', 'id': 'address', 'placeholder': 'Address'}))
    country = forms.ChoiceField(label="Select your country", choices=COUNTRIES, required=True,
                                widget=forms.Select(attrs={'class': 'form-control country', 'id': None}))

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name','referral_id','user_id', 'mobile', 'address', 'country',
                  'image')  # 'full_name'

class UserAdminChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = ('email','full_name', 'password','is_active', 'admin')

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]







# class GuestForm(forms.Form):
    # email = forms.EmailField()


class GuestForm(forms.ModelForm):
    class Meta:
        model = GuestEmail
        fields =[
            'email',
        ]

    def __init__(self,request,*args,**kwargs):
        self.request  = request
        super(GuestForm,self).__init__(*args,**kwargs)

    def save(self,commit=True):
        obj = super(GuestForm, self).save(commit=False)
        if commit:
            obj.save()
            request = self.request
            request.session['guest_email_id'] = obj.id
        return obj


class LoginForm(forms.Form):
    # username = forms.CharField()
    email = forms.CharField(label='',widget=forms.TextInput(attrs={"class":'form-control',"placeholder":"Email or Username"}))
    password = forms.CharField(label='',widget=forms.PasswordInput(attrs={"class":'form-control',"placeholder":"Password"}),)

    def __init__(self,request,*args,**kwargs):
        self.request = request
        super(LoginForm, self).__init__(*args,**kwargs)

    def clean(self):
        request = self.request
        data = self.cleaned_data
        email = data.get("email")
        password = data.get("password")

        qs = User.objects.filter(email=email)
        if qs.exists():
            # user email is registered, check active/
            not_active = qs.filter(is_active=False)
            if not_active.exists():
                ## not active, check email activation
                link = reverse("account:resend-activation")
                reconfirm_msg= f"""Go to <a href ='{link}'>resend confirmation email </a>."""

                confirm_email = EmailActivation.objects.filter(email=email)
                is_confirmable = confirm_email.confirmable().exists()
                if is_confirmable:
                    msg1 = f"Please check your email to confirm your account or "+reconfirm_msg.lower()
                    raise forms.ValidationError(mark_safe(msg1))
                email_confirm_exists = EmailActivation.objects.email_exists(email).exists()
                if email_confirm_exists:
                    msg2 = "Email not confirmed. "+reconfirm_msg
                    raise forms.ValidationError(mark_safe(msg2))
                if not is_confirmable and not email_confirm_exists:
                    raise forms.ValidationError("This user is inactive.")

        user = authenticate(request,username = email,password=password)
        if user is None:
            raise forms.ValidationError("Invalid credentials")
        login(request,user)
        self.user = user
        user_logged_in.send(user.__class__, instance=user, request=request)
        try:
            del request.session['guest_email_id']
        except:
            pass
        return data


    # def form_valid(self, form):
    #     request = self.request
    #     next_ = request.GET.get('next')
    #     next_post = request.POST.get('next')
    #     redirect_path = next_ or next_post or None
    #
    #     email = form.cleaned_data.get("email")
    #     password = form.cleaned_data.get("password")
    #     user = authenticate(request, username=email, password=password)
    #     # print('user is auth or not --', request.user.is_authenticated)
    #     print('user -->', user, type(user))
    #     if user is not None:
    #         # print('user is auth or not --', request.user.is_authenticated)
    #         if not user.is_active:
    #             messages.error(request,"This user is inactive")
    #             return super(LoginView,self).form_invalid(form)
    #         login(request, user)
    #         user_logged_in.send(user.__class__,instance=user,request=request)
    #         try:
    #             del request.session['guest_email_id']
    #         except:
    #             pass
    #         # redirect to a success page
    #         if is_safe_url(redirect_path, request.get_host()):
    #             return redirect(redirect_path)
    #         else:
    #             return redirect("/")
    #     return super(LoginView,self).form_invalid(form)

choice=(('left','Left'),
        ('right','Right'))



class RegisterForm(forms.ModelForm):
    """
    A form for creating new users. Includes all the required
    fields, plus a repeated password.
    """

    # email = forms.CharField(label='Email', widget=forms.TextInput(attrs={"class":'form-control'}))
    # full_name = forms.CharField(label='Full Name', widget=forms.TextInput(attrs={"class":'form-control'}))

    # user.user_id = last_user_id + 1
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput(attrs={"class":'form-control','placeholder':'New Password'}))
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput(attrs={"class":'form-control','placeholder':'Confirm Password'}))
    username = forms.CharField(label='Username', widget=forms.TextInput(attrs={"class":'form-control','placeholder':'Username'}))
    first_name = forms.CharField(max_length=25, required=True, widget=forms.TextInput(
        attrs={'class': 'form-control', 'id': 'firstName', 'placeholder': 'First Name'}))
    last_name = forms.CharField(max_length=25, required=True, widget=forms.TextInput(
        attrs={'class': 'form-control', 'id': 'lastName', 'placeholder': 'Last Name'}))
    email = forms.EmailField(max_length=35, required=True, widget=forms.TextInput(
        attrs={'class': 'form-control', 'id': 'emailAddress', 'placeholder': 'Email'}))
    referral_id =  forms.CharField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control', 'id': 'referral_id', 'placeholder': 'Referral Id'}))
    placement_id =  forms.CharField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control', 'id': 'placement_id', 'placeholder': 'Placement Id'}))
    position = forms.ChoiceField( required=True,choices=choice,  widget=forms.Select(attrs={'class': 'form-control', 'id': 'position'}))
    mobile = PhoneNumberField(max_length=16, required=True, widget=forms.TextInput(
        attrs={'class': 'form-control', 'id': 'mobile', 'placeholder': 'Mobile'}))
    address = forms.CharField(max_length=45, required=True, widget=forms.TextInput(
        attrs={'class': 'form-control', 'id': 'address', 'placeholder': 'Address'}))
    country = forms.ChoiceField(label="Select your country", choices=COUNTRIES, required=True,
                                widget=forms.Select(attrs={'class': 'form-control country', 'id': None,}))
    # image = forms.ImageField(required=False,widget=forms.I(attrs={'class': 'form-control',}))
    class Meta:
        model = User
        fields = ('username','email','first_name','last_name','referral_id','placement_id','position','password1','password2','mobile','address','country','image')  # 'full_name'

    def clean_password2(self):
        print('clean password @@@ 1')
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        print('clean password @@@ 2')
        password2 = self.cleaned_data.get("password2")
        print('clean password @@@ 3')
        if password1 and password2 and password1 != password2:
            print('clean password @@@ 4')
            raise forms.ValidationError("Passwords don't match")
        print('clean password @@@ 5')
        return password2

    def clean_position(self):
        print('clean position  @@@ referral id ',(self.cleaned_data['referral_id']))

        parent = User.objects.filter(referral_id=(self.cleaned_data['referral_id'])).first()
        # print('parent ---',parent.email)
        print('position 1')
        if parent == None:
            raise forms.ValidationError('Invalid referral id !')
        print('position 2 placement id ',(self.cleaned_data['placement_id']))
        placement_parent=User.objects.filter(placement_id=(self.cleaned_data['placement_id'])).first()
        print('position 3 placement parent --',placement_parent)
        if placement_parent == None:
            raise forms.ValidationError('Invalid placement id !')
        print('position 4')
        print("cleaned_data['position']  ",self.cleaned_data['position'])


        if self.cleaned_data['position'] == 'left' and placement_parent.left != None:
            raise forms.ValidationError('left position already taken !')

        elif self.cleaned_data['position'] == 'right' and placement_parent.right != None:
            raise forms.ValidationError('right position already taken !')
        print('position 5')

        print('position 6')

        return self.cleaned_data.get('position')


    def save(self, commit=True):
        print('in register save method @@@@ 1')
        # Save the provided password in hashed format
        user = super(RegisterForm, self).save(commit=False)
        print('in register save method @@@@ 2')
        user.set_password(self.cleaned_data["password1"])
        print('in register save method @@@@ 3')
        print('user cleaned data #####', self.cleaned_data)
        user.is_active = False  # send confirmation email via signals
        print('in register save method @@@@ 4')
        last_user_id = User.objects.all().last().user_id
        print('in register save method @@@@ 5')

        print('last user id is --', last_user_id)
        user.user_id = last_user_id + 4
        user.parent_refer_id = self.cleaned_data['referral_id']
        parent = User.objects.filter(placement_id=self.cleaned_data['placement_id']).first()
        #parent = User.objects.filter(referral_id=self.cleaned_data['referral_id']).first()
        print('in register save method @@@@ 6')
        if self.cleaned_data['position'] == 'left':
            parent.left = user

        elif self.cleaned_data['position'] == 'right':
            parent.right = user
        print('in register save method @@@@ 7')
        user.save()
        parent.save()
        print('in register save method @@@@ 8')
        user.parent = parent
        user.level = parent.level + 1
        print('in register save method @@@@ 9')
        user.referral_id = user.username
        print('in register save method @@@@ 10')
        user.placement_id = user.username
        print('in register save method @@@@ 11')
        # obj = EmailActivation.objects.create(user=user)
        # obj.send_activation_email()
        if commit:
            user.save()

        return user


# class RegisterForm(forms.Form):
#     username  = forms.CharField()
#     email = forms.EmailField()
#     password = forms.CharField(widget=forms.PasswordInput)
#     password2 = forms.CharField(label='Confirm Password',widget=forms.PasswordInput)
#
#     def clean_username(self):
#         username = self.cleaned_data.get("username")
#         qs = User.objects.filter(username=username)
#         if qs.exists():
#             raise forms.ValidationError("username is taken")
#         return username
#
#     def clean_email(self):
#         email = self.cleaned_data.get("email")
#         qs = User.objects.filter(email=email)
#         if qs.exists():
#             raise forms.ValidationError("email is taken")
#         return email
#
#
#
#     def clean(self):
#         data = self.cleaned_data
#         password = self.cleaned_data.get('password')
#         password2 = self.cleaned_data.get('password2')
#         if password2 != password:
#             raise forms.ValidationError("Passwords must match.")
#         return data
#
