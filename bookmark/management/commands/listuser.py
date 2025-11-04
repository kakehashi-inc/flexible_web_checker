from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Lists all user accounts with their usernames, emails, and permission levels'

    def handle(self, *args, **options):
        users = User.objects.all().order_by('username')
        
        if not users:
            self.stdout.write(self.style.WARNING('No user accounts found.'))
            return
        
        self.stdout.write(self.style.SUCCESS(f'Found {users.count()} user account(s):'))
        
        for user in users:
            permission_level = []
            if user.is_superuser:
                permission_level.append('スーパーユーザー')
            if user.is_staff:
                permission_level.append('スタッフ')
            if not user.is_superuser and not user.is_staff:
                permission_level.append('一般ユーザー')
                
            self.stdout.write(f'ユーザー名: {user.username}')
            self.stdout.write(f'メールアドレス: {user.email}')
            self.stdout.write(f'権限レベル: {", ".join(permission_level)}')
            self.stdout.write(f'アクティブ: {user.is_active}')
            self.stdout.write('-' * 40)
