from django.db import models

LONG_LENGTH = 200
SMALL_LENGTH = 50

chat_types = (("pr", "private"),
            ("gr", "group"),
            ("sgr", "supergroup"),
            ("ch", "channel"))

class Chat(models.Model):
    id = models.BigIntegerField(primary_key=True)
    type = models.CharField(max_length=SMALL_LENGTH, choices=chat_types)
    title = models.CharField(max_length=LONG_LENGTH, null=True)
    username = models.CharField(max_length=LONG_LENGTH, null=True)


class TelegramUser(models.Model):
    id = models.BigIntegerField(primary_key=True)
    is_bot = models.BooleanField()
    first_name = models.CharField(max_length=LONG_LENGTH)
    last_name = models.CharField(max_length=LONG_LENGTH, null=True)
    username = models.CharField(max_length=LONG_LENGTH, null=True)

class Message(models.Model):
    message_id = models.IntegerField(primary_key=True)
    date = models.PositiveBigIntegerField()
    from_user = models.OneToOneField(TelegramUser, verbose_name="from",
                    on_delete=models.DO_NOTHING, null=True, related_name="messages")
    chat = models.OneToOneField(Chat, on_delete=models.DO_NOTHING, null=True)
    text = models.TextField(null=True)

    @classmethod
    def does_message_id_exist(cls, message_id):
        return bool(cls.objects.filter(pk=message_id).exists())


class Update(models.Model):
    update_id = models.IntegerField(primary_key=True)
    message = models.ForeignKey(Message, null=True, on_delete=models.CASCADE)
    message_edited = models.BooleanField(null=True)

