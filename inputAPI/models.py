from django.db import models
import datetime
from inputAPI.Utils.telegram_api_client import TelegramAPIClient
import abc

LONG_LENGTH = 200
SMALL_LENGTH = 50

chat_types = (("private", "private"),
            ("group", "group"),
            ("supergroup", "supergroup"),
            ("channel", "channel"))

class Downloadable():
    def get_file_path(self, renew=False):
        t = TelegramAPIClient()
        return t.download_file(self.file_id, renew)

    def get_file_url(self):
        t = TelegramAPIClient()
        return t.get_download_link(self.file_id)
    

class Sticker(models.Model, Downloadable):
    file_id = models.CharField(max_length=LONG_LENGTH, primary_key=True)
    file_unique_id = models.CharField(max_length=LONG_LENGTH)
    sticker_type = models.CharField(max_length=SMALL_LENGTH)
    width = models.IntegerField()
    height = models.IntegerField()
    is_animated = models.BooleanField()
    is_video = models.BooleanField()


class Chat(models.Model):
    id = models.BigIntegerField(primary_key=True)
    type = models.CharField(max_length=SMALL_LENGTH, choices=chat_types)
    title = models.CharField(max_length=LONG_LENGTH, null=True)
    username = models.CharField(max_length=LONG_LENGTH, null=True)
    first_name = models.CharField(max_length=LONG_LENGTH, null=True)
    last_name = models.CharField(max_length=LONG_LENGTH, null=True)

    def get_title(self):
        return self.title or self.get_full_name() or self.username or "Title Unknown"

    def get_full_name(self):
        if self.first_name or self.last_name:
            return f"{self.first_name}" + (f" {self.last_name}" if self.last_name else "")
        return None
    
    def get_ordered_messages(self):
        return self.messages.order_by("date").all()

class TelegramUser(models.Model):
    id = models.BigIntegerField(primary_key=True)
    is_bot = models.BooleanField()
    first_name = models.CharField(max_length=LONG_LENGTH)
    last_name = models.CharField(max_length=LONG_LENGTH, null=True)
    username = models.CharField(max_length=LONG_LENGTH, null=True)

    def get_title(self):
        return f"{self.id} - {self.first_name}{f' self.last_name' if self.last_name else ''}{f' - {self.username}' if self.username else ''}"


class Message(models.Model):
    message_id = models.IntegerField()
    chat = models.ForeignKey(Chat, on_delete=models.DO_NOTHING, related_name="messages")
    message_thread_id = models.IntegerField(null=True)
    date = models.PositiveBigIntegerField()
    from_user = models.ForeignKey(TelegramUser, verbose_name="from",
                    on_delete=models.DO_NOTHING, null=True, related_name="messages")
    sender_chat = models.ForeignKey(Chat, on_delete=models.DO_NOTHING, null=True, related_name="messages_sent_on_behalf")
    text = models.TextField(null=True)
    sticker = models.ForeignKey(Sticker, null=True, on_delete=models.DO_NOTHING)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["message_id", "chat"],
                                     name="message_id_and_chat_unique_constraint")
        ]
    
    def get_formatted_date(self):
        return datetime.datetime.fromtimestamp(self.date)
        
    def get_sender(self):
        if self.from_user:
            return self.from_user.get_title()
        elif self.sender_chat:
            return self.sender_chat.get_title()
        else:
            return "Sender Unknown"


class Update(models.Model):
    update_id = models.IntegerField(primary_key=True)
    message = models.ForeignKey(Message, null=True, on_delete=models.CASCADE)
    message_edited = models.BooleanField(null=True)

