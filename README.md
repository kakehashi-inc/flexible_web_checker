# Flexible Web Checker

Flexible Web Checkerは、Webサイトの更新を監視し、変更があった場合に通知するDjangoベースのWebアプリケーションです。

## 概要

このアプリケーションは、指定したURLのWebページを定期的にチェックし、コンテンツに変更があった場合に検知します。ユーザーは複数のURLを登録し、それらをコレクションとしてグループ化することができます。

主な機能：
- URLの登録と管理（単一追加、一括追加）
- 複数のチェック方法（標準HTML、HTMLセレクタ、カスタム条件）
- コレクションによるURL管理
- 更新検知と履歴管理
- サムネイル自動生成
- 多言語対応（日本語・英語）

## セットアップ方法

### 開発環境

1. リポジトリのクローン
```bash
git clone https://github.com/kakehashi-inc/flexible_web_checker.git
cd flexible_web_checker
```

2. 仮想環境の作成と有効化
```bash
python -m venv venv
source venv/bin/activate  # Windowsの場合: venv\Scripts\activate
```

3. 依存パッケージのインストール
```bash
pip install -r requirements.txt
```

4. 環境変数の設定 (必要な場合)
`.env.example` をコピーして `.env` ファイルを作成し、必要に応じて設定を編集します。特にデータベース接続情報や `SECRET_KEY` を設定してください。
```bash
cp .env.example .env
# nano .env  # or your preferred editor
```

5. データベースのマイグレーション
```bash
python manage.py migrate
```

6. 開発サーバーの起動
```bash
python manage.py runserver
```

7. Celeryワーカーの起動（別ターミナルで）
```bash
celery -A flexible_web_checker worker --loglevel=info
```

8. Celery Beatの起動（別ターミナルで、定期タスク用）
```bash
celery -A flexible_web_checker beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

### 本番環境

本番環境へのデプロイ手順については、以下のドキュメントを参照してください：

- [RHEL系OS向けApacheデプロイ手順](Documents/setup_apache_rhel.md)
- [Ubuntu/Debian系OS向けApacheデプロイ手順](Documents/setup_apache_ubuntu.md)

## 主要コマンド

- 開発サーバー起動: `python manage.py runserver`
- テスト実行: `python manage.py test`
- マイグレーション作成: `python manage.py makemigrations`
- マイグレーション適用: `python manage.py migrate`
- 静的ファイル収集: `python manage.py collectstatic`
- スーパーユーザー作成: `python manage.py createsuperuser`
- Celeryワーカー起動: `celery -A flexible_web_checker worker --loglevel=info`
- Celery Beat起動: `celery -A flexible_web_checker beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler`
- コード解析: `pylint flexible_web_checker`
- コードフォーマット: `black .`

## 技術スタック

- **バックエンド**: Django 4.2, Python 3.9+
- **フロントエンド**: HTML, CSS (Tailwind CSS), JavaScript
- **データベース**: SQLite (開発), PostgreSQL (本番推奨)
- **非同期タスク**: Celery, Redis
- **その他**: mod_wsgi (Apache連携), Requests, BeautifulSoup4, Selenium, Pillow

## ドキュメント

詳細なドキュメントは `Documents` ディレクトリにあります：

- [仕様書案.md](./Documents/仕様書案.md)
- [テーブル定義](Documents/テーブル定義.md)
- [RHEL系OS向けApacheデプロイ手順](Documents/setup_apache_rhel.md)
- [Ubuntu/Debian系OS向けApacheデプロイ手順](Documents/setup_apache_ubuntu.md)

## ライセンス

Copyright © 2025 Kakehashi Inc. All rights reserved.
