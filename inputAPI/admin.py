from django.contrib import admin
from inputAPI.models import Update, Message, Chat, TelegramUser, Sticker

# Register your models here.
admin.site.register(Update)
admin.site.register(Message)
admin.site.register(Chat)
admin.site.register(TelegramUser)
admin.site.register(Sticker)