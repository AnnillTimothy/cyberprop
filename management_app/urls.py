from django.urls import path

from . import views

app_name = 'management'

urlpatterns = [
    path('', views.management_overview, name='overview'),
    path('property/<int:pk>/financials/', views.property_financials, name='property_financials'),
    path('property/<int:pk>/expenses/', views.expense_list, name='expenses'),
    path('property/<int:pk>/income/', views.income_list, name='income'),
    path('maintenance/', views.maintenance_list, name='maintenance'),
    path('maintenance/create/', views.maintenance_create, name='maintenance_create'),
    path('payouts/', views.payout_list, name='payouts'),
    path('cleaning/', views.cleaning_list, name='cleaning'),
]
