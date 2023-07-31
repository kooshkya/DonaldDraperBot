from django.core.management.base import BaseCommand
from inputAPI.Utils.telegram_api_client import TelegramAPIClient
import requests

class Command(BaseCommand):
    help = "Allows you to talk to the telegram servers"
    
    def handle(self, *args, **options):
        while True:
            self.stdout.write("give me the command:")
            command = input()
            if (command.lower().startswith("quit")):
                return
            client = TelegramAPIClient()
            response = client.convert_response_to_pretty_string(
                client.call_get_format_function(command)
                )
            self.stdout.write(response)
        
            