"""
테스트 헬퍼 유틸리티 모듈

공통으로 사용되는 테스트 함수들을 모아놓은 모듈입니다.
"""

import json
import os
from pathlib import Path
from datetime import datetime
import requests

def validate_api_response(response_data, expected_keys=None):
    """
    API 응답 데이터 검증
    
    Args:
        response_data: API에서 받은 데이터
        expected_keys: 예상되는 키 목록
    
    Returns:
        dict: 검증 결과
    """
    result = {
        'valid': False,
        'errors': [],
        'warnings': [],
        'info': {}
    }
    
    # 기본 검증
    if response_data is None:
        result['errors'].append("응답 데이터가 None입니다")
        return result
    
    if not isinstance(response_data, dict):
        result['errors'].append(f"응답 데이터가 dict가 아닙니다: {type(response_data)}")
        return result
    
    # 키 검증
    if expected_keys:
        missing_keys = []
        for key in expected_keys:
            if key not in response_data:
                missing_keys.append(key)
        
        if missing_keys:
            result['errors'].append(f"누락된 키: {missing_keys}")
    
    # 데이터 정보 수집
    result['info']['keys'] = list(response_data.keys())
    result['info']['data_types'] = {key: type(value).__name__ for key, value in response_data.items()}
    
    # 리스트 데이터 검증
    for key, value in response_data.items():
        if isinstance(value, list):
            result['info'][f'{key}_count'] = len(value)
            if len(value) == 0:
                result['warnings'].append(f"{key} 리스트가 비어있습니다")
            elif len(value) > 0:
                # 첫 번째 항목의 구조 확인
                first_item = value[0]
                if isinstance(first_item, dict):
                    result['info'][f'{key}_structure'] = list(first_item.keys())
    
    # 에러가 없으면 유효한 것으로 판단
    if not result['errors']:
        result['valid'] = True
    
    return result

def save_test_result(test_name, result_data, save_dir="tests/data"):
    """
    테스트 결과를 파일로 저장
    
    Args:
        test_name: 테스트 이름
        result_data: 저장할 데이터
        save_dir: 저장할 디렉토리
    """
    project_root = Path(__file__).parent.parent.parent
    save_path = project_root / save_dir
    save_path.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{test_name}_{timestamp}.json"
    file_path = save_path / filename
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(result_data, f, indent=2, ensure_ascii=False)
    
    return str(file_path)

def load_test_data(filename, data_dir="tests/data"):
    """
    저장된 테스트 데이터 로드
    
    Args:
        filename: 파일명
        data_dir: 데이터 디렉토리
    
    Returns:
        dict: 로드된 데이터
    """
    project_root = Path(__file__).parent.parent.parent
    file_path = project_root / data_dir / filename
    
    if not file_path.exists():
        return None
    
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def compare_api_responses(old_data, new_data):
    """
    두 API 응답 비교
    
    Args:
        old_data: 이전 응답 데이터
        new_data: 새 응답 데이터
    
    Returns:
        dict: 비교 결과
    """
    result = {
        'identical': False,
        'differences': [],
        'summary': {}
    }
    
    if old_data == new_data:
        result['identical'] = True
        return result
    
    # 구조 비교
    if isinstance(old_data, dict) and isinstance(new_data, dict):
        old_keys = set(old_data.keys())
        new_keys = set(new_data.keys())
        
        if old_keys != new_keys:
            result['differences'].append({
                'type': 'keys_changed',
                'added_keys': list(new_keys - old_keys),
                'removed_keys': list(old_keys - new_keys)
            })
        
        # 공통 키의 값 비교
        common_keys = old_keys & new_keys
        for key in common_keys:
            if old_data[key] != new_data[key]:
                # 리스트인 경우 길이 비교
                if isinstance(old_data[key], list) and isinstance(new_data[key], list):
                    result['differences'].append({
                        'type': 'list_length_changed',
                        'key': key,
                        'old_length': len(old_data[key]),
                        'new_length': len(new_data[key])
                    })
                else:
                    result['differences'].append({
                        'type': 'value_changed',
                        'key': key,
                        'old_value': old_data[key],
                        'new_value': new_data[key]
                    })
    
    result['summary']['total_differences'] = len(result['differences'])
    return result

def format_test_output(test_name, success, details=None):
    """
    테스트 결과를 예쁘게 포맷팅
    
    Args:
        test_name: 테스트 이름
        success: 성공 여부
        details: 상세 정보
    
    Returns:
        str: 포맷된 출력 문자열
    """
    icon = "✅" if success else "❌"
    status = "성공" if success else "실패"
    
    output = f"{icon} {test_name}: {status}\n"
    
    if details:
        for key, value in details.items():
            output += f"   {key}: {value}\n"
    
    return output

def check_environment():
    """
    테스트 환경 확인
    
    Returns:
        dict: 환경 정보
    """
    env_info = {
        'python_version': f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        'nexon_api_key_set': bool(os.getenv('NEXON_API_KEY')),
        'django_available': False,
        'requests_available': False,
        'project_root': str(Path(__file__).parent.parent.parent)
    }
    
    # Django 확인
    try:
        import django
        env_info['django_available'] = True
        env_info['django_version'] = django.get_version()
    except ImportError:
        pass
    
    # requests 확인
    try:
        import requests
        env_info['requests_available'] = True
        env_info['requests_version'] = requests.__version__
    except ImportError:
        pass
    
    return env_info

if __name__ == "__main__":
    # 환경 체크 실행
    print("🔍 테스트 환경 확인")
    print("=" * 40)
    
    env = check_environment()
    for key, value in env.items():
        print(f"{key}: {value}")
