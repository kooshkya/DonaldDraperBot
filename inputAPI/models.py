from django.db import models
import datetime


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

    @classmethod
    def create_or_update_user(cls, data: dict):
        assert "id" in data
        query = cls.objects.filter(pk=data.get("id"))
        if not query.exists:
            return cls.objects.create(**data)
        else:
            instance = query.first()
            for field in data:
                if hasattr(instance, field):
                    setattr(instance, field, data.get(field))
            instance.save()
            return instance



class Message(models.Model):
    message_id = models.IntegerField(primary_key=True)
    date = models.PositiveBigIntegerField()
    from_user = models.ForeignKey(TelegramUser, verbose_name="from",
                    on_delete=models.DO_NOTHING, null=True, related_name="messages")
    chat = models.ForeignKey(Chat, on_delete=models.DO_NOTHING, null=True)
    text = models.TextField(null=True)
    
    def get_formatted_date(self):
        return datetime.datetime.fromtimestamp(self.date)
    
    @classmethod
    def create_or_update_message(cls, data: dict):
        assert "message_id" in data
        query = cls.objects.filter(pk=data.get("message_id"))
        if not query.exists():
            return cls.objects.create(**data)
        else:
            instance = query.first()
            for field in data:
                if hasattr(instance, field):
                    setattr(instance, field, data.get(field))
            instance.save()
            return instance


class Update(models.Model):
    update_id = models.IntegerField(primary_key=True)
    message = models.ForeignKey(Message, null=True, on_delete=models.CASCADE)
    message_edited = models.BooleanField(null=True)

