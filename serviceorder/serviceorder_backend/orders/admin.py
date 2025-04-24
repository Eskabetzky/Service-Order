# orders/admin.py
from django.contrib import admin
from .models import ServiceOrder, ServiceRecord

class ServiceRecordInline(admin.TabularInline):
    model = ServiceRecord
    extra = 1  # Number of empty forms to display

@admin.register(ServiceOrder)
class ServiceOrderAdmin(admin.ModelAdmin):
    inlines = [ServiceRecordInline]
    list_display = ('full_name', 'birth_date', 'birth_place', 'created_at')
    search_fields = ('full_name',)

@admin.register(ServiceRecord)
class ServiceRecordAdmin(admin.ModelAdmin):
    list_display = ('service_order', 'service_from', 'service_to', 'designation', 'status')
    list_filter = ('status', 'station')