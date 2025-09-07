"""
회원 가입/인증 API 뷰 (signup 도메인)
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.utils import timezone
from drf_spectacular.utils import extend_schema

from .serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    AuthResponseSerializer,
)


class UserRegistrationAPIView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary="사용자 회원가입",
        request=UserRegistrationSerializer,
        responses={201: AuthResponseSerializer},
        tags=["Authentication"],
    )
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'error': serializer.errors, 'status': 'error'}, status=status.HTTP_400_BAD_REQUEST)
        data = serializer.validated_data
        user = {
            'id': data['username'],
            'username': data['username'],
            'email': data['email'],
            'nickname': data['nickname'],
            'has_nexon_api': bool(data.get('nexon_api_key')),
            'created_at': timezone.now()
        }
        return Response({'user': user, 'token': 'sample_jwt_token_here', 'message': '회원가입이 완료되었습니다.', 'status': 'success'}, status=201)


class UserLoginAPIView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary="사용자 로그인",
        request=UserLoginSerializer,
        responses={200: AuthResponseSerializer},
        tags=["Authentication"],
    )
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'error': serializer.errors, 'status': 'error'}, status=status.HTTP_400_BAD_REQUEST)
        username = serializer.validated_data['username']
        user = {
            'id': username,
            'username': username,
            'email': f'{username}@example.com',
            'nickname': f'{username}_nick',
            'has_nexon_api': True,
            'created_at': timezone.now()
        }
        return Response({'user': user, 'token': 'sample_jwt_token_here', 'message': '로그인이 완료되었습니다.', 'status': 'success'})


