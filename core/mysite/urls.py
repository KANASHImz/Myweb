from django.contrib import admin
from django.urls import path
from .views import * 

app_name = 'mysite'

urlpatterns = [
    path('', HomePageView.as_view(), name='index'),
    path('contact/', ContactUsView.as_view(), name='contact'),
    path('about/', about_view, name='about'),
]