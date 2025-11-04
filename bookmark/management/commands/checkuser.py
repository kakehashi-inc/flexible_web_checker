import getpass
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model, authenticate

User = get_user_model()

class Command(BaseCommand):
    help = 'Checks if a user with the given username and password exists and can authenticate'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, help='Username to check')
        parser.add_argument('--password', type=str, help='Password to check')

    def handle(self, *args, **options):
        username = options.get('username')
        password = options.get('password')
        
        if not username:
            username = input('Enter username: ')
        
        if not password:
            password = getpass.getpass('Enter password: ')
        
        try:
            user = User.objects.get(username=username)
            self.stdout.write(self.style.SUCCESS(f'User "{username}" exists.'))
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'User "{username}" does not exist.'))
            return
        
        if not user.is_active:
            self.stdout.write(self.style.WARNING(f'User "{username}" is inactive.'))
            return
        
        auth_user = authenticate(username=username, password=password)
        if auth_user is not None:
            permission_level = []
            if auth_user.is_superuser:
                permission_level.append('Superuser')
            if auth_user.is_staff:
                permission_level.append('Staff')
            if not auth_user.is_superuser and not auth_user.is_staff:
                permission_level.append('Regular User')
                
            self.stdout.write(self.style.SUCCESS(f'Authentication successful: Password for user "{username}" is correct.'))
            self.stdout.write(f'Username: {auth_user.username}')
            self.stdout.write(f'Email: {auth_user.email}')
            self.stdout.write(f'Permission Level: {", ".join(permission_level)}')
            self.stdout.write(f'Active: {auth_user.is_active}')
        else:
            self.stdout.write(self.style.ERROR(f'Authentication failed: Password for user "{username}" is incorrect.'))
