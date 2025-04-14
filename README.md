# Flexible Web Checker

## 概要 (Overview)

Flexible Web Checkerは、指定したWebページの更新を柔軟な方法で監視・通知するDjangoアプリケーションです。RSSフィード、HTMLコンテンツの変更（標準またはカスタムセレクタ指定）を検知し、更新があった場合にユーザーに通知します（通知機能は将来実装予定）。

主な機能:
*   ユーザー認証
*   監視対象URLの登録・管理（単一・一括追加）
*   URLごとのチェックタイプ設定（RSS, HTML標準, HTMLカスタム）
*   更新履歴の表示
*   Webページのサムネイル自動生成
*   非同期タスク処理 (Celery)

## 技術スタック (Tech Stack)

*   **Backend:** Python 3.12+, Django 4.2+
*   **Database:** PostgreSQL (推奨), SQLite (開発用)
*   **Async Tasks:** Celery, Redis (or RabbitMQ)
*   **Frontend:** HTML, Tailwind CSS, JavaScript
*   **Web Server (Deployment):** Apache + mod_wsgi (推奨構成例あり), Nginx + Gunicorn など
*   **Other:** Requests, BeautifulSoup4, Selenium, Pillow

## セットアップ方法 (Setup)

### 1. リポジトリのクローン

```bash
git clone https://github.com/kakehashi-inc/flexible_web_checker.git
cd flexible_web_checker
```

### 2. Python仮想環境の作成と有効化

```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate  # Windows
```

### 3. 依存パッケージのインストール

```bash
pip install -r requirements.txt
```

### 4. 環境変数の設定

`.env.example` をコピーして `.env` ファイルを作成し、必要に応じて設定を編集します。特にデータベース接続情報や `SECRET_KEY` を設定してください。

```bash
cp .env.example .env
# nano .env  # or your preferred editor
```

### 5. データベースマイグレーションの実行

```bash
python manage.py migrate
```

### 6. 静的ファイルの収集 (本番環境向け)

```bash
python manage.py collectstatic
```

### 7. スーパーユーザーの作成 (任意)

```bash
python manage.py createsuperuser
```

### 8. 開発サーバーの起動

```bash
python manage.py runserver
```

### 9. CeleryワーカーとBeatの起動 (非同期タスク用)

別のターミナルでそれぞれ起動します。

```bash
celery -A flexible_web_checker worker -l info
```

```bash
celery -A flexible_web_checker beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

## 主要コマンド (Key Commands)

*   `python manage.py runserver`: 開発用Webサーバーを起動します。
*   `python manage.py test`: ユニットテストを実行します。
*   `python manage.py makemigrations [app_name]`: データベースモデルの変更に基づいてマイグレーションファイルを作成します。
*   `python manage.py migrate`: マイグレーションをデータベースに適用します。
*   `python manage.py collectstatic`: 静的ファイルを `STATIC_ROOT` に収集します。
*   `python manage.py createsuperuser`: 管理者アカウントを作成します。
*   `celery -A flexible_web_checker worker -l info`: Celeryワーカープロセスを起動します。
*   `celery -A flexible_web_checker beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler`: Celery Beat (定期タスクスケジューラ) を起動します。
*   `pylint flexible_web_checker`: Pylintによるコード解析を実行します。
*   `black .`: Blackによるコードフォーマットを実行します。

## ドキュメント (Documentation)

詳細なドキュメントは `Documents/` ディレクトリを参照してください。

*   [仕様書案.md](./Documents/仕様書案.md)
*   [テーブル定義.md](./Documents/テーブル定義.md) (作成中)
*   [setup_apache_rhel.md](./Documents/setup_apache_rhel.md) (作成中)
*   [setup_apache_ubuntu.md](./Documents/setup_apache_ubuntu.md) (作成中)
