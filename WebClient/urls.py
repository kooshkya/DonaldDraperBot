from django.urls import path, register_converter
from WebClient import views

app_name = "WebClient"

class SignedIntConverter:
    regex = "-?[0-9]+"

    def to_python(self, value):
        return int(value)
    
    def to_url(self, value):
        return str(value)

register_converter(SignedIntConverter, "signed_int")


urlpatterns = [
    path("", views.ChatListView.as_view(), name="chat_list"),
    path("chats/<signed_int:chat_id>/", views.ChatView.as_view(), name="chat_detail"),
]