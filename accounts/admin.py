from django.contrib import admin
from django.contrib.auth import get_user_model
from .forms import UserAdminCreationForm,UserAdminChangeForm
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import GuestEmail,EmailActivation
#,UserProfile

User = get_user_model()



class UserAdmin(BaseUserAdmin):
    # The forms to add and change user instances
    form = UserAdminChangeForm
    add_form = UserAdminCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('email', 'admin')
    list_filter = ('admin','staff','is_active','ban')
    fieldsets = (
        (None, {'fields': ('email','username', 'password','parent_refer_id')}),
        ('Personal info', {'fields': (
                                'first_name',
                                'ban',
                                'last_name',
                                  'daily_earnings',
                                   'monthly_royality_last_date',
                                  'monthly_royality',
                                'user_id','referral_id','placement_id',

                                'mobile',
                                'address',
                                'country',
                                'parent',
                                'left',
                                'right',
                                'investment_carry',

                                      'image')}),

        ('Permissions', {'fields': ('admin','staff','is_active',)}),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2')}
        ),
    )
    search_fields = ('email','full_name')
    ordering = ('email',)
    filter_horizontal = ()


# class UserAdmin(admin.ModelAdmin):
#     search_fields = ['email']
#     form =  UserAdminChangeForm        # update view
#     add_form = UserAdminCreationForm   # create view
#
#     # class Meta:
#     #     model = User



admin.site.register(User,UserAdmin)


# remove Group Model from admin. We're not using it.
admin.site.unregister(Group)


class EmailActivationAdmin(admin.ModelAdmin):
    search_fields = ['email']
    class Meta:
        model = EmailActivation

admin.site.register(EmailActivation,EmailActivationAdmin)


admin.site.register(GuestEmail)

# admin.site.register(UserProfile)
