from django.shortcuts import render, redirect
from .get_nexon_api import get_notice_list
import requests
from django.http import JsonResponse
import asyncio
import aiohttp
import time


def main_page(request):

    notice = get_notice_list()

    context = {
        **notice,
        'timestamp': int(time.time())  # 캐시 방지용 타임스탬프
    }
    
    return render(request, 'main_page/main_page.html', context)

def character_info_view(request):
    return render(request, "character_info/character_info.html")
