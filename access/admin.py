from django.contrib import admin

from access.models import AccountConfiguration, AccessToken  # Organization, OrganizationUser

# admin.site.register(Organization)
# admin.site.register(OrganizationUser)
admin.site.register(AccountConfiguration)
admin.site.register(AccessToken)


# from django.contrib import admin

# from django.contrib import admin
# from django.contrib.auth import get_user_model
# from django.contrib.auth.admin import UserAdmin

# from .forms import CustomUserCreationForm, CustomUserChangeForm
# from .models import CustomUser

# class CustomUserAdmin(UserAdmin):
#     add_form = CustomUserCreationForm
#     form = CustomUserChangeForm
#     model = CustomUser
#     list_display = ['email', 'username', 'name', 'is_driver', 'is_customer']

# admin.site.register(CustomUser, CustomUserAdmin)
