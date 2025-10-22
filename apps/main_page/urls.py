from django.urls import path
from . import views

app_name = 'main_page'

urlpatterns = [
    path('', views.main_page, name='main_page'),
    path('chatbot/', views.chatbot_page, name='chatbot_page'),
    path('api/rankings/', views.ranking_api_view, name='ranking_api'),
    path('api/character/search/', views.character_search_api_view, name='character_search_api'),
]