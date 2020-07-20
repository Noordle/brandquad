from django.contrib.auth.models import User
from django.core.management import BaseCommand

from processlogs.settings import ADMIN_LOGIN, ADMIN_PASSWORD


class Command(BaseCommand):
	def handle(self, *args, **options):
		if User.objects.filter(username=ADMIN_LOGIN).exists():
			return

		User.objects.create_superuser(
			email='admin@email.com',
			username=ADMIN_LOGIN,
			password=ADMIN_PASSWORD,
		)
