from django.urls import path
from django.shortcuts import render
from . import views

urlpatterns = [
    # Resident functions
    path('request/new/', views.RequestCreateView.as_view(), name='request_create'),
    # Staff functions (Barangay Staff)
    path('staff/requests/', views.AdminRequestListView.as_view(), name='admin_request_list'),
    path('staff/request/<int:pk>/update/', views.RequestUpdateView.as_view(), name='request_update'),
    # You would also need views for: Distribution record creation, and simple reports.
    # Placeholder for a homepage
    path('', views.home_view, name='home'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('staff/reports/', views.DistributionReportView.as_view(), name='distribution_report'),
    # Resident pages
    path('request/list/', views.RequestListView.as_view(), name='request_list'),
    path('request/<int:pk>/', views.RequestDetailView.as_view(), name='request_detail'),
    path('profile/', views.BeneficiaryUpdateView.as_view(), name='profile'),
    # Staff pages
    path('distribution/new/', views.DistributionCreateView.as_view(), name='distribution_create'),
    # Static pages
    path('about/', lambda request: render(request, 'about.html'), name='about'),
    path('help/', lambda request: render(request, 'help.html'), name='help'),
]