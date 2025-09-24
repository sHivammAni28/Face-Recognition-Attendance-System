from django.core.management.base import BaseCommand
from apps.authentication.models import User


class Command(BaseCommand):
    help = 'Create a default admin user'

    def handle(self, *args, **options):
        if not User.objects.filter(email='admin@attendance.com').exists():
            User.objects.create_user(
                username='admin',
                email='admin@attendance.com',
                password='admin123',
                first_name='System',
                last_name='Administrator',
                role='admin',
                is_staff=True,
                is_superuser=True
            )
            self.stdout.write(
                self.style.SUCCESS('Successfully created admin user')
            )
            self.stdout.write('Email: admin@attendance.com')
            self.stdout.write('Password: admin123')
        else:
            self.stdout.write(
                self.style.WARNING('Admin user already exists')
            )