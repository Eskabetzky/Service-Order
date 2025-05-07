# service_order/forms.py
from django import forms # type: ignore
from .models import ServiceOrder, ServiceRecord

class ServiceOrderForm(forms.ModelForm):
    class Meta:
        model = ServiceOrder
        fields = ['full_name', 'birth_date', 'birth_place']
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
        }
class ServiceRecordForm(forms.ModelForm):
    class Meta:
        model = ServiceRecord
        fields = '__all__'
        widgets = {
            'service_from': forms.DateInput(attrs={'type': 'date'}),
            'service_to': forms.DateInput(attrs={'type': 'date'}),
            'separation_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make these fields optional
        self.fields['station_of_assignment'].required = False
        self.fields['branch'].required = False

class ServiceRecordFormSet(forms.BaseInlineFormSet):
    def clean(self):
        super().clean()
        for form in self.forms:
            if not form.is_valid():
                return
            if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                service_from = form.cleaned_data.get('service_from')
                service_to = form.cleaned_data.get('service_to')
                if service_from and service_to and service_from > service_to:
                    form.add_error('service_to', 'End date must be after start date')