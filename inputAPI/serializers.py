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
    from_user = TelegramUserSerializer(required=False)

    def validate(self, data):
        if "from_user" in data:
            user_data = data.get("from_user")
            TelegramUser.create_or_update_user(user_data)
        return data

    class Meta:
        model = Message
        fields = ["message_id", "date", "text", "from_user"]

    def update():
        raise NotImplemented("Not implemented!")
    
    def create():
        raise NotImplemented("Not implemented!")


class UpdateSerializer(serializers.ModelSerializer):
    update_id = serializers.IntegerField()
    message = MessageSerializer(required=False)
    edited_message = MessageSerializer(required=False)

    class Meta:
        model = Update
        fields = ["update_id", "message", "message_edited", "edited_message"]
    

    def fix_message_fields_in_validated_data(self, validated_data):
        if "message" in validated_data:
            validated_data["message_edited"] = False
            message_data = validated_data.get("message")
        if "edited_message" in validated_data:
            validated_data["message_edited"] = True
            message_data = validated_data.get("edited_message")
            validated_data.pop("edited_message")

        message = Message.create_or_update_message(message_data)
        validated_data["message"] = message


    def create(self, validated_data):
        self.fix_message_fields_in_validated_data(validated_data)
        query_set = Update.objects.filter(pk=validated_data.get("update_id"))
        if query_set.exists():
            print("Update already existed, returning original instance:")
        new_update = Update(**validated_data)
        new_update.save()

        return new_update

