from django.urls import path
from . import views

app_name = 'character_info'

urlpatterns = [
    path('', views.character_info_view, name='character_info'),
    path('search/', views.character_info_view, name='character_search'),
]