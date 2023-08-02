from django.test import TestCase

# Create your tests here.
from inputAPI.serializers import UpdateSerializer
from inputAPI.models import *
from inputAPI.Utils.telegram_api_client import TelegramAPIClient
from rest_framework.parsers import JSONParser
import io
t = TelegramAPIClient()
r = t.call_get_format_function("getUpdates?limit=5")
raw = r.content
i = io.BytesIO(raw)
d = JSONParser().parse(i)
dd = d["result"][2]
u = UpdateSerializer(data=dd)
u.is_valid()
u.validated_data