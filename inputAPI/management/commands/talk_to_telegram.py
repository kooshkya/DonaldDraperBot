from django.core.management.base import BaseCommand
import requests

class Command(BaseCommand):
    help = "Allows you to talk to the telegram servers"
    
    def handle(self, *args, **options):
        while True:
            self.stdout.write("give me the command:")
            command = input()
            if (command.lower().startswith("quit")):
                return
            