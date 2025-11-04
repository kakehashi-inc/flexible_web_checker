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
            username = input('ユーザー名を入力してください: ')
        
        if not password:
            password = getpass.getpass('パスワードを入力してください: ')
        
        try:
            user = User.objects.get(username=username)
            self.stdout.write(self.style.SUCCESS(f'ユーザー "{username}" が存在します。'))
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'ユーザー "{username}" は存在しません。'))
            return
        
        if not user.is_active:
            self.stdout.write(self.style.WARNING(f'ユーザー "{username}" は非アクティブです。'))
            return
        
        auth_user = authenticate(username=username, password=password)
        if auth_user is not None:
            permission_level = []
            if auth_user.is_superuser:
                permission_level.append('スーパーユーザー')
            if auth_user.is_staff:
                permission_level.append('スタッフ')
            if not auth_user.is_superuser and not auth_user.is_staff:
                permission_level.append('一般ユーザー')
                
            self.stdout.write(self.style.SUCCESS(f'認証成功: ユーザー "{username}" のパスワードは正しいです。'))
            self.stdout.write(f'ユーザー名: {auth_user.username}')
            self.stdout.write(f'メールアドレス: {auth_user.email}')
            self.stdout.write(f'権限レベル: {", ".join(permission_level)}')
            self.stdout.write(f'アクティブ: {auth_user.is_active}')
        else:
            self.stdout.write(self.style.ERROR(f'認証失敗: ユーザー "{username}" のパスワードが正しくありません。'))
