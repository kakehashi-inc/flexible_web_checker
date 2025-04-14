# Flexible Web Checker

## 概要

Flexible Web Checkerは、指定したWebページの更新を定期的にチェックし、変更があった場合に通知するDjangoアプリケーションです。ユーザーはURLを登録し、コレクションにまとめることができます。更新チェックはバックグラウンドで非同期に実行されます。

## 技術スタック

-   **バックエンド:** Python, Django, Celery
-   **フロントエンド:** HTML, Tailwind CSS, JavaScript
-   **データベース:** SQLite (デフォルト), MySQL (接続数増加時)
-   **非同期処理:** Celery
-   **その他:** requests, beautifulsoup4, Pillow, Selenium

## セットアップ方法

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

### 3. 依存関係のインストール

```bash
pip install -r requirements.txt
```

### 4. 環境変数の設定

`.env.example` ファイルをコピーして `.env` ファイルを作成し、必要な設定（データベース接続情報、メール設定など）を記述します。

```bash
cp .env.example .env
# .env ファイルを編集
```

### 5. データベースマイグレーション

```bash
python manage.py migrate
```

### 6. スーパーユーザーの作成 (任意)

```bash
python manage.py createsuperuser
```

### 7. 開発サーバーの起動

```bash
python manage.py runserver
```

### 8. CeleryワーカーとBeatの起動 (非同期タスク用)

別のターミナルでそれぞれ起動します。

```bash
# Celeryワーカー
celery -A flexible_web_checker worker -l info

# Celery Beat (スケジュールタスク用)
celery -A flexible_web_checker beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

## 主要コマンド

-   `python manage.py runserver`: 開発サーバーを起動します。
-   `python manage.py test`: ユニットテストを実行します。
-   `python manage.py makemigrations`: データベースモデルの変更に基づいてマイグレーションファイルを作成します。
-   `python manage.py migrate`: マイグレーションをデータベースに適用します。
-   `celery -A flexible_web_checker worker -l info`: Celeryワーカーを起動します。
-   `celery -A flexible_web_checker beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler`: Celery Beatを起動します。
-   `pylint flexible_web_checker`: Pylintを実行してコードを静的解析します。

## ドキュメント

詳細なドキュメントは `Documents/` ディレクトリを参照してください。

-   `Documents/テーブル定義.md`: データベースのテーブル定義。
-   `Documents/setup_apache_rhel.md`: RHEL系OS向けのApache + Gunicornデプロイ手順。
-   `Documents/setup_apache_ubuntu.md`: Ubuntu/Debian系OS向けのApache + Gunicornデプロイ手順。
-   `Documents/仕様書案.md`: アプリケーションの仕様に関する詳細。
