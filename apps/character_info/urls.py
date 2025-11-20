from django.urls import path
from . import views

urlpatterns = [
    path('', views.character_info_view, name='character_info'),
]