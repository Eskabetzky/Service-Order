# service_order/models.py (no changes)
from django.db import models
from decimal import Decimal

class ServiceOrder(models.Model):
    full_name = models.CharField(max_length=255)
    birth_date = models.DateField(null=True, blank=True)
    birth_place = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.full_name

class ServiceRecord(models.Model):
    service_order = models.ForeignKey(ServiceOrder, on_delete=models.CASCADE, related_name='service_records')
    service_from = models.DateField(null=True, blank=True)
    service_to = models.DateField(null=True, blank=True)
    designation = models.CharField(max_length=255)
    status = models.CharField(max_length=100)
    salary = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    station_of_assignment = models.CharField(max_length=255, blank=True, null=True)
    branch = models.CharField(max_length=255, blank=True, null=True)
    lwop = models.CharField(max_length=100, blank=True, null=True)
    separation_date = models.DateField(null=True, blank=True)
    separation_cause = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.designation} ({self.service_from} to {self.service_to})"