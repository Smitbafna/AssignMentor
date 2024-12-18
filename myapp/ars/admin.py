from django.contrib import admin
from .models import Organization
from .models import CustomUser
# Register your models here.


admin.site.register(Organization)
admin.site.register(CustomUser)