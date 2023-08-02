from rest_framework import serializers
from inputAPI.models import Update, Message, TelegramUser

class TelegramUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = TelegramUser
        fields = ["id", "is_bot", "first_name", "last_name", "username"]


class MessageSerializer(serializers.ModelSerializer):
    # In order to keep the serializer from throwing errors
    #  when an already existing id is supplied, this field has been overridden
    message_id = serializers.IntegerField()

    class Meta:
        model = Message
        fields = ["message_id", "date", "text"]


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
                    if new_serializer.is_valid():
                        msg = new_serializer.save()
                        return msg.message_id
                    else:
                        raise serializers.ValidationError("Error while trying to update pre-existing message using serializers.")
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
