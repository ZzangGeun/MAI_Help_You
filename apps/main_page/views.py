from django.http.request import HttpRequest
from django.shortcuts import render, redirect
from .main_page_nexon_api_get import get_notice_list, get_api_data
import requests
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db import connection
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
import asyncio
import aiohttp
import time
import logging
import psutil

logger = logging.getLogger(__name__)


# HTML 페이지 뷰들
def main_page(request):
    notice = get_notice_list()
    context = {
        **notice,
        'timestamp': int(time.time())  # 캐시 방지용 타임스탬프
    }
    
    return render(request, 'main_page.html', context)


# 캐릭터 정보 페이지 뷰
def character_info_view(request):
    return render(request, "character_info.html")

# 회원가입 페이지 뷰
def signup_view(request):
    return render(request, "signup.html")

# 로그인 페이지 뷰
def login_view(request):
    return render(request, "login.html")

# =============================================================================
# DRF APIView 예제들 (하이브리드 방식)
# =============================================================================



class LoginAPIView(APIView):
    """
    로그인 API (DRF APIView 예제)
    """
    permission_classes = [AllowAny]
    
    @extend_schema(
        summary="사용자 로그인",
        description="사용자 인증을 수행합니다.",
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'string', 'description': '아이디'},
                    'password': {'type': 'string', 'description': '비밀번호'},
                },
                'required': ['id', 'password']
            }
        },
        responses={
            200: {
                'description': '로그인 성공',
                'content': {
                    'application/json': {
                        'example': {
                            'message': '로그인 성공',
                            'token': 'jwt_token_here',
                            'user': {
                                'id': 'user123',
                                'username': 'testuser',
                                'nickname': '테스트유저'
                            },
                            'status': 'success'
                        }
                    }
                }
            },
            401: {'description': '인증 실패'},
            400: {'description': '잘못된 요청'}
        },
        tags=["Authentication"]
    )
    def post(self, request):
        """
        POST /api/v1/auth/login/
        """
        try:
            username = request.data.get('username')
            password = request.data.get('password')
            
            if not username or not password:
                return Response({
                    'error': '사용자명과 비밀번호를 입력해주세요.',
                    'status': 'error'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 실제 로그인 로직 (예제)
            # TODO: 사용자 인증, JWT 토큰 생성 등
            
            return Response({
                'message': '로그인 성공',
                'token': f'jwt_token_for_{username}',
                'user': {
                    'id': f'user_{username}',
                    'username': username,
                    'nickname': f'{username}_닉네임'
                },
                'status': 'success'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"로그인 오류: {e}")
            return Response({
                'error': f'로그인 중 오류가 발생했습니다: {str(e)}',
                'status': 'error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CharacterInfoAPIView(APIView):
    """
    캐릭터 정보 조회 API (DRF APIView 예제)
    """
    permission_classes = [IsAuthenticated]  # 인증된 사용자만 접근 가능
    
    @extend_schema(
        summary="캐릭터 정보 조회",
        description="특정 캐릭터의 상세 정보를 조회합니다.",
        parameters=[
            OpenApiParameter(
                name='character_name',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,
                description='캐릭터 이름',
                required=True
            ),
            OpenApiParameter(
                name='world_name',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='월드 이름 (선택사항)',
                required=False
            )
        ],
        responses={
            200: {
                'description': '캐릭터 정보 조회 성공',
                'content': {
                    'application/json': {
                        'example': {
                            'character': {
                                'name': '테스트캐릭터',
                                'level': 200,
                                'class': '아크메이지',
                                'world': '스카니아',
                                'guild': '테스트길드'
                            },
                            'status': 'success'
                        }
                    }
                }
            },
            404: {'description': '캐릭터를 찾을 수 없음'},
            401: {'description': '인증 필요'}
        },
        tags=["Character"]
    )
    def get(self, request, character_name=None):
        """
        GET /api/v1/character/info/{character_name}/
        """
        try:
            # URL 파라미터에서 캐릭터 이름 가져오기
            if not character_name:
                character_name = request.query_params.get('character_name')
            
            if not character_name:
                return Response({
                    'error': '캐릭터 이름이 필요합니다.',
                    'status': 'error'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            world_name = request.query_params.get('world_name', '스카니아')
            
            # 실제 캐릭터 정보 조회 로직 (예제)
            # TODO: Nexon API 호출, 데이터베이스 조회 등
            
            character_data = {
                'name': character_name,
                'level': 200,
                'class': '아크메이지',
                'world': world_name,
                'guild': '테스트길드',
                'last_updated': time.time()
            }
            
            return Response({
                'character': character_data,
                'status': 'success'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"캐릭터 정보 조회 오류: {e}")
            return Response({
                'error': f'캐릭터 정보 조회 중 오류가 발생했습니다: {str(e)}',
                'status': 'error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# =============================================================================
# DRF Function-based View 예제들 (@api_view 데코레이터 사용)
# =============================================================================

@api_view(['GET'])
@permission_classes([AllowAny])
@extend_schema(
    summary="공지사항 목록 조회 (Function-based)",
    description="Function-based view를 사용한 공지사항 조회 예제",
    responses={
        200: {
            'description': '공지사항 목록 조회 성공',
            'content': {
                'application/json': {
                    'example': {
                        'notices': [
                            {
                                'title': '공지사항 제목',
                                'date': '2024-01-01',
                                'url': 'https://example.com'
                            }
                        ],
                        'total_count': 10,
                        'status': 'success'
                    }
                }
            }
        }
    },
    tags=["Notice"]
)
def notice_list_api(request):
    """
    GET /api/v1/main/notices/
    Function-based view 예제
    """
    try:
        # 기존 함수 재사용
        notice_data = get_notice_list()
        
        return Response({
            'notices': notice_data.get('notices', []),
            'total_count': len(notice_data.get('notices', [])),
            'status': 'success'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"공지사항 조회 오류: {e}")
        return Response({
            'error': f'공지사항 조회 중 오류가 발생했습니다: {str(e)}',
            'status': 'error'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@extend_schema(
    summary="API 키 검증 (Function-based)",
    description="Function-based view를 사용한 API 키 검증 예제",
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'api_key': {'type': 'string', 'description': '검증할 API 키'}
            },
            'required': ['api_key']
        }
    },
    responses={
        200: {
            'description': 'API 키 검증 성공',
            'content': {
                'application/json': {
                    'example': {
                        'valid': True,
                        'message': '유효한 API 키입니다.',
                        'status': 'success'
                    }
                }
            }
        },
        400: {'description': '잘못된 API 키'},
        401: {'description': '인증 필요'}
    },
    tags=["API Key"]
)
def validate_api_key_api(request):
    """
    POST /api/v1/main/validate-api-key/
    Function-based view 예제
    """
    try:
        api_key = request.data.get('api_key')
        
        if not api_key:
            return Response({
                'error': 'API 키가 필요합니다.',
                'status': 'error'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 실제 API 키 검증 로직 (예제)
        is_valid = len(api_key) >= 10  # 간단한 검증 예제
        
        if is_valid:
            return Response({
                'valid': True,
                'message': '유효한 API 키입니다.',
                'status': 'success'
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'valid': False,
                'message': '유효하지 않은 API 키입니다.',
                'status': 'error'
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        logger.error(f"API 키 검증 오류: {e}")
        return Response({
            'error': f'API 키 검증 중 오류가 발생했습니다: {str(e)}',
            'status': 'error'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


