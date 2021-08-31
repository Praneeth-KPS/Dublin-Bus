from os import name
from django.urls import path
from . import views
from django.contrib import admin

urlpatterns = [
    path('',views.index, name='index'),
    path("Historic/",views.Historic, name="Historic"),
    path('about/',views.about, name='about'),
    path('transport_details/',views.transport_details, name='transport_details'),
    path('settings/',views.settings, name='settings'),
    path("Model/", views.Model, name="Model"),
    path("Traffic_Model/", views.Traffic_Model, name="Traffic_Model")
]