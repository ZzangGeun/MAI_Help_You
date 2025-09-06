"""
챗봇 API 뷰 (DRF 버전)
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.utils.crypto import get_random_string
from django.utils import timezone
from drf_spectacular.utils import extend_schema
import logging

from apps.chatbot.services import chatbot_service
from .chatbot_serializers import (
    ChatbotAskRequestSerializer,
    ChatbotAskResponseSerializer,
    ChatbotHistoryResponseSerializer,
    ChatbotClearHistoryRequestSerializer,
    ChatbotClearHistoryResponseSerializer,
    ChatbotHealthCheckResponseSerializer,
)

logger = logging.getLogger(__name__)


class ChatbotAskAPIView(APIView):
    """
    챗봇 질문 처리 API
    """
    permission_classes = [AllowAny]  # 로그인 없이 사용 가능
    
    @extend_schema(
        summary="챗봇 질문하기",
        description="사용자의 질문을 받아서 AI 챗봇이 응답합니다.",
        request=ChatbotAskRequestSerializer,
        responses={
            200: ChatbotAskResponseSerializer,
            400: "잘못된 요청",
            500: "서버 오류"
        },
        tags=["Chatbot"]
    )
    def post(self, request):
        # 요청 데이터 검증
        serializer = ChatbotAskRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'error': serializer.errors,
                'status': 'error'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        question = serializer.validated_data['question']
        user_id = serializer.validated_data.get('user_id')
        
        # 세션 기반 임시 user_id 생성
        if not user_id:
            if not request.session.session_key:
                request.session.save()
            user_id = request.session.session_key or get_random_string(12)
        
        try:
            # 챗봇 서비스 호출
            result = chatbot_service.get_response(question, user_id)
            
            response_data = {
                'response': result.get('response'),
                'sources': result.get('sources', []),
                'has_rag': result.get('has_rag', False),
                'status': 'success',
                'user_id': user_id
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"챗봇 응답 생성 오류: {e}")
            return Response({
                'error': f'답변 생성 오류: {e}',
                'status': 'error',
                'user_id': user_id
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ChatbotHistoryAPIView(APIView):
    """
    채팅 히스토리 조회 API
    """
    permission_classes = [AllowAny]
    
    @extend_schema(
        summary="채팅 히스토리 조회",
        description="사용자의 채팅 히스토리를 조회합니다.",
        responses={
            200: ChatbotHistoryResponseSerializer,
            500: "서버 오류"
        },
        tags=["Chatbot"]
    )
    def get(self, request):
        try:
            user_id = request.query_params.get("user_id")
            if not user_id:
                if not request.session.session_key:
                    request.session.save()
                user_id = request.session.session_key
            
            history = chatbot_service.get_chat_history(user_id)
            
            return Response({
                'history': history,
                'status': 'success',
                'user_id': user_id
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"히스토리 조회 오류: {e}")
            return Response({
                'error': f"히스토리 조회 중 오류: {str(e)}",
                'status': 'error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ChatbotClearHistoryAPIView(APIView):
    """
    채팅 히스토리 초기화 API
    """
    permission_classes = [AllowAny]
    
    @extend_schema(
        summary="채팅 히스토리 초기화",
        description="사용자의 채팅 히스토리를 모두 삭제합니다.",
        request=ChatbotClearHistoryRequestSerializer,
        responses={
            200: ChatbotClearHistoryResponseSerializer,
            400: "잘못된 요청",
            500: "서버 오류"
        },
        tags=["Chatbot"]
    )
    def post(self, request):
        try:
            serializer = ChatbotClearHistoryRequestSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            user_id = serializer.validated_data.get("user_id")
            if not user_id:
                if not request.session.session_key:
                    request.session.save()
                user_id = request.session.session_key
            
            success = chatbot_service.clear_history(user_id)
            
            if success:
                return Response({
                    'message': "채팅 히스토리가 초기화되었습니다.",
                    'status': 'success',
                    'user_id': user_id
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'error': "히스토리 초기화에 실패했습니다.",
                    'status': 'error'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except Exception as e:
            logger.error(f"히스토리 초기화 오류: {e}")
            return Response({
                'error': f"히스토리 초기화 중 오류: {str(e)}",
                'status': 'error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ChatbotHealthCheckAPIView(APIView):
    """
    챗봇 서비스 상태 확인 API
    """
    permission_classes = [AllowAny]
    
    @extend_schema(
        summary="챗봇 서비스 상태 확인",
        description="챗봇 서비스가 정상 동작하는지 확인합니다.",
        responses={
            200: ChatbotHealthCheckResponseSerializer,
            503: "서비스 불가능"
        },
        tags=["Chatbot"]
    )
    def get(self, request):
        try:
            # 테스트 응답으로 서비스 상태 확인
            test_response = chatbot_service.get_response("테스트", "test_user")
            
            if test_response.get('response'):
                return Response({
                    'status': 'healthy',
                    'timestamp': timezone.now(),
                    'details': {
                        'service': 'chatbot',
                        'test_response': 'OK'
                    }
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'status': 'unhealthy',
                    'timestamp': timezone.now(),
                    'details': {
                        'service': 'chatbot',
                        'error': 'No response from service'
                    }
                }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
                
        except Exception as e:
            logger.error(f"헬스체크 오류: {e}")
            return Response({
                'status': 'unhealthy',
                'timestamp': timezone.now(),
                'details': {
                    'service': 'chatbot',
                    'error': str(e)
                }
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
