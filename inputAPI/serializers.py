from rest_framework import serializers
from inputAPI.models import Update, Message, TelegramUser

class TelegramUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = TelegramUser
        fields = ["id", "is_bot", "first_name", "last_name", "username"]

class TelegramUserLexSerializer(serializers.Serializer):
    id = serializers.IntegerField()


class MessageSerializer(serializers.ModelSerializer):
    # In order to keep the serializer from throwing errors
    #  when an already existing id is supplied, this field has been overridden
    message_id = serializers.IntegerField()

    class Meta:
        model = Message
        fields = ["message_id", "date", "text", "from_user"]

    def attain_sender_id(self, from_data):
        user_lex_serializer = TelegramUserLexSerializer(data=from_data)
        if user_lex_serializer.is_valid(raise_exception=True):
            query = TelegramUser.objects.filter(pk=user_lex_serializer.validated_data.get("id"))
            if query.exists():
                return query.first().id
            user_serializer = TelegramUserSerializer(data=from_data)
            if user_serializer.is_valid(raise_exception=True):
                instance = user_serializer.save()
                return instance.id

    def to_internal_value(self, data):
        print(f"incoming data is {data}")
        if "from" in data:
            data["from_user"] = data.pop("from")
        if "from_user" in data:
            from_data = data.get("from_user")
            data["from_user"] = self.attain_sender_id(from_data)
        print(f"outgoing data is {data}")
        return super().to_internal_value(data)

class UpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Update
        fields = ["update_id", "message", "message_edited"]

    def calculate_message_field(self, message_edited, message_data):
        message_serializer = MessageSerializer(data=message_data)
        if message_serializer.is_valid(raise_exception=True):
            id = message_serializer.validated_data.get("message_id")
            query = Message.objects.filter(pk=id)
            if query.exists():
                instance = query.first()
                if message_edited:
                    new_serializer = MessageSerializer(instance, 
                                                       data=message_serializer.validated_data)
                    if new_serializer.is_valid(raise_exception=True):
                        msg = new_serializer.save()
                        return msg.message_id
                else:
                    return instance.message_id
            else:
                msg = message_serializer.save()
                return msg.message_id

    def to_internal_value(self, data):
        if "message" in data or "edited_message" in data:
            message_edited = "edited_message" in data
            data["message_edited"] = message_edited
            message_data = data.get("message", data.get("edited_message"))
            data["message"] = self.calculate_message_field(message_edited, message_data)
        return super().to_internal_value(data)
