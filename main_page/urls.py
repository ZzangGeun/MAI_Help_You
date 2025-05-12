from django.urls import path
from . import views

urlpatterns = [
    path('', views.main_page, name='main_page'),
    path('character_info/', views.character_info_view, name="character_info_view")
]