"""
Django 통합 API 테스트 모듈

Django 환경에서 API 함수들을 테스트합니다.

실행방법:
    python manage.py shell
    >>> from tests.api.test_django_integration import DjangoAPITester
    >>> tester = DjangoAPITester()
    >>> tester.run_tests()
"""

import os
import sys
from pathlib import Path

# Django 환경에서 실행되는지 확인
try:
    from django.conf import settings
    DJANGO_AVAILABLE = True
except ImportError:
    DJANGO_AVAILABLE = False
    print("⚠️  Django가 설정되지 않았습니다. Django 셸에서 실행해주세요.")

if DJANGO_AVAILABLE:
    # Django 앱에서 API 함수 import
    from apps.main_page.get_nexon_api import get_api_data, get_notice_list, test_api_data

class DjangoAPITester:
    """Django 환경에서의 API 테스터"""
    
    def __init__(self):
        if not DJANGO_AVAILABLE:
            raise ImportError("Django 환경이 필요합니다. 'python manage.py shell'에서 실행해주세요.")
        
        self.test_results = []
    
    def test_get_api_data(self):
        """get_api_data 함수 테스트"""
        print("\n🔧 get_api_data() 함수 테스트")
        print("-" * 40)
        
        # 공지사항 테스트
        notice_data = get_api_data("/notice")
        notice_success = notice_data is not None
        
        print(f"📢 공지사항 API: {'✅' if notice_success else '❌'}")
        if notice_success:
            print(f"   데이터 타입: {type(notice_data)}")
            if isinstance(notice_data, dict):
                print(f"   키: {list(notice_data.keys())}")
        
        # 이벤트 테스트
        event_data = get_api_data("/notice-event")
        event_success = event_data is not None
        
        print(f"🎉 이벤트 API: {'✅' if event_success else '❌'}")
        if event_success:
            print(f"   데이터 타입: {type(event_data)}")
            if isinstance(event_data, dict):
                print(f"   키: {list(event_data.keys())}")
        
        return notice_success and event_success
    
    def test_get_notice_list(self):
        """get_notice_list 함수 테스트"""
        print("\n📋 get_notice_list() 함수 테스트")
        print("-" * 40)
        
        try:
            result = get_notice_list()
            success = result is not None
            
            print(f"함수 실행: {'✅' if success else '❌'}")
            
            if success:
                print(f"반환 타입: {type(result)}")
                if isinstance(result, dict):
                    print(f"키 목록: {list(result.keys())}")
                    
                    # 각 키의 데이터 확인
                    for key, value in result.items():
                        print(f"  {key}: {type(value)} ({'있음' if value else '없음'})")
            
            return success
            
        except Exception as e:
            print(f"❌ 오류 발생: {e}")
            return False
    
    def test_api_test_function(self):
        """test_api_data 함수 테스트"""
        print("\n🧪 test_api_data() 함수 테스트")
        print("-" * 40)
        
        try:
            test_api_data()  # 이 함수는 자체적으로 출력을 함
            print("✅ 테스트 함수 실행 완료")
            return True
        except Exception as e:
            print(f"❌ 테스트 함수 실행 오류: {e}")
            return False
    
    def run_tests(self):
        """모든 Django 통합 테스트 실행"""
        print("=" * 60)
        print("🔧 Django 통합 API 테스트")
        print("=" * 60)
        
        tests = [
            ("API 데이터 함수", self.test_get_api_data),
            ("공지사항 목록 함수", self.test_get_notice_list),
            ("테스트 함수", self.test_api_test_function),
        ]
        
        results = []
        for test_name, test_func in tests:
            print(f"\n🚀 {test_name} 테스트 시작...")
            try:
                result = test_func()
                results.append((test_name, result))
                print(f"{'✅' if result else '❌'} {test_name} 완료")
            except Exception as e:
                results.append((test_name, False))
                print(f"❌ {test_name} 오류: {e}")
        
        # 결과 요약
        print("\n" + "=" * 60)
        print("📊 테스트 결과 요약")
        print("=" * 60)
        
        success_count = sum(1 for _, success in results if success)
        total_count = len(results)
        
        print(f"✅ 성공: {success_count}/{total_count}")
        print(f"❌ 실패: {total_count - success_count}/{total_count}")
        
        for test_name, success in results:
            status = "✅" if success else "❌"
            print(f"{status} {test_name}")

# Django 셸에서 바로 사용할 수 있는 함수들
def quick_test():
    """빠른 테스트 실행"""
    if not DJANGO_AVAILABLE:
        print("Django 셸에서 실행해주세요: python manage.py shell")
        return
    
    tester = DjangoAPITester()
    tester.run_tests()

def test_single_api():
    """단일 API 호출 테스트"""
    if not DJANGO_AVAILABLE:
        print("Django 셸에서 실행해주세요: python manage.py shell")
        return
    
    print("🔍 단일 API 테스트")
    
    # 사용자 입력 받기 (Django 셸에서)
    endpoint = input("테스트할 엔드포인트 입력 (예: /notice): ")
    
    try:
        data = get_api_data(endpoint)
        if data:
            print(f"✅ 성공!")
            print(f"데이터: {data}")
        else:
            print("❌ 실패")
    except Exception as e:
        print(f"❌ 오류: {e}")

if __name__ == "__main__":
    print("이 파일은 Django 셸에서 실행해주세요:")
    print("python manage.py shell")
    print(">>> from tests.api.test_django_integration import quick_test")
    print(">>> quick_test()")
