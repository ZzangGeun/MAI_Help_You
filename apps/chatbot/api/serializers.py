"""
챗봇 API 시리얼라이저 (도메인 전용)
"""
from rest_framework import serializers


class ChatbotAskRequestSerializer(serializers.Serializer):
    """챗봇 질문 요청 데이터"""
    question = serializers.CharField(
        max_length=1000, 
        help_text="사용자 질문",
        error_messages={
            'required': '질문이 필요합니다.',
            'blank': '질문을 입력해주세요.',
        }
    )
    user_id = serializers.CharField(
        max_length=100, 
        required=False, 
        help_text="사용자 ID (선택사항, 없으면 세션 기반으로 생성)"
    )

    def validate_question(self, value):
        """질문 유효성 검사"""
        if not value.strip():
            raise serializers.ValidationError("질문을 입력해주세요.")
        return value.strip()


class ChatbotAskResponseSerializer(serializers.Serializer):
    """챗봇 질문 응답 데이터"""
    response = serializers.CharField(help_text="AI 응답")
    sources = serializers.ListField(
        child=serializers.CharField(),
        help_text="참조된 소스 목록",
        required=False
    )
    has_rag = serializers.BooleanField(help_text="RAG 검색 여부")
    status = serializers.CharField(help_text="응답 상태")
    user_id = serializers.CharField(help_text="사용자 ID")


class ChatHistoryItemSerializer(serializers.Serializer):
    """개별 채팅 히스토리 아이템"""
    message_type = serializers.ChoiceField(
        choices=['user', 'assistant'],
        help_text="메시지 타입"
    )
    content = serializers.CharField(help_text="메시지 내용")
    timestamp = serializers.DateTimeField(help_text="생성 시간")


class ChatbotHistoryResponseSerializer(serializers.Serializer):
    """챗봇 히스토리 응답 데이터"""
    history = ChatHistoryItemSerializer(many=True, help_text="채팅 히스토리")
    status = serializers.CharField(help_text="응답 상태")
    user_id = serializers.CharField(help_text="사용자 ID")


class ChatbotClearHistoryRequestSerializer(serializers.Serializer):
    """히스토리 삭제 요청 데이터"""
    user_id = serializers.CharField(
        max_length=100, 
        required=False,
        help_text="사용자 ID (선택사항)"
    )


class ChatbotClearHistoryResponseSerializer(serializers.Serializer):
    """히스토리 삭제 응답 데이터"""
    message = serializers.CharField(help_text="응답 메시지")
    status = serializers.CharField(help_text="응답 상태")
    user_id = serializers.CharField(help_text="사용자 ID")


class ChatbotHealthCheckResponseSerializer(serializers.Serializer):
    """헬스체크 응답 데이터"""
    status = serializers.ChoiceField(
        choices=['healthy', 'unhealthy'],
        help_text="서비스 상태"
    )
    timestamp = serializers.DateTimeField(help_text="체크 시간")
    details = serializers.DictField(
        required=False,
        help_text="상세 정보"
    )
