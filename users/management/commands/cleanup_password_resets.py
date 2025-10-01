from django.core.management.base import BaseCommand
from django.utils import timezone
from users.models import PasswordReset

class Command(BaseCommand):
    help = "Elimina tokens de restablecimiento expirados"

    def handle(self, *args, **options):
        now = timezone.now()
        deleted, _ = PasswordReset.objects.filter(expires_at__lt=now).delete()
        self.stdout.write(self.style.SUCCESS(f"Eliminados expirados: {deleted}"))