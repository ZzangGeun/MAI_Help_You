from django.shortcuts import render, redirect
import json
import os
from django.conf import settings
from django.urls import reverse

async def character_info(request):
    return render(request, 'character_info/character_info.html')


