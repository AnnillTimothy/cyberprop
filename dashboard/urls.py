from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_home, name='home'),
    path('users/', views.user_list, name='user_list'),
    path('users/create/', views.user_create, name='user_create'),
    path('users/<int:pk>/', views.user_detail, name='user_detail'),
    path('properties/', views.property_admin_list, name='property_list'),
    path('properties/create/', views.property_admin_create, name='property_create'),
    path('properties/<int:pk>/', views.property_admin_detail, name='property_detail'),
    path('properties/<int:pk>/delete/', views.property_admin_delete, name='property_delete'),
    path('submissions/', views.submission_list, name='submission_list'),
    path('submissions/<int:pk>/', views.submission_review, name='submission_review'),
    path('bookings/', views.booking_list, name='booking_list'),
    path('bookings/<int:pk>/', views.booking_update, name='booking_update'),
    path('enquiries/', views.enquiry_list, name='enquiry_list'),
    path('orders/', views.order_admin_list, name='order_list'),
    path('orders/<int:pk>/', views.order_admin_detail, name='order_detail'),
    path('reports/', views.reports, name='reports'),
    path('contact-messages/', views.contact_message_list, name='contact_message_list'),
    path('contact-messages/<int:pk>/', views.contact_message_detail, name='contact_message_detail'),
]
