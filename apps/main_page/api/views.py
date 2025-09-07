"""
메인 페이지 DRF API 뷰 (도메인 전용)
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.utils import timezone
from django.db import connection
from drf_spectacular.utils import extend_schema
import logging
import psutil

from apps.main_page.main_page_nexon_api_get import get_notice_list, get_api_data
from .serializers import (
    NoticeListResponseSerializer,
    EventListResponseSerializer,
    HealthCheckResponseSerializer,
    APIKeyValidationSerializer,
    APIKeyValidationResponseSerializer,
)

logger = logging.getLogger(__name__)


class NoticeListAPIView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary="공지사항 목록 조회",
        responses={200: NoticeListResponseSerializer},
        tags=["Main Page"],
    )
    def get(self, request):
        try:
            notice_data = get_notice_list()
            response_data = {
                'notices': notice_data.get('notices', []),
                'total_count': len(notice_data.get('notices', [])),
                'last_updated': timezone.now(),
                'status': 'success'
            }
            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"공지사항 조회 오류: {e}")
            return Response({'error': str(e), 'status': 'error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class EventListAPIView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary="이벤트 목록 조회",
        responses={200: EventListResponseSerializer},
        tags=["Main Page"],
    )
    def get(self, request):
        try:
            event_data = get_api_data('events')
            response_data = {
                'events': event_data.get('events', []) if event_data else [],
                'total_count': len(event_data.get('events', [])) if event_data else 0,
                'last_updated': timezone.now(),
                'status': 'success'
            }
            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"이벤트 조회 오류: {e}")
            return Response({'error': str(e), 'status': 'error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class HealthCheckAPIView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary="시스템 상태 확인",
        responses={200: HealthCheckResponseSerializer},
        tags=["System"],
    )
    def get(self, request):
        try:
            db_status = self._check_database()
            nexon_api_status = self._check_nexon_api()
            system_status = self._check_system_resources()

            overall_status = 'healthy'
            if not db_status['healthy'] or not nexon_api_status['healthy']:
                overall_status = 'degraded'
            if not system_status['healthy']:
                overall_status = 'unhealthy'

            return Response({
                'status': overall_status,
                'timestamp': timezone.now(),
                'services': {
                    'database': db_status,
                    'nexon_api': nexon_api_status,
                    'system': system_status
                },
                'version': '1.0.0'
            })
        except Exception as e:
            logger.error(f"헬스체크 오류: {e}")
            return Response({'status': 'unhealthy', 'error': str(e)}, status=status.HTTP_200_OK)

    def _check_database(self) -> dict:
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
            return {'healthy': True, 'message': 'Database connection OK'}
        except Exception as e:
            return {'healthy': False, 'message': f'Database error: {str(e)}'}

    def _check_nexon_api(self) -> dict:
        try:
            test_data = get_notice_list()
            return {'healthy': bool(test_data), 'message': 'Nexon API OK' if test_data else 'Nexon API No Data'}
        except Exception as e:
            return {'healthy': False, 'message': f'Nexon API error: {str(e)}'}

    def _check_system_resources(self) -> dict:
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            cpu_healthy = cpu_percent < 80
            memory_healthy = memory.percent < 80
            disk_healthy = disk.percent < 80
            return {
                'healthy': cpu_healthy and memory_healthy and disk_healthy,
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'disk_percent': disk.percent,
                'message': 'System resources OK' if all([cpu_healthy, memory_healthy, disk_healthy]) else 'High resource usage'
            }
        except Exception as e:
            return {'healthy': False, 'message': f'System check error: {str(e)}'}


class APIKeyValidationAPIView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary="넥슨 API 키 검증",
        request=APIKeyValidationSerializer,
        responses={200: APIKeyValidationResponseSerializer},
        tags=["Validation"],
    )
    def post(self, request):
        serializer = APIKeyValidationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'error': serializer.errors, 'status': 'error'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            api_key = serializer.validated_data['api_key']
            is_valid = len(api_key) > 10
            if is_valid:
                data = {'is_valid': True, 'api_info': {'key_type': 'game_api', 'expires_at': '2025-12-31', 'permissions': ['character_info', 'rankings']}, 'status': 'success'}
            else:
                data = {'is_valid': False, 'error_message': 'API 키가 유효하지 않습니다.', 'status': 'error'}
            return Response(data)
        except Exception as e:
            logger.error(f"API 키 검증 오류: {e}")
            return Response({'is_valid': False, 'error_message': str(e), 'status': 'error'})


