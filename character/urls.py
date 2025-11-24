from django.urls import path
from . import views

app_name = 'character'

urlpatterns = [
    path('', views.character_info_page, name='character_info_page'),
    path('api/', views.character_info_view, name='character_info_api'),
]