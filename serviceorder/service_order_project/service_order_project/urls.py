"""
URL configuration for service_order_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# service_order_project/urls.py
from django.contrib import admin # type: ignore
from django.urls import path # type: ignore
from service_order import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.service_order_form, name='service_order_form'),
    path('success/', views.service_order_success, name='service_order_success'),
    path('records/', views.service_order_list, name='service_order_list'),
    path('records/<int:pk>/', views.service_order_detail, name='service_order_detail'),
    path('records/<int:pk>/edit/', views.service_order_edit, name='service_order_edit'),
    path('records/<int:pk>/delete/', views.service_order_delete, name='service_order_delete'),
    
]