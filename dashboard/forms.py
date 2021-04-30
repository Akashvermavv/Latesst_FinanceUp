from django import forms
from django.urls import reverse
from django.contrib.auth.forms import ReadOnlyPasswordHashField
import datetime
from django.utils.safestring import mark_safe
from django.contrib.auth import login,authenticate,logout,get_user_model
from phonenumber_field.formfields import PhoneNumberField
from .models import AllUserNotice,KycVerification
from django.forms.widgets import DateInput



class KycForm(forms.ModelForm):



    first_name = forms.CharField(max_length=25, required=True, widget=forms.TextInput(
        attrs={'class': 'form-control', 'id': 'firstName', }))
    last_name = forms.CharField(max_length=25, required=True, widget=forms.TextInput(
        attrs={'class': 'form-control', 'id': 'lastName', }))
    email = forms.EmailField(max_length=35, required=True, widget=forms.TextInput(
        attrs={'class': 'form-control', 'id': 'emailAddress', }))


    mobile = PhoneNumberField(max_length=16, required=True, widget=forms.TextInput(
        attrs={'class': 'form-control', 'id': 'mobile', }))

    # dob = forms.DateField(initial=datetime.date.today,widget=forms.DateField(attrs={'type': 'date'}))
    address = forms.CharField(max_length=45, required=True, widget=forms.TextInput(
        attrs={'class': 'form-control', 'id': 'address',}))
    city = forms.CharField(max_length=45, required=True, widget=forms.TextInput(
        attrs={'class': 'form-control', 'id': 'city',}))
    state = forms.CharField(max_length=45, required=True, widget=forms.TextInput(
        attrs={'class': 'form-control', 'id': 'state',}))
    nationality = forms.CharField(max_length=45, required=True, widget=forms.TextInput(
        attrs={'class': 'form-control', 'id': 'nationality',}))
    id_number = forms.CharField(max_length=45, required=True, widget=forms.TextInput(
        attrs={'class': 'form-control', 'id': 'id_number', }))
    zipcode = forms.IntegerField(label="", required=True,
                                widget=forms.TextInput(attrs={'class': 'form-control',}))
    # image = forms.ImageField(required=False,widget=forms.ImageField())
    class Meta:
        model = KycVerification
        fields = ('email','first_name','last_name','mobile','dob','address','city','state'
                  ,'passport_image'
                  ,'national_id_front_image'
                  ,'national_id_back_image',
                  'driver_license_image',
                  'other_image',
                  'id_number',
                   'nationality'
                  )  # 'full_name'
        widgets = {
            'dob': DateInput(attrs={'type': 'date'})
        }






class AllUserNoticeForm(forms.ModelForm):
    notice= forms.Textarea(
                               attrs={"class": 'form-control', "placeholder": "Enter the Notice for all users "}
                    )


    class Meta:
        model = AllUserNotice
        fields =[
            'notice',
        ]

