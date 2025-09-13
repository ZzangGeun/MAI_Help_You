#!/usr/bin/env python
"""
간단한 HTTP 요청으로 views.py 테스트 (DRF 제거 후)
"""
import requests
import json

def test_api_endpoints():
    """API 엔드포인트들을 테스트합니다."""
    base_url = "http://127.0.0.1:8000"
    
    # 테스트할 엔드포인트들
    endpoints = [
        "/api/health/",
        "/api/notice/",
        "/api/notice-cashshop/",
        "/api/notice-update/",
        "/api/notice-event/",
    ]
    
    print("🚀 API 엔드포인트 테스트 시작! (DRF 제거 후)")
    print("=" * 50)
    
    for endpoint in endpoints:
        url = base_url + endpoint
        print(f"\n📡 테스트 중: {endpoint}")
        
        try:
            response = requests.get(url, timeout=5)
            print(f"✅ 상태 코드: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"📄 응답 데이터: {json.dumps(data, indent=2, ensure_ascii=False)[:200]}...")
                except:
                    print(f"📄 응답 텍스트: {response.text[:200]}...")
            else:
                print(f"❌ 오류: {response.text[:200]}...")
                
        except requests.exceptions.ConnectionError:
            print("❌ 연결 실패: 서버가 실행 중인지 확인하세요.")
        except requests.exceptions.Timeout:
            print("❌ 타임아웃: 요청이 너무 오래 걸렸습니다.")
        except Exception as e:
            print(f"❌ 오류: {e}")

def test_post_endpoints():
    """POST 엔드포인트들을 테스트합니다."""
    base_url = "http://127.0.0.1:8000"
    
    print("\n" + "=" * 50)
    print("📝 POST API 엔드포인트 테스트")
    print("=" * 50)
    
    # 로그인 API 테스트
    print("\n🔐 로그인 API 테스트:")
    try:
        login_data = {
            "username": "testuser",
            "password": "testpass123"
        }
        response = requests.post(
            f"{base_url}/api/login/",
            json=login_data,
            headers={'Content-Type': 'application/json'},
            timeout=5
        )
        print(f"✅ 상태 코드: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"📄 응답: {json.dumps(data, indent=2, ensure_ascii=False)}")
    except Exception as e:
        print(f"❌ 오류: {e}")
    
    # API 키 검증 테스트
    print("\n🔑 API 키 검증 테스트:")
    try:
        api_key_data = {
            "api_key": "test_api_key_12345"
        }
        response = requests.post(
            f"{base_url}/api/validate-api-key/",
            json=api_key_data,
            headers={'Content-Type': 'application/json'},
            timeout=5
        )
        print(f"✅ 상태 코드: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"📄 응답: {json.dumps(data, indent=2, ensure_ascii=False)}")
    except Exception as e:
        print(f"❌ 오류: {e}")

def test_main_page():
    """메인 페이지를 테스트합니다."""
    print("\n" + "=" * 50)
    print("🏠 메인 페이지 테스트")
    print("=" * 50)
    
    try:
        response = requests.get("http://127.0.0.1:8000/", timeout=5)
        print(f"✅ 상태 코드: {response.status_code}")
        
        if response.status_code == 200:
            print("📄 HTML 페이지가 정상적으로 로드되었습니다.")
            print(f"📊 응답 크기: {len(response.text)} bytes")
        else:
            print(f"❌ 오류: {response.text[:200]}...")
            
    except requests.exceptions.ConnectionError:
        print("❌ 연결 실패: 서버가 실행 중인지 확인하세요.")
    except Exception as e:
        print(f"❌ 오류: {e}")

if __name__ == "__main__":
    test_main_page()
    test_api_endpoints()
    test_post_endpoints()
    
    print("\n" + "=" * 50)
    print("✅ 모든 테스트 완료!")
    print("=" * 50)
