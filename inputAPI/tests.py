from django.test import TestCase

# Create your tests here.
from inputAPI.serializers import UpdateSerializer
from inputAPI.models import *
from inputAPI.Utils.telegram_api_client import TelegramAPIClient
from rest_framework.parsers import JSONParser
import io
t = TelegramAPIClient()
r = t.call_get_format_function("getUpdates?limit=10")
raw = r.content
i = io.BytesIO(raw)
d = JSONParser().parse(i)
jj = 5
dd = d["result"][jj]
print(dd)
u = UpdateSerializer(data=dd)
print(u.is_valid())
print(u.validated_data)



from inputAPI.serializers import UpdateSerializer
from inputAPI.models import *
from inputAPI.Utils.telegram_api_client import TelegramAPIClient
from rest_framework.parsers import JSONParser
import io
t = TelegramAPIClient()
def func(jj):
    r = t.call_get_format_function("getUpdates?limit=5")
    raw = r.content
    i = io.BytesIO(raw)
    d = JSONParser().parse(i)
    dd = d["result"][jj]
    u = UpdateSerializer(data=dd)
    print(u.is_valid())
    print(u.validated_data)
    return u


u = func(0)


from inputAPI.models import *
Update.objects.all().delete()
Message.objects.all().delete()
TelegramUser.objects.all().delete()