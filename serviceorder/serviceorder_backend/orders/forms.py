from django import forms
from .models import ServiceOrder, ServiceRecord

class ServiceOrderForm(forms.ModelForm):
    class Meta:
        model = ServiceOrder
        fields = ['full_name', 'birth_date', 'birth_place']

class ServiceRecordForm(forms.ModelForm):
    class Meta:
        model = ServiceRecord
        fields = '__all__'
        exclude = ['service_order']