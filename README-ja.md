# Flexible Web Checker

## 1. システム概要

Flexible Web Checkerは、指定したWebページの更新を定期的にチェックし、変更があった場合に通知するDjangoアプリケーションです。ユーザーはURLを登録し、コレクションにまとめることができます。更新チェックはバックグラウンドで非同期に実行されます。

## 2. 開発環境構築

### 2.1 前提条件

- Python 3.12以上 (Django 5.2)
- gettext（国際化のため）
- Node.js, Yarn

### 2.2 手順

1. リポジトリのクローン

    ```bash
    git clone <リポジトリURL>
    cd <リポジトリ名>
    ```

2. 仮想環境の作成と有効化

    ```bash
    # 仮想環境の作成
    python3 -m venv venv

    # 仮想環境の有効化
    source venv/bin/activate  # (macOS/Linux)
    .\venv\Scripts\activate  # (Windows)
    ```

3. 依存関係のインストール

    ```bash
    # Python依存関係のインストール
    pip install -r requirements.txt

    # gettextがインストールされていない場合（Ubuntu/Debian）
    # sudo apt-get install gettext
    ```

4. 環境変数の設定

    `.env.example`ファイルを`.env`にコピーして必要に応じて編集する

    ```bash
    cp .env.example .env
    # 必要に応じて.envファイルを編集
    ```

5. フロントエンド依存関係のインストールとセットアップ

    **注記:** このプロジェクトではパッケージマネージャーとして **Yarn の利用を推奨**していますが、npm でも動作します。
    以下のコマンド例は Yarn を使用しています。npm を使用する場合は、適宜コマンドを読み替えてください
    (`yarn install` は `npm install`、`yarn <script>` は `npm run <script>`)。

    ```bash
    # Node.jsとYarnがインストールされていることを確認
    # 依存関係をインストール
    yarn install

    # TypeScriptをビルド
    yarn build:ts

    # JavaScriptをビルド
    yarn build:js

    # CSS (Tailwind) をビルド
    yarn build:css:prod

    # SCSS をビルド
    yarn build:scss

    # JavaScript ライブラリをコピー
    yarn setup:libs

    # FontAwesome フォントをコピー
    yarn setup:fa

    # アイコンを生成 (もし必要なら)
    # yarn icons

    # モジュールの選択更新
    # yarn upgrade-interactive

    # モジュールの更新
    # yarn up "sweetalert2"
    ```

6. 言語ファイルのコンパイル

    ```bash
    # .poファイルから.moファイルを生成
    python manage.py compilemessages
    ```

7. データベースのマイグレーション

    ```bash
    python manage.py migrate
    ```

8. 静的ファイルの準備（本番環境など）

    ```bash
    python manage.py collectstatic
    ```

9. スーパーユーザーの作成 (管理者アカウント)

    ```bash
    python manage.py createsuperuser
    ```

10. 定期タスクのセットアップ（URL更新チェックのスケジュール設定）

    ```bash
    python manage.py setup_periodic_tasks
    ```

    このコマンドは、`.env`ファイルの`UPDATE_CHECK_SCHEDULE`設定に基づいて、定期タスクの設定を初期化します。

11. 開発サーバーの起動

    ```bash
    python manage.py runserver
    ```

### 2.3 動作確認

ブラウザで `http://localhost:8000/` にアクセス。

### 2.4. CeleryワーカーとBeatの起動 (非同期タスク用)

別のターミナルでそれぞれ起動します。

```bash
# Celeryワーカー
celery -A flexible_web_checker worker -l info

# Celery Beat (スケジュールタスク用)
celery -A flexible_web_checker beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

## 3. 開発時の注意点

### モデルとマイグレーション

Djangoのモデル（`models.py` または `models/` ディレクトリ内のファイル）に変更を加えた場合は、**原則としてマイグレーションファイルの作成・適用が必要**です。
モデルファイルを編集した後は、**習慣として `makemigrations <アプリ名>` を実行し**、"No changes detected" と表示されるか、意図した変更がマイグレーションファイルとして生成されるかを確認することを推奨します。

1. makemigrations の実行
    モデルに変更を加えた後、以下のコマンドを実行して変更内容をマイグレーションファイルに記録します。

    ```bash
    python manage.py makemigrations bookmark
    ```

    このコマンドは、モデル定義と既存のマイグレーションファイルとの差分を検出し、新しいマイグレーションファイル（例: `000X_...py`）を生成します。

2. migrate の実行
    生成されたマイグレーションファイルを以下のコマンドでデータベースに適用します。

    ```bash
    python manage.py migrate
    ```

    これにより、データベースのスキーマがモデル定義と同期されます。

### 翻訳ファイルの更新 (compilemessages)

翻訳ファイル（`.po` ファイル）に手動で変更を加えた場合や、ソースコード内の翻訳対象文字列 (`{% trans "..." %}` や `trans("...")` および `_("...")` など) を追加・変更した後に `python manage.py makemessages -l <言語コード>` を実行した場合は、以下のコマンドで翻訳ファイルをコンパイルする必要があります。

```bash
python manage.py compilemessages
```

これにより、`.po` ファイルから `.mo` ファイルが生成（または更新）され、アプリケーションの表示言語に翻訳が正しく反映されるようになります。

### CSSの再構築 (Tailwind CSS)

HTMLテンプレートファイルや、Tailwind CSSのスキャン対象として設定されている他のファイル（JavaScriptファイルやPythonファイルなど）で、Tailwind CSSのユーティリティクラスを追加・変更・削除した場合は、CSSファイルを再構築して変更を反映させる必要があります。

多くのプロジェクトでは、開発中にファイルの変更を監視し、自動的にCSSを再構築するウォッチモードが用意されています。

```bash
yarn watch:css
# または npm run watch:css
```

ウォッチモードを使用している場合でも、定期的に本番用ビルドを実行して、最終的なCSSの出力に問題がないか確認することが推奨されます。

本番ビルド:

```bash
yarn build:css:prod
# または npm run build:css:prod
```
