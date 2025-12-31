from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from .models import UserProfile
import re

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['maple_nickname', 'nexon_api_key']

class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'profile']

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True)
    maple_nickname = serializers.CharField(write_only=True, max_length=12)
    nexon_api_key = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ['username', 'password', 'confirm_password', 'maple_nickname', 'nexon_api_key']

    def validate_username(self, value):
        if not re.match(r'^[a-zA-Z0-9_]{6,20}$', value):
            raise serializers.ValidationError("아이디는 6~20자의 영문자, 숫자, 밑줄(_)만 사용할 수 있습니다.")
        return value

    def validate_maple_nickname(self, value):
        if UserProfile.objects.filter(maple_nickname=value).exists():
            raise serializers.ValidationError("이미 사용 중인 메이플 닉네임입니다.")
        return value

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "비밀번호가 일치하지 않습니다."})
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        maple_nickname = validated_data.pop('maple_nickname')
        nexon_api_key = validated_data.pop('nexon_api_key', '')

        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password']
        )

        UserProfile.objects.create(
            user=user,
            maple_nickname=maple_nickname,
            nexon_api_key=nexon_api_key
        )
        
        return user

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if user:
                if not user.is_active:
                    raise serializers.ValidationError("비활성화된 계정입니다.")
                data['user'] = user
            else:
                raise serializers.ValidationError("아이디 또는 비밀번호가 잘못되었습니다.")
        else:
            raise serializers.ValidationError("아이디와 비밀번호를 모두 입력해주세요.")
        return data
