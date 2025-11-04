# Ubuntu/Debian系OS向け Apache + Gunicorn デプロイ手順

## 前提条件

- Ubuntu 20.04/22.04 または Debian 11/12
- Python 3.8以上
- Apache 2.4以上
- Gunicorn

## インストール手順

### 1. 必要なパッケージのインストール

```bash
# システムの更新
sudo apt update
sudo apt upgrade -y

# 必要なパッケージのインストール
sudo apt install -y python3 python3-pip python3-dev apache2 apache2-dev build-essential git

# Pythonの仮想環境ツールのインストール
sudo pip3 install virtualenv
```

### 2. アプリケーションのデプロイ

```bash
# アプリケーションディレクトリの作成
sudo mkdir -p /var/www/flexible_web_checker
sudo chown -R $USER:$USER /var/www/flexible_web_checker

# Gitリポジトリのクローン
cd /var/www/flexible_web_checker
git clone https://github.com/kakehashi-inc/flexible_web_checker.git .

# 仮想環境の作成とアクティベート
python3 -m virtualenv venv
source venv/bin/activate

# 依存パッケージのインストール
pip install -r requirements.txt
pip install gunicorn

# 環境設定ファイルの作成
cp .env.example .env
# .envファイルを編集して適切な設定を行う

# 静的ファイルの収集
python manage.py collectstatic --noinput

# データベースのマイグレーション
python manage.py migrate
```

### 3. Gunicornの設定

```bash
# Gunicornのサービスファイルを作成
sudo tee /etc/systemd/system/gunicorn_flexible_web_checker.service > /dev/null << 'EOF'
[Unit]
Description=gunicorn daemon for flexible_web_checker
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/flexible_web_checker
ExecStart=/var/www/flexible_web_checker/venv/bin/gunicorn \
          --access-logfile - \
          --workers 3 \
          --bind unix:/var/www/flexible_web_checker/flexible_web_checker.sock \
          flexible_web_checker.wsgi:application

[Install]
WantedBy=multi-user.target
EOF

# アプリケーションディレクトリの所有者を変更
sudo chown -R www-data:www-data /var/www/flexible_web_checker

# サービスの有効化と起動
sudo systemctl enable gunicorn_flexible_web_checker
sudo systemctl start gunicorn_flexible_web_checker
```

### 4. Apacheの設定

```bash
# Apacheモジュールの有効化
sudo a2enmod proxy
sudo a2enmod proxy_http

# Apacheの設定ファイルを作成
sudo tee /etc/apache2/sites-available/flexible_web_checker.conf > /dev/null << 'EOF'
<VirtualHost *:80>
    ServerName example.com
    ServerAlias www.example.com

    DocumentRoot /var/www/flexible_web_checker

    ErrorLog ${APACHE_LOG_DIR}/flexible_web_checker_error.log
    CustomLog ${APACHE_LOG_DIR}/flexible_web_checker_access.log combined

    Alias /static/ /var/www/flexible_web_checker/static/
    Alias /media/ /var/www/flexible_web_checker/media/

    <Directory /var/www/flexible_web_checker/static>
        Require all granted
    </Directory>

    <Directory /var/www/flexible_web_checker/media>
        Require all granted
    </Directory>

    <Directory /var/www/flexible_web_checker/flexible_web_checker>
        <Files wsgi.py>
            Require all granted
        </Files>
    </Directory>

    ProxyPass /static/ !
    ProxyPass /media/ !
    ProxyPass / unix:/var/www/flexible_web_checker/flexible_web_checker.sock|http://localhost/
    ProxyPassReverse / unix:/var/www/flexible_web_checker/flexible_web_checker.sock|http://localhost/
</VirtualHost>
EOF

# サイトの有効化
sudo a2ensite flexible_web_checker.conf

# デフォルトサイトの無効化（必要に応じて）
sudo a2dissite 000-default.conf

# Apacheの設定テスト
sudo apache2ctl configtest

# Apacheの再起動
sudo systemctl restart apache2
```

### 5. ファイアウォールの設定

```bash
# ファイアウォールでHTTPを許可
sudo ufw allow 'Apache Full'
```

## 運用とメンテナンス

### アプリケーションの更新

```bash
# アプリケーションディレクトリに移動
cd /var/www/flexible_web_checker

# 最新のコードを取得
git pull

# 仮想環境をアクティベート
source venv/bin/activate

# 依存パッケージの更新
pip install -r requirements.txt

# データベースのマイグレーション
python manage.py migrate

# 静的ファイルの再収集
python manage.py collectstatic --noinput

# 所有者の変更
sudo chown -R www-data:www-data /var/www/flexible_web_checker

# Gunicornの再起動
sudo systemctl restart gunicorn_flexible_web_checker
```

### ログの確認

```bash
# Gunicornのログを確認
sudo journalctl -u gunicorn_flexible_web_checker

# Apacheのエラーログを確認
sudo tail -f /var/log/apache2/flexible_web_checker_error.log

# Apacheのアクセスログを確認
sudo tail -f /var/log/apache2/flexible_web_checker_access.log
```

## トラブルシューティング

### Gunicornが起動しない場合

```bash
# ステータスの確認
sudo systemctl status gunicorn_flexible_web_checker

# 手動でGunicornを起動してエラーを確認
cd /var/www/flexible_web_checker
source venv/bin/activate
gunicorn --bind unix:/var/www/flexible_web_checker/flexible_web_checker.sock flexible_web_checker.wsgi:application
```

### Apacheが起動しない場合

```bash
# 設定ファイルの構文チェック
sudo apache2ctl configtest

# ステータスの確認
sudo systemctl status apache2
```

### 静的ファイルが表示されない場合

```bash
# 権限の確認と修正
sudo chown -R www-data:www-data /var/www/flexible_web_checker/static/
sudo chown -R www-data:www-data /var/www/flexible_web_checker/media/
```

### ソケットファイルの問題

```bash
# ソケットファイルの権限確認
ls -la /var/www/flexible_web_checker/flexible_web_checker.sock

# ソケットディレクトリの権限確認
ls -la /var/www/flexible_web_checker/

# 権限の修正
sudo chown www-data:www-data /var/www/flexible_web_checker/flexible_web_checker.sock
```
