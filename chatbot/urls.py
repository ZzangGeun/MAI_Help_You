from django.urls import path
from .views import chatbot_view, chatbot_ask

urlpatterns = [
    path("", chatbot_view, name="chatbot_view"),
    path("chatbot_ask/", chatbot_ask, name="chatbot_ask")
]