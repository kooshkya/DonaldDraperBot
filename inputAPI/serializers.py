from rest_framework import serializers
from inputAPI.models import Update, Message


class MessageSerializer(serializers.ModelSerializer):
    message_id = serializers.IntegerField(null=True)
    class Meta:
        model = Message
        fields = ["message_id", "date", "text"]


class UpdateSerializer(serializers.ModelSerializer):
    message = MessageSerializer(required=False)
    edited_message = MessageSerializer(required=False)

    class Meta:
        model = Update
        fields = ["update_id", "message", "message_edited", "edited_message"]

    def get_message_or_create_it(self, data):
        id = data.get("message_id")
        query_set = Message.objects.filter(pk=id)
        if not query_set.exists():
            message = Message.objects.create(**data)
        else:
            message = query_set.first()
        return message
    

    def fix_message_fields_in_validated_data(self, validated_data):
        if "message" in validated_data:
            validated_data["message_edited"] = False
            message_data = validated_data.get("message")
            message = self.get_message_or_create_it(message_data)
            validated_data["message"] = message
        if "edited_message" in validated_data:
            validated_data["message_edited"] = True
            message_data = validated_data.get("edited_message")
            message = self.get_message_or_create_it(message_data)
            validated_data.pop("edited_message")
            validated_data["message"] = message


    def create(self, validated_data):
        self.fix_message_fields_in_validated_data(validated_data)
        query_set = Update.objects.filter(pk=validated_data.get("update_id"))
        if not query_set.exists():
            new_update = Update.objects.create(**validated_data)
        else:
            new_update = query_set.first()
        return new_update

