from django.shortcuts import render
from django.views.generic import ListView
from inputAPI import models

# Create your views here.
class ChatListView(ListView):
    model = models.Chat
    template_name = "WebClient/ChatList.html"