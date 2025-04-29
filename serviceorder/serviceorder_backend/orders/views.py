# orders/views.py
from django.shortcuts import render, redirect
from .forms import ServiceOrderForm

def create_service_order(request):
    if request.method == 'POST':
        form = ServiceOrderForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('success')
    else:
        form = ServiceOrderForm()
    return render(request, 'orders/service_order.html', {'form': form})

def success(request):
    return render(request, 'orders/success.html')