from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import LoginSerializer

class LoginView(APIView):
    """
    사용자 로그인을 처리하는 API View
    """
    permission_classes = [AllowAny] # 로그인 API는 누구나 접근 가능해야 함

    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        
        if serializer.is_valid():
            # Serializer의 validate 메서드에서 생성된 데이터를 응답으로 반환
            # API 명세서의 SuccessResponse 형식에 맞춤
            response_data = {
                "success": True,
                "data": serializer.validated_data
            }
            return Response(response_data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(APIView):
    """
    사용자 로그아웃을 처리하는 API View
    Refresh Token을 받아 블랙리스트에 추가합니다.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            refresh_token = request.data["refresh"]
            if not refresh_token:
                raise ValueError()
                
            token = RefreshToken(refresh_token)
            token.blacklist()

            # API 명세서의 SuccessResponse 형식에 맞춤
            return Response({"success": True, "message": "성공적으로 로그아웃되었습니다."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"success": False, "error": "유효하지 않은 토큰이거나 토큰이 제공되지 않았습니다."}, status=status.HTTP_400_BAD_REQUEST)