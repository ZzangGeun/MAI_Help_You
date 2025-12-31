from django.contrib.auth import get_user_model, authenticate
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    """
    로그인 성공 시 사용자 정보를 반환하기 위한 Serializer
    API 명세서의 User 스키마와 필드를 일치시킵니다.
    """
    class Meta:
        model = User
        # API 명세서(models.yaml)에 정의된 필드들을 포함합니다.
        fields = [
            'id', 'username', 'email', 'nickname', 'profile_image', 
            'provider', 'is_active', 'last_login', 'created_at', 'updated_at'
        ]
        read_only_fields = fields


class LoginSerializer(serializers.Serializer):
    """
    로그인 처리를 위한 Serializer
    아이디와 비밀번호를 받아 유효성을 검증하고 토큰을 생성합니다.
    """
    username = serializers.CharField(required=True, write_only=True)
    password = serializers.CharField(required=True, write_only=True, style={'input_type': 'password'})

    def validate(self, data):
        user = authenticate(username=data['username'], password=data['password'])
        if user is None:
            raise serializers.ValidationError("아이디 또는 비밀번호가 일치하지 않습니다.")

        # JWT 토큰 생성
        refresh = RefreshToken.for_user(user)
        
        # API 명세서에 맞는 응답 데이터 구성
        return {
            'user': UserSerializer(user).data,
            'tokens': {
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            }
        }