# RHEL系OS (Amazon Linux 2023含む) 向け Apache + Gunicorn デプロイ手順

## 前提条件

- RHEL 8/9、CentOS 8/9、Amazon Linux 2023 などのRHEL系OS
- Python 3.8以上
- Apache 2.4以上
- Gunicorn

## インストール手順

### 1. 必要なパッケージのインストール

```bash
# 必要なパッケージのインストール
sudo dnf update -y
sudo dnf install -y python3 python3-pip python3-devel httpd httpd-devel gcc git

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

# サービスの有効化と起動
sudo systemctl enable gunicorn_flexible_web_checker
sudo systemctl start gunicorn_flexible_web_checker
```

### 4. Apacheの設定

```bash
# Apacheの設定ファイルを作成
sudo tee /etc/httpd/conf.d/flexible_web_checker.conf > /dev/null << 'EOF'
<VirtualHost *:80>
    ServerName example.com
    ServerAlias www.example.com

    DocumentRoot /var/www/flexible_web_checker

    ErrorLog /var/log/httpd/flexible_web_checker_error.log
    CustomLog /var/log/httpd/flexible_web_checker_access.log combined

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

# 必要なApacheモジュールの有効化
sudo dnf install -y httpd-devel mod_proxy mod_proxy_http

# Apacheの再起動
sudo systemctl restart httpd
sudo systemctl enable httpd
```

### 5. ファイアウォールの設定

```bash
# ファイアウォールでHTTPを許可
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --reload
```

### 6. SELinuxの設定（SELinuxが有効な場合）

```bash
# SELinuxの設定
sudo setsebool -P httpd_can_network_connect 1
sudo chcon -Rt httpd_sys_content_t /var/www/flexible_web_checker/static/
sudo chcon -Rt httpd_sys_content_t /var/www/flexible_web_checker/media/
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

# Gunicornの再起動
sudo systemctl restart gunicorn_flexible_web_checker
```

### ログの確認

```bash
# Gunicornのログを確認
sudo journalctl -u gunicorn_flexible_web_checker

# Apacheのエラーログを確認
sudo tail -f /var/log/httpd/flexible_web_checker_error.log

# Apacheのアクセスログを確認
sudo tail -f /var/log/httpd/flexible_web_checker_access.log
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
sudo apachectl configtest

# ステータスの確認
sudo systemctl status httpd
```

### 静的ファイルが表示されない場合

```bash
# 権限の確認と修正
sudo chown -R apache:apache /var/www/flexible_web_checker/static/
sudo chown -R apache:apache /var/www/flexible_web_checker/media/

# SELinuxコンテキストの設定
sudo chcon -Rt httpd_sys_content_t /var/www/flexible_web_checker/static/
sudo chcon -Rt httpd_sys_content_t /var/www/flexible_web_checker/media/
```
