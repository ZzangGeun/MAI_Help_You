from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from core.services import get_notice_list, get_ranking_list
import logging

logger = logging.getLogger(__name__)

class HomeDataAPIView(APIView):
    """
    메인 페이지에 필요한 데이터(공지사항, 랭킹 등)를 반환하는 API
    """
    def get(self, request):
        try:
            # 기존 서비스 함수 활용
            notice = get_notice_list() or {}
            ranking = get_ranking_list() or {}
            
            # 데이터 추출 로직
            def extract_list(data, keys):
                if not data: return []
                if isinstance(data, dict):
                    for key in keys:
                        if key in data and isinstance(data[key], list):
                            return data[key]
                if isinstance(data, list): return data
                return []

            # 공지사항 추출
            notice_events = extract_list(notice.get('notice_event'), ['event_notice'])
            notice_updates = extract_list(notice.get('notice_update'), ['update_notice'])
            notice_cashshops = extract_list(notice.get('notice_cashshop'), ['cashshop_notice'])
            
            # 랭킹 추출
            ranking_data = ranking.get('overall_ranking', {})
            ranking_list = []
            if isinstance(ranking_data, dict) and 'ranking' in ranking_data:
                ranking_list = ranking_data['ranking']
            elif isinstance(ranking_data, list):
                ranking_list = ranking_data
            
            # 데이터 가공
            processed_data = {
                "notices": {
                    "updates": notice_updates[:5],
                    "events": notice_events[:5],
                    "cashshop": notice_cashshops[:5],
                },
                "ranking": ranking_list[:10]
            }
            
            return Response(processed_data)
            
        except Exception as e:
            logger.error(f"Home API Error: {e}")
            # 에러 발생 시 빈 데이터 반환하여 프론트엔드 에러 방지
            return Response({
                "notices": {"updates": [], "events": [], "cashshop": []},
                "ranking": []
            })
