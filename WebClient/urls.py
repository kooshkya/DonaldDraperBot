from django.urls import path
from WebClient import views

urlpatterns = [
    path("", views.ChatListView.as_view())
]