"""
회원 가입/인증 API 시리얼라이저 (signup 도메인)
"""
from rest_framework import serializers


class UserRegistrationSerializer(serializers.Serializer):
    """사용자 회원가입 요청"""
    username = serializers.CharField(max_length=50, help_text="사용자 아이디")
    password = serializers.CharField(max_length=128, write_only=True, help_text="비밀번호")
    email = serializers.EmailField(help_text="이메일 주소")
    nickname = serializers.CharField(max_length=50, help_text="닉네임")
    nexon_api_key = serializers.CharField(max_length=200, required=False, help_text="넥슨 API 키 (선택사항)")

    def validate_username(self, value):
        if len(value) < 3:
            raise serializers.ValidationError("사용자명은 3자 이상이어야 합니다.")
        return value

    def validate_password(self, value):
        if len(value) < 6:
            raise serializers.ValidationError("비밀번호는 6자 이상이어야 합니다.")
        return value


class UserLoginSerializer(serializers.Serializer):
    """사용자 로그인 요청"""
    username = serializers.CharField(max_length=50, help_text="사용자 아이디")
    password = serializers.CharField(max_length=128, write_only=True, help_text="비밀번호")


class UserResponseSerializer(serializers.Serializer):
    """사용자 정보 응답"""
    id = serializers.CharField(help_text="사용자 ID")
    username = serializers.CharField(help_text="사용자명")
    email = serializers.EmailField(help_text="이메일")
    nickname = serializers.CharField(help_text="닉네임")
    has_nexon_api = serializers.BooleanField(help_text="넥슨 API 키 보유 여부")
    created_at = serializers.DateTimeField(required=False, help_text="가입일")


class AuthResponseSerializer(serializers.Serializer):
    """인증 응답 (회원가입/로그인)"""
    user = UserResponseSerializer(help_text="사용자 정보")
    token = serializers.CharField(required=False, help_text="인증 토큰 (JWT 등)")
    message = serializers.CharField(help_text="응답 메시지")
    status = serializers.CharField(help_text="응답 상태")
