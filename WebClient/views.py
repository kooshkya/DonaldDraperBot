from typing import Any, Dict
from django.shortcuts import render
from django.views.generic import ListView, DetailView
from inputAPI import models

# Create your views here.
class ChatListView(ListView):
    model = models.Chat
    template_name = "WebClient/ChatList.html"


class ChatView(DetailView):
    model = models.Chat
    template_name = "WebClient/Chat.html"
    pk_url_kwarg = "chat_id"
    context_object_name = "chat"
