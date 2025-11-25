from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    # Pages (HTML 렌더링)
    path('', views.chatbot_page, name='chatbot_page'),
    
    # API - Chat Messages (채팅 메시지)
    path('api/messages/', views.chat_api, name='chat_message_api'),
    
    # API - Chat Sessions (채팅 세션)
    path('api/sessions/', views.chat_sessions, name='chat_sessions_api'),
    # path('api/sessions/<int:session_id>/', views.chat_session_detail, name='chat_session_detail_api'),  # TODO: 세션 상세 조회
]