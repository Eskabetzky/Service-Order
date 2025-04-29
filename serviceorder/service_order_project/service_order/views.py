# service_order/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from .forms import ServiceOrderForm, ServiceRecordForm, ServiceRecordFormSet
from .models import ServiceOrder, ServiceRecord
import json
from django.http import JsonResponse
from django.core.exceptions import ValidationError
from decimal import Decimal
from django.forms import inlineformset_factory
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from .forms import ServiceOrderForm, ServiceRecordForm, ServiceRecordFormSet
from .models import ServiceOrder, ServiceRecord
import json
from django.http import JsonResponse, HttpResponse
from django.core.exceptions import ValidationError
from decimal import Decimal
from django.forms import inlineformset_factory
from django.db.models import Q
import csv
from datetime import datetime
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.forms import inlineformset_factory
from .models import ServiceOrder, ServiceRecord
from .forms import ServiceOrderForm, ServiceRecordForm
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import ServiceOrder

def service_order_form(request):
    if request.method == 'POST':
        form = ServiceOrderForm(request.POST)
        if form.is_valid():
            service_order = form.save()
            
            service_records = json.loads(request.POST.get('service_records', '[]'))
            for record in service_records:
                try:
                    ServiceRecord.objects.create(
                        service_order=service_order,
                        service_from=record['service_from'] if record['service_from'] else None,
                        service_to=record['service_to'] if record['service_to'] else None,
                        designation=record['designation'],
                        status=record['status'],
                        salary=Decimal(record['salary']) if record['salary'] else Decimal('0'),
                        station_of_assignment=record['station_of_assignment'],
                        branch=record['branch'],
                        lwop=record.get('lwop', ''),
                        separation_date=record.get('separation_date') if record.get('separation_date') else None,
                        separation_cause=record.get('separation_cause', '')
                    )
                except ValidationError as e:
                    return render(request, 'service_order/form.html', {
                        'form': form,
                        'error': str(e)
                    })
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'id': service_order.id})
            return redirect('service_order_success')
    else:
        form = ServiceOrderForm()
    
    return render(request, 'service_order/form.html', {'form': form})

def service_order_success(request):
    return render(request, 'service_order/success.html')

def service_order_list(request):
    search_query = request.GET.get('search', '')
    order_by = request.GET.get('order_by', '-created_at')
    
    if search_query:
        service_orders = ServiceOrder.objects.filter(full_name__icontains=search_query).order_by(order_by)
    else:
        service_orders = ServiceOrder.objects.all().order_by(order_by)
    
    paginator = Paginator(service_orders, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'service_order/list.html', {
        'service_orders': page_obj,
        'page_obj': page_obj,
        'is_paginated': paginator.num_pages > 1,
        'search_query': search_query,
        'order_by': order_by
    })

def service_order_detail(request, pk):
    service_order = get_object_or_404(ServiceOrder.objects.prefetch_related('service_records'), pk=pk)
    return render(request, 'service_order/detail.html', {
        'service_order': service_order
    })

def service_order_edit(request, pk):
    service_order = get_object_or_404(ServiceOrder, pk=pk)
    
    # Define the formset factory at the start of the function
    ServiceRecordFormSet = inlineformset_factory(
        ServiceOrder,
        ServiceRecord,
        form=ServiceRecordForm,
        extra=1,
        can_delete=True
    )
    
    if request.method == 'POST':
        form = ServiceOrderForm(request.POST, instance=service_order)
        formset = ServiceRecordFormSet(request.POST, instance=service_order)
        
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            return redirect('service_order_detail', pk=service_order.id)
    else:
        form = ServiceOrderForm(instance=service_order)
        formset = ServiceRecordFormSet(instance=service_order)
    
    return render(request, 'service_order/edit.html', {
        'form': form,
        'formset': formset,
        'service_order': service_order
    })

from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import ServiceOrder

def service_order_delete(request, pk):
    service_order = get_object_or_404(ServiceOrder, pk=pk)
    
    if request.method == 'POST':
        # Delete all related service records first
        service_order.service_records.all().delete()
        # Then delete the service order itself
        service_order.delete()
        messages.success(request, 'Service order and all related records have been permanently deleted.')
        return redirect('service_order_list')
    
    return render(request, 'service_order/confirm_delete.html', {
        'service_order': service_order
    })

def service_order_list(request):
    search_query = request.GET.get('search', '')
    order_by = request.GET.get('order_by', '-created_at')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    status_filter = request.GET.get('status')
    export_format = request.GET.get('export')

    # Base queryset
    service_orders = ServiceOrder.objects.all().order_by(order_by)

    # Apply filters
    if search_query:
        service_orders = service_orders.filter(full_name__icontains=search_query)
    
    if start_date:
        service_orders = service_orders.filter(created_at__date__gte=start_date)
    
    if end_date:
        service_orders = service_orders.filter(created_at__date__lte=end_date)
    
    if status_filter == 'active':
        service_orders = service_orders.filter(service_records__service_to__isnull=True).distinct()
    elif status_filter == 'inactive':
        service_orders = service_orders.filter(service_records__service_to__isnull=False).distinct()

    # Handle export
    if export_format:
        return export_service_orders(service_orders, export_format)

    # Pagination
    paginator = Paginator(service_orders, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'service_order/list.html', {
        'service_orders': page_obj,
        'page_obj': page_obj,
        'is_paginated': paginator.num_pages > 1,
        'search_query': search_query,
        'order_by': order_by,
        'request': request
    })

def export_service_orders(queryset, format_type):
    if format_type == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="service_orders.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'ID', 'Full Name', 'Birth Date', 'Birth Place', 
            'Created At', 'Records Count'
        ])
        
        for order in queryset:
            writer.writerow([
                order.id,
                order.full_name,
                order.birth_date.strftime('%Y-%m-%d') if order.birth_date else '',
                order.birth_place,
                order.created_at.strftime('%Y-%m-%d %H:%M'),
                order.service_records.count()
            ])
        
        return response
    
    elif format_type == 'excel':
        response = HttpResponse(content_type='application/ms-excel')
        response['Content-Disposition'] = 'attachment; filename="service_orders.xls"'
        
        writer = csv.writer(response)
        writer.writerow([
            'ID', 'Full Name', 'Birth Date', 'Birth Place', 
            'Created At', 'Records Count'
        ])
        
        for order in queryset:
            writer.writerow([
                order.id,
                order.full_name,
                order.birth_date.strftime('%Y-%m-%d') if order.birth_date else '',
                order.birth_place,
                order.created_at.strftime('%Y-%m-%d %H:%M'),
                order.service_records.count()
            ])
        
        return response
    
    elif format_type == 'pdf':
        template = get_template('service_order/export_pdf.html')
        context = {
            'service_orders': queryset,
            'export_date': datetime.now().strftime('%Y-%m-%d %H:%M')
        }
        html = template.render(context)
        
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="service_orders.pdf"'
        
        pisa_status = pisa.CreatePDF(html, dest=response)
        if pisa_status.err:
            return HttpResponse('PDF generation error')
        return response
    
    return redirect('service_order_list')
