from django.shortcuts import render
import requests
from django.http import JsonResponse

# Create your views here.

FASTAPI_URL = "http://localhost:8000/api/fastapi/ask"

def chatbot_view(request):
    return render(request, "chatbot/chatbot.html") # html 렌더링

def chatbot_ask(request):
    question = request.GET.get("question","") # 사용자가 입력한 질문 불러오기

    if not question:
        return JsonResponse({'error': "질문이 없습니다."}, status = 400)
    
    try:
        response = requests.get(FASTAPI_URL, params={"question": question})
        data = response.json()
        return JsonResponse(data)
    except requests.RequestException as e:
        return JsonResponse({"error": str(e)}, status = 500)
