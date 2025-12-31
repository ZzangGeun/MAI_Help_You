from typing import List, Dict, Any
from datetime import datetime, timezone, timedelta


def clean_date_format(date_str: str) -> str:
    """ISO 8601 형식 문자열을 'YYYY.MM.DD' 형식으로 변환"""
    try:
        # None 또는 빈 문자열 체크
        if not date_str:
            return "날짜 정보 없음"
        # T, +09:00 등의 정보를 포함하는 ISO 형식 문자열을 파싱
        dt = datetime.fromisoformat(date_str.replace("T", " "))
        # 날짜만 'YYYY.MM.DD' 형식으로 포매팅
        return dt.strftime('%Y.%m.%d')
    except (ValueError, TypeError, AttributeError):
        return "날짜 정보 없음"

def transform_to_carousel_format(api_data: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
    """
    API에서 가져온 복잡한 공지 데이터를 프론트엔드 캐러셀 형식으로 변환합니다.
    """
    if api_data is None:
        return {"events": [], "cashItems": []}
    
    events = []
    cash_items = []

    # 1. 이벤트 공지 (notice_event) 매핑
    # 데이터 구조: api_data['notice_event']['event_notice']
    event_list = api_data.get('notice_event', {}).get('event_notice', [])
    for item in event_list[:3]:  # 최신 이벤트 3개만 사용 (프론트엔드 예시에 맞춤)
        # 이벤트는 기간이 명시되는 경우가 많으므로 title에서 기간 정보를 추출하거나 date 필드를 활용
        events.append({
            'icon': '⭐', # 아이콘은 임의로 지정하거나 API에서 이미지 정보를 추가해야 함
            'title': item.get('title', '제목 없음'),
            'description': f"공지일: {clean_date_format(item.get('date', ''))}",
            'url': item.get('url', '#'),
            # 추가적으로 이벤트 기간(start_date, end_date) 필드를 활용하여 description을 풍부하게 할 수 있습니다.
        })
        
    # 2. 캐시샵 공지 (notice_cashshop) 매핑
    # 데이터 구조: api_data['notice_cashshop']['cashshop_notice']
    cashshop_list = api_data.get('notice_cashshop', {}).get('cashshop_notice', [])
    for item in cashshop_list:
        # ongoing_flag가 'true'이거나 아직 판매 종료일이 되지 않은 아이템만 필터링 (선택사항)
        is_ongoing = item.get('ongoing_flag') == 'true' or (
            item.get('date_sale_end') and datetime.fromisoformat(item['date_sale_end'].replace("T", " ")) > datetime.now(timezone.utc)
        )
        
        if is_ongoing:
            sale_end_date = clean_date_format(item.get('date_sale_end', ''))
            
            cash_items.append({
                'image': '💰', # 아이콘 임의 지정
                'title': item.get('title', '제목 없음'),
                # 판매 종료일이 있으면 부제로 표시
                'subtitle': f"판매 종료일: {sale_end_date}" if sale_end_date != "날짜 정보 없음" else "상시 판매",
                'url': item.get('url', '#'),
            })

    # 최신 캐시샵 아이템 5개만 사용
    return {
        "events": events[:5], 
        "cashItems": cash_items[:5]
    }

