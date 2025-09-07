"""
DRF API 테스트 명령어
사용법: python manage.py test_api
"""
from django.core.management.base import BaseCommand
import requests
import json


class Command(BaseCommand):
    help = 'DRF API 기본 테스트'

    def handle(self, *args, **options):
        base_url = 'http://127.0.0.1:8000/api/v1'
        
        self.stdout.write(self.style.SUCCESS('🚀 DRF API 테스트 시작'))
        
        # 1. 헬스체크 테스트
        try:
            response = requests.get(f'{base_url}/chatbot/health/')
            self.stdout.write(f'✅ 헬스체크: {response.status_code} - {response.json()}')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ 헬스체크 실패: {e}'))
        
        # 2. 챗봇 질문 테스트
        try:
            test_data = {
                'question': 'DRF 테스트 질문입니다',
                'user_id': 'test_user'
            }
            response = requests.post(
                f'{base_url}/chatbot/ask/',
                json=test_data,
                headers={'Content-Type': 'application/json'}
            )
            result = response.json()
            self.stdout.write(f'✅ 챗봇 질문: {response.status_code}')
            self.stdout.write(f'   응답: {result.get("status")}')
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ 챗봇 질문 실패: {e}'))
        
        # 3. 히스토리 조회 테스트
        try:
            response = requests.get(f'{base_url}/chatbot/history/?user_id=test_user')
            result = response.json()
            self.stdout.write(f'✅ 히스토리 조회: {response.status_code}')
            self.stdout.write(f'   히스토리 개수: {len(result.get("history", []))}')
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ 히스토리 조회 실패: {e}'))
        
        # 4. 메인 페이지 API 테스트
        try:
            # 공지사항 목록 테스트
            response = requests.get(f'{base_url}/main/notices/')
            self.stdout.write(f'✅ 공지사항 API: {response.status_code}')
            if response.status_code == 200:
                data = response.json()
                notice_count = data.get('total_count', 0)
                self.stdout.write(f'   공지사항 개수: {notice_count}개')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ 공지사항 API 실패: {e}'))
        
        # 5. 헬스체크 테스트
        try:
            response = requests.get(f'{base_url}/main/health/')
            result = response.json()
            status_emoji = '✅' if result.get('status') == 'healthy' else '⚠️'
            self.stdout.write(f'{status_emoji} 시스템 헬스체크: {result.get("status")}')
            
            # 서비스별 상태 표시
            services = result.get('services', {})
            for service, info in services.items():
                service_status = '✅' if info.get('healthy') else '❌'
                self.stdout.write(f'   {service}: {service_status} {info.get("message", "")}')
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ 헬스체크 실패: {e}'))
        
        # 6. API 키 검증 테스트
        try:
            test_key_data = {'api_key': 'test_key_12345'}
            response = requests.post(
                f'{base_url}/main/validate-api-key/',
                json=test_key_data,
                headers={'Content-Type': 'application/json'}
            )
            result = response.json()
            self.stdout.write(f'✅ API 키 검증: {response.status_code}')
            self.stdout.write(f'   검증 결과: {"유효" if result.get("is_valid") else "무효"}')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ API 키 검증 실패: {e}'))

        # 7. API 문서 접근 테스트 (개발 환경에서만)
        try:
            response = requests.get('http://127.0.0.1:8000/api/docs/')
            if response.status_code == 200:
                self.stdout.write('✅ API 문서 접근 가능: http://127.0.0.1:8000/api/docs/')
            else:
                self.stdout.write(f'⚠️  API 문서 상태: {response.status_code}')
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'⚠️  API 문서 접근 실패: {e}'))
        
        self.stdout.write(self.style.SUCCESS('\n🎉 전체 API 테스트 완료!'))
