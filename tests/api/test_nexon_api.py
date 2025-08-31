"""
넥슨 메이플스토리 API 테스트 모듈

이 파일은 독립적으로 실행 가능한 API 테스트입니다.
Django 설정 없이도 바로 실행할 수 있습니다.

실행방법:
    python tests/api/test_nexon_api.py
"""

import os
import sys
import requests
import json
from pathlib import Path
from dotenv import load_dotenv

# 프로젝트 루트 경로를 Python path에 추가
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

# .env 파일 로드
load_dotenv(project_root / '.env')

BASE_URL = "https://open.api.nexon.com/maplestory/v1"
NEXON_API_KEY = os.getenv('NEXON_API_KEY')

class NexonAPITester:
    """넥슨 API 테스터 클래스"""
    
    def __init__(self):
        self.base_url = BASE_URL
        self.api_key = NEXON_API_KEY
        self.headers = {'x-nxopen-api-key': self.api_key}
        self.test_results = []
    
    def get_api_data(self, endpoint, params=None):
        """API 데이터 가져오기"""
        url = f'{self.base_url}{endpoint}'
        
        print(f"🌐 API 호출: {url}")
        print(f"🔑 API 키 설정됨: {'✅' if self.api_key else '❌'}")
        
        if not self.api_key:
            print("⚠️  NEXON_API_KEY가 설정되지 않았습니다!")
            return None

        try: 
            response = requests.get(url, headers=self.headers, params=params)
            print(f"📡 HTTP 상태 코드: {response.status_code}")
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f'❌ API 요청 실패: {url}')
                print(f'📄 응답 내용: {response.text}')
                return None
        
        except requests.RequestException as e:
            print(f'🚨 요청 오류: {e}')
            return None
    
    def test_endpoint(self, endpoint, description):
        """개별 엔드포인트 테스트"""
        print(f"\n{description} 테스트")
        print("-" * 40)
        
        data = self.get_api_data(endpoint)
        
        result = {
            'endpoint': endpoint,
            'description': description,
            'success': data is not None,
            'data': data
        }
        
        if data:
            print(f"✅ 성공!")
            print(f"📊 데이터 타입: {type(data)}")
            
            if isinstance(data, dict):
                print(f"🗝️  키 목록: {list(data.keys())}")
                
                # 각 키의 데이터 미리보기
                for key, value in data.items():
                    if isinstance(value, list):
                        print(f"📝 {key}: 리스트 (항목 {len(value)}개)")
                        if value:  # 리스트가 비어있지 않으면
                            print(f"   첫 번째 항목 미리보기:")
                            first_item = value[0]
                            if isinstance(first_item, dict):
                                for item_key, item_value in first_item.items():
                                    # 너무 긴 내용은 잘라서 표시
                                    display_value = str(item_value)
                                    if len(display_value) > 100:
                                        display_value = display_value[:100] + "..."
                                    print(f"      {item_key}: {display_value}")
                    else:
                        print(f"📄 {key}: {value}")
        else:
            print("❌ 데이터 가져오기 실패")
        
        self.test_results.append(result)
        return result
    
    def run_all_tests(self):
        """모든 API 엔드포인트 테스트 실행"""
        print("=" * 60)
        print("🍁 메이플스토리 넥슨 API 전체 테스트")
        print("=" * 60)
        
        # 테스트할 엔드포인트들
        endpoints = [
            ("/notice", "📢 공지사항"),
            ("/notice-event", "🎉 이벤트"),
        ]
        
        for endpoint, description in endpoints:
            self.test_endpoint(endpoint, description)
        
        self.print_summary()
    
    def print_summary(self):
        """테스트 결과 요약"""
        print("\n" + "=" * 60)
        print("📋 테스트 결과 요약")
        print("=" * 60)
        
        success_count = sum(1 for result in self.test_results if result['success'])
        total_count = len(self.test_results)
        
        print(f"✅ 성공: {success_count}/{total_count}")
        print(f"❌ 실패: {total_count - success_count}/{total_count}")
        
        for result in self.test_results:
            status = "✅" if result['success'] else "❌"
            print(f"{status} {result['description']}: {result['endpoint']}")
    
    def save_test_data(self, save_dir="tests/data"):
        """테스트 데이터를 파일로 저장"""
        save_path = project_root / save_dir
        save_path.mkdir(exist_ok=True)
        
        print(f"\n💾 테스트 데이터를 {save_dir}/ 폴더에 저장합니다...")
        
        for result in self.test_results:
            if result['success'] and result['data']:
                endpoint = result['endpoint'].strip('/').replace('/', '_')
                filename = f"nexon_api_{endpoint}_data.json"
                file_path = save_path / filename
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(result['data'], f, indent=2, ensure_ascii=False)
                
                print(f"📁 {result['description']} 데이터 저장: {filename}")

def main():
    """메인 실행 함수"""
    tester = NexonAPITester()
    tester.run_all_tests()
    
    # 파일 저장 여부 확인
    save_choice = input("\n📄 API 데이터를 JSON 파일로 저장하시겠습니까? (y/n): ")
    if save_choice.lower() == 'y':
        tester.save_test_data()
    
    print("\n✨ 테스트 완료!")

if __name__ == "__main__":
    main()
