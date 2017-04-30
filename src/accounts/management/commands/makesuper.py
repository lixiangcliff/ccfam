from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from src.ccfam import settings

class Command(BaseCommand):
    def handle(self, *args, **options):
        User = get_user_model()
        if User.objects.filter(username__exact="cliff").count() == 0:
            User.objects.create_superuser("cliff", "lixiang.cliff@gmail.com", "test")
        else:
            print('account cliff already exists. do nothing.')
