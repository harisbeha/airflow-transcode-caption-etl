from django.contrib import admin

from orgs.models import Organization, OrganizationUser

admin.site.register(Organization)
admin.site.register(OrganizationUser)
