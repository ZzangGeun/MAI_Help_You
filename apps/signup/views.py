from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

import logging
logger = logging.getLogger(__name__)

# Create your views here.


class SignupAPIView(APIView):
    """
    회원가입 API (DRF APIView 예제)
    """
    permission_classes = [AllowAny]  # 회원가입은 인증 불필요
    
    @extend_schema(
        summary="사용자 회원가입",
        description="새로운 사용자를 등록합니다.",
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'string', 'description': '아이디'},
                    'password': {'type': 'string', 'description': '비밀번호'},
                    'nickname': {'type': 'string', 'description': '닉네임'},
                },
                'required': ['id','password', 'nickname']
            }
        },
        responses={
            201: {
                'description': '회원가입 성공',
                'content': {
                    'application/json': {
                        'example': {
                            'message': '회원가입이 완료되었습니다.',
                            'user_id': 'user123',
                            'status': 'success'
                        }
                    }
                }
            },
            400: {'description': '잘못된 요청 데이터'},
            409: {'description': '이미 존재하는 사용자'}
        },
        tags=["Authentication"]
    )
    def post(self, request):
        """
        POST /api/v1/auth/register/
        """
        try:
            # 요청 데이터 검증

            id = request.data.get('id')
            password = request.data.get('password')
            nickname = request.data.get('nickname')
            
            if not all([password, id, nickname]):
                return Response({
                    'error': '필수 필드가 누락되었습니다.',
                    'status': 'error'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 실제 회원가입 로직 (예제)
            # TODO: 실제 User 모델 생성, 비밀번호 해싱, 이메일 중복 체크 등
            
            return Response({
                'message': '회원가입이 완료되었습니다.',
                'user_id': f'{id}',
                'status': 'success'
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"회원가입 오류: {e}")
            return Response({
                'error': f'회원가입 중 오류가 발생했습니다: {str(e)}',
                'status': 'error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
