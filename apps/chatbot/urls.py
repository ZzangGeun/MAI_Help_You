from django.urls import path
from .views import chatbot_view, chatbot_ask, chatbot_health_check, chatbot_history, chatbot_clear_history

urlpatterns = [
    path("", chatbot_view, name="chatbot"),
    path("ask/", chatbot_ask, name="chatbot_ask"),
    path("history/", chatbot_history, name="chatbot_history"),
    path("clear-history/", chatbot_clear_history, name="chatbot_clear_history"),
    path("health/", chatbot_health_check, name="chatbot_health"),
]