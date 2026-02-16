"""
URL configuration for travel_system project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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

from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from bookings import views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Auth
    path('', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),    
    # Dashboard & Bookings
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/new/', views.new_booking, name='new_booking'),
    
    # Check this line carefully!
    path('dashboard/export/', views.export_bookings_csv, name='export_data'),

    path('dashboard/view/<str:booking_id>/', views.booking_detail, name='booking_detail'),
    path('dashboard/delete/<str:booking_id>/', views.delete_booking, name='delete_booking'),

    

    
    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)