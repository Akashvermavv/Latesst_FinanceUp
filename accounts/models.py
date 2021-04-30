from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import (
                                AbstractBaseUser,
                                BaseUserManager
                                )
from django.core.mail import send_mail
from django.urls import reverse
from django.db.models.signals import post_save,pre_save
from django.template.loader import get_template
from django.conf import settings
from django.db.models import Q

from phonenumber_field.modelfields import PhoneNumberField
from django_countries.fields import CountryField


from random import randint

from financeup.utils import  random_string_generator,unique_key_generator
# send_mail(subject,message,from_email,recipient_list,html_message)


DEFAULT_ACTIVATION_DAYS = getattr(settings,'DEFAULT_ACTIVATION_DAYS',7)


class UserManager(BaseUserManager):
    def create_user(self,username,full_name=None,password=None,is_active=True,is_staff=False,is_admin=False):
        if not username:
            raise ValueError("Users must have an username ")
        if not password:
            raise ValueError("Users must have a password")
        # if not full_name:
        #     raise ValueError("Users must have a fullname")

        user_obj = self.model(
            username = username,
            full_name = full_name
        )
        user_obj.set_password(password)    # change user password
        user_obj.staff = is_staff
        user_obj.admin = is_admin
        user_obj.is_active = is_active
        user_obj.save(using=self._db)
        return user_obj

    def create_staffuser(self,username,full_name=None,password =None):
        user = self.create_user(
                            username,
                            full_name=full_name,
                            password =password,
                            is_staff=True
                        )
        return user

    def create_superuser(self,username,full_name=None,password =None):
        user = self.create_user(
                            username,
                            full_name=full_name,
                            password =password,
                            is_staff=True,
                            is_admin=True
                        )
        return user

choice=(('left','Left'),
        ('right','Right'))

class User(AbstractBaseUser):
    first_name = models.CharField(max_length=25, blank=False, null=False)
    last_name = models.CharField(max_length=25, blank=False, null=False)
    username = models.CharField(max_length=25,blank=False,null=False,unique=True)
    position = models.CharField(max_length=25, choices=choice, default='left', )
    email = models.EmailField(max_length=255, unique=True)
    referral_id = models.CharField(max_length=25,blank=False,null=False)
    placement_id = models.CharField(max_length=25,blank=False,null=False)
    parent_refer_id = models.CharField(max_length=25,blank=True,null=True,)

    user_id = models.IntegerField(default=0, unique=True)
    full_name = models.CharField(max_length=255, blank=True, null=True)
    mobile = PhoneNumberField(blank=False, null=False, max_length=16)
    address = models.CharField(max_length=45, blank=False, null=False)
    country = CountryField(blank=False, null=False, blank_label='(select country)')
    # active = models.BooleanField(default=True)  # can login
    is_active = models.BooleanField(default=True)  # can login
    ban = models.BooleanField(default=False)  # can login
    staff = models.BooleanField(default=False)  # staff user non superuser
    admin = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='profile_images', blank=True)
    parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.SET_NULL, related_name="user_parent")
    left = models.ForeignKey("self", null=True, blank=True, on_delete=models.SET_NULL, related_name="user_left_child")
    right = models.ForeignKey("self", null=True, blank=True, on_delete=models.SET_NULL, related_name="user_right_child")
    level = models.IntegerField(default=1)
    investment_carry = models.FloatField(max_length=9, default=0.0)
    daily_earnings = models.FloatField(max_length=9, default=0.0)
    monthly_royality = models.FloatField(max_length=9, default=0.0)
    monthly_royality_last_date = models.DateField(default=None,null=True,blank=True)

    # confirm = models.BooleanField(default=False)
    # confirmed_date = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD  = 'username'  # username
    # USERNAME_FIELD AND password are required by default
    # REQUIRED_FIELDS = ['full_name']   # ['full_name']
    REQUIRED_FIELDS = []   # ['full_name']

    objects = UserManager()

    def __str__(self):
        return self.username

    def get_full_name(self):
        if self.full_name:
            return self.full_name
        return self.email

    def get_short_name(self):
        return self.email

    def has_perm(self,perm,obj=None):
        return True

    def has_module_perms(self,app_label):
        return True

    @property
    def is_staff(self):
        if self.is_admin:
            return True
        return self.staff

    @property
    def is_admin(self):
        return self.admin
    # @property
    # def is_active(self):
    #     return self.active

# class UserProfile(models.Model):
#     user = models.OneToOneField()
#     image = models.ImageField(upload_to='images/', null=True, blank=True)

class EmailActivationQuerySet(models.query.QuerySet):
    def confirmable(self):
        now = timezone.now()
        start_range = now - timedelta(days=DEFAULT_ACTIVATION_DAYS)
        # does my object have a timestamp in here
        end_range = now
        return self.filter(
            activated=False,
            forced_expired = False
        ).filter(
            timestamp__gt = start_range,
            timestamp__lte = end_range
        )

class EmailActivationManager(models.Manager):
    def get_queryset(self):
        return EmailActivationQuerySet(self.model,using=self._db)

    def confirmable(self):
        return self.get_queryset().confirmable()

    def email_exists(self,email):
        return self.get_queryset().filter(Q(email=email) | Q(user__email=email) ).filter(activated = False)

class EmailActivation(models.Model):
    user            = models.ForeignKey(User,on_delete=models.CASCADE)
    email           = models.EmailField()
    key             = models.CharField(max_length=120,blank=True,null=True)
    activated       = models.BooleanField(default=False)
    forced_expired  = models.BooleanField(default=False)
    expires         = models.IntegerField(default=7)
    timestamp       = models.DateTimeField(auto_now_add=True)
    update           = models.DateTimeField(auto_now=True)

    objects = EmailActivationManager()

    def __str__(self):
        return self.email

    def can_activate(self):
        qs = EmailActivation.objects.filter(pk=self.pk).confirmable()   # 1 object
        if qs.exists():
            return True
        return False

    def activate(self):
        if self.can_activate():
            # pre activation user signal
            user = self.user
            user.is_active = True
            user.save()

            # post activation signal for user
            self.activated = True
            self.save()
            return True
        return False


    def regenerate(self):
        self.key = None
        self.save()
        if self.key is not None:
            return True
        return False


    def send_activation(self):
        if not self.activated and not self.forced_expired:
            if self.key:
                base_url =getattr(settings,'BASE_URL','https://www.pythonecommerce.com')
                key_path = reverse("account:email-activate",kwargs={'key':self.key})  # use reverse
                path = "{base}{path}".format(base=base_url,path=key_path)
                context ={
                    'path':path,
                    'email':self.email
                }

                txt_ = get_template("registration/emails/verify.txt").render(context)
                html_ = get_template("registration/emails/verify.html").render(context)
                subject = '1-click Email Verification'
                from_email = settings.DEFAULT_FROM_EMAIL
                recipient_list = [self.email]
                sent_mail =send_mail(subject,
                                     txt_,
                                     from_email,
                                     recipient_list,
                                     html_message=html_,
                                     fail_silently=False,

                                     )
                return sent_mail
        return False



def pre_save_email_activation(sender,instance,*args,**kwargs):
    if not instance.activated and not instance.forced_expired:
        if not instance.key:
            instance.key = unique_key_generator(instance)

pre_save.connect(pre_save_email_activation,sender=EmailActivation)

def post_save_user_create_receiver(sender,instance,created,*args,**kwargs):
    if created:
        obj = EmailActivation.objects.create(user=instance,email = instance.email)
        obj.send_activation()

post_save.connect(post_save_user_create_receiver,sender=User)

class Profile(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    # extend extra data

class GuestEmail(models.Model):
    email       = models.EmailField()
    active      = models.BooleanField(default=True)
    update      = models.DateTimeField(auto_now=True)
    timestamp   = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email
