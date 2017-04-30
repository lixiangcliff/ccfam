from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from src.ccfam import settings

class Command(BaseCommand):
    def handle(self, *args, **options):
        User = get_user_model()
        if not User.objects.filter(username__exact="cliff").exists():
            User.objects.create_superuser("cliff", "lixiang.cliff@gmail.com", settings.SUPERUSER_PASSWORD)