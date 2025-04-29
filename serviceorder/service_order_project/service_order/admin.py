from django.contrib import admin
from .models import ServiceOrder, ServiceRecord

admin.site.register(ServiceOrder)
admin.site.register(ServiceRecord)