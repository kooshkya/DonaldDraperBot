from rest_framework import serializers
from inputAPI.models import Update, Message, TelegramUser, Chat


class ChatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chat
        fields = ["id", "type", "title", "username", "first_name", "last_name"]

class ChatLexSerializer(serializers.Serializer):
    id = serializers.IntegerField()

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
        fields = ["message_id", "date", "text", "from_user", "chat"]

    def attain_sender_id(self, from_data):
        if isinstance(from_data, TelegramUser):
            return from_data.id
        user_lex_serializer = TelegramUserLexSerializer(data=from_data)
        if user_lex_serializer.is_valid(raise_exception=True):
            query = TelegramUser.objects.filter(pk=user_lex_serializer.validated_data.get("id"))
            if query.exists():
                return query.first().id
            user_serializer = TelegramUserSerializer(data=from_data)
            if user_serializer.is_valid(raise_exception=True):
                instance = user_serializer.save()
                return instance.id
            
    def attain_chat_id(self, chat_data):
        if isinstance(chat_data, Chat):
            return chat_data.id
        chat_lex_serializer = ChatLexSerializer(data=chat_data)
        if chat_lex_serializer.is_valid():
            id = chat_lex_serializer.validated_data.get("id")
            query = Chat.objects.filter(pk=id)
            if query.exists():
                return query.first().id
            chat_serializer = ChatSerializer(data=chat_data)
            if chat_serializer.is_valid():
                instance = chat_serializer.save()
                return instance.id
            else:
                print(chat_data)
                print(chat_serializer.errors)
                raise serializers.ValidationError({"ChatSerializer": "The data supplied for chat is not valid"})
        else:
            raise serializers.ValidationError({"ChatLexSerializer": "the data supplied for chat is not valid."})
        
    def to_internal_value(self, data):
        if "from" in data:
            data["from_user"] = data.pop("from")
        if "from_user" in data:
            from_data = data.get("from_user")
            data["from_user"] = self.attain_sender_id(from_data)
        if "chat" in data:
            data["chat"] = self.attain_chat_id(data.get("chat"))
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
                    validated_data = message_serializer.validated_data
                    for field in validated_data:
                        if hasattr(instance, field):
                            setattr(instance, field, validated_data.get(field))
                    instance.save()
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
