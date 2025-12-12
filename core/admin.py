# core/admin.py

from django.contrib import admin
from .models import Beneficiary, AidRequest, Distribution

# Register your models here
admin.site.register(Beneficiary)
admin.site.register(AidRequest)
admin.site.register(Distribution)