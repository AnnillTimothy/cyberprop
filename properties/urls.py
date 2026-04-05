from django.urls import path
from . import views

app_name = 'properties'

urlpatterns = [
    path('', views.property_list, name='list'),
    path('submit/', views.submit_property, name='submit'),
    path('my-submissions/', views.my_submissions, name='my_submissions'),
    path('<slug:slug>/', views.property_detail, name='detail'),
    path('<slug:slug>/enquiry/', views.submit_enquiry, name='enquiry'),
    path('<slug:slug>/book/', views.book_viewing, name='book'),
]
