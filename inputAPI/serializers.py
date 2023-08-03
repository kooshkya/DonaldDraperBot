from rest_framework import serializers
from inputAPI.models import Update, Message, TelegramUser, Chat, Sticker


class StickerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sticker
        fields = "__all__"

    def to_internal_value(self, data):
        if "type" in data:
            data["sticker_type"] = data.pop("type")
        return super().to_internal_value(data)

class StickerLexSerializer(serializers.Serializer):
    file_id = serializers.CharField()
    file_unique_id = serializers.CharField()


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
        fields = ["message_id", "message_thread_id",
                  "date", "text", "from_user", "chat", "sender_chat",
                  "sticker"]

    def attain_sender_id(self, from_data):
        if isinstance(from_data, TelegramUser):
            return from_data.id
        user_lex_serializer = TelegramUserLexSerializer(data=from_data)
        if user_lex_serializer.is_valid():
            query = TelegramUser.objects.filter(pk=user_lex_serializer.validated_data.get("id"))
            if query.exists():
                return query.first().id
            user_serializer = TelegramUserSerializer(data=from_data)
            if user_serializer.is_valid():
                instance = user_serializer.save()
                return instance.id
            else:
                raise serializers.ValidationError({"MessageSerializer": f"The user information supplied is invalid: {user_serializer.errors}"})
        else:
            raise serializers.ValidationError({"MessageSerializer": f"The user id supplied is invalid: {user_lex_serializer.errors}"})
            
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
                raise serializers.ValidationError({"ChatSerializer": "The data supplied for chat is not valid"})
        else:
            raise serializers.ValidationError({"ChatLexSerializer": "the data supplied for chat is not valid."})
    
    def attain_sticker_pk(self, sticker_data):
        if isinstance(sticker_data, Sticker):
            return sticker_data.pk
        sticker_lex_serializer = StickerLexSerializer(data=sticker_data)
        if sticker_lex_serializer.is_valid():
            query = Sticker.objects.filter(pk=sticker_lex_serializer.validated_data.get("file_id"))
            if query.exists():
                return query.first().pk
            sticker_serializer = StickerSerializer(data=sticker_data)
            if sticker_serializer.is_valid():
                instance = sticker_serializer.save()
                return instance.pk
            else:
                raise serializers.ValidationError({"StickerSerializer": f"invalid sticker data: {sticker_serializer.errors}"})
        else:
            raise serializers.ValidationError({"StickerLexSerializer": f"file_id and file_unique_id not given or invalid: {sticker_lex_serializer.errors}"})
        

    def to_internal_value(self, data):
        if "from" in data:
            data["from_user"] = data.pop("from")
        if "from_user" in data:
            from_data = data.get("from_user")
            data["from_user"] = self.attain_sender_id(from_data)
        if "chat" in data:
            data["chat"] = self.attain_chat_id(data.get("chat"))
        if "sender_chat" in data:
            data["sender_chat"] = self.attain_chat_id(data.get("sender_chat"))
        if "sticker" in data:
            data["sticker"] = self.attain_sticker_pk(data.get("sticker"))
        return super().to_internal_value(data)


class UpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Update
        fields = ["update_id", "message", "message_edited"]

    def calculate_message_field(self, message_edited, message_data):
        message_serializer = MessageSerializer(data=message_data)
        if message_serializer.is_valid():
            id = message_serializer.validated_data.get("message_id")
            chat_id = message_serializer.validated_data.get("chat").id
            query = Message.objects.filter(message_id=id, chat=chat_id)
            if query.exists():
                instance = query.first()
                if message_edited:
                    validated_data = message_serializer.validated_data
                    for field in validated_data:
                        if hasattr(instance, field):
                            setattr(instance, field, validated_data.get(field))
                    instance.save()
                    return instance.id
                else:
                    return instance.pk
            else:
                msg = message_serializer.save()
                return msg.id
        else:
            raise serializers.ValidationError(
                f"UpdateSerializer: the message data supplied is invalid: {message_serializer.errors}")

    def to_internal_value(self, data):
        if "message" in data or "edited_message" in data:
            message_edited = "edited_message" in data
            data["message_edited"] = message_edited
            message_data = data.get("message", data.get("edited_message"))
            data["message"] = self.calculate_message_field(message_edited, message_data)
        if "channel_post" in data or "edited_channel_post" in data:
            message_edited = "edited_channel_post" in data
            data["message_edited"] = message_edited
            message_data = data.get("channel_post", data.get("edited_channel_post"))
            data["message"] = self.calculate_message_field(message_edited, message_data)
        return super().to_internal_value(data)
