from django.urls import path
from . import views

urlpatterns = [
    path('', views.character_info, name='character_info'),
]