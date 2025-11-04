import re
from pathlib import Path


def extract_trans_keys_from_templates():
    template_dir = Path("bookmark/templates")
    keys = set()

    for file_path in template_dir.glob("**/*.html"):
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

            # _('...')
            trans_pattern = r'_\([\'"]([^\'"]+)[\'"]\)'
            matches = re.findall(trans_pattern, content)
            keys.update(matches)

            for trans_keyword in ["trans", "translate", "var_translate"]:
                # trans "..."
                trans_pattern = rf"{trans_keyword}\s+[\"']([^\"']+)[\"']"
                matches = re.findall(trans_pattern, content)
                keys.update(matches)

                # trans('...')
                trans_pattern = rf"{trans_keyword}\([\"']([^\"']+)[\"']\)"
                matches = re.findall(trans_pattern, content)
                keys.update(matches)

            # {% blocktrans ... %}...{% endblocktrans %}
            trans_pattern = r"{%\s*blocktrans[^}]*%}(.+){%\s*endblocktrans\s*%}"
            matches = re.findall(trans_pattern, content)
            keys.update(matches)

    return keys


def extract_trans_keys_from_python():
    python_dir = Path("bookmark")
    keys = set()

    for file_path in python_dir.glob("**/*.py"):
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

            # _('...')
            python_pattern = r'_\([\'"]([^\'"]+)[\'"]\)'
            matches = re.findall(python_pattern, content)
            keys.update(matches)

            # trans('...')
            python_pattern = r'trans\([\'"]([^\'"]+)[\'"]\)'
            matches = re.findall(python_pattern, content)
            keys.update(matches)

            # gettext('...')
            python_pattern = r'gettext\([\'"]([^\'"]+)[\'"]\)'
            matches = re.findall(python_pattern, content)
            keys.update(matches)

            # gettext_lazy('...')
            python_pattern = r'gettext_lazy\([\'"]([^\'"]+)[\'"]\)'
            matches = re.findall(python_pattern, content)
            keys.update(matches)

    return keys


def get_keys_from_locale_dir(base_dir, lang_code):
    """指定されたベースディレクトリと言語コードからpoファイルのキーとパスを取得"""
    po_path = Path(base_dir) / lang_code / "LC_MESSAGES" / "django.po"

    keys = set()

    if not po_path.exists():
        # ファイルが存在しない場合は空のセットとパスを返す
        return keys

    with open(po_path, "r", encoding="utf-8") as f:
        content = f.read()

        # msgid "..." または msgid '...' を抽出
        msgid_pattern = r'msgid\s+["\']([^"\']+)["\']'
        matches = re.findall(msgid_pattern, content)

        # 空のキーを除外してセットに追加
        keys.update(m for m in matches if m)

    return keys


def find_missing_and_unused_keys():
    template_keys = extract_trans_keys_from_templates()
    python_keys = extract_trans_keys_from_python()
    used_keys = template_keys.union(python_keys)

    root_locale_dir = Path("locale")
    bookmark_locale_dir = Path("bookmark/locale")

    if not root_locale_dir.exists():
        print(f"ディレクトリが見つかりません: {root_locale_dir}")
        return

    if not bookmark_locale_dir.exists():
        print(f"ディレクトリが見つかりません: {bookmark_locale_dir}")
        return

    bookmark_lang_dirs = [d for d in bookmark_locale_dir.iterdir() if d.is_dir()]

    for lang_dir in bookmark_lang_dirs:
        lang_code = lang_dir.name

        # ヘルパー関数を使ってキーとパスを取得
        root_lang_keys = get_keys_from_locale_dir(root_locale_dir, lang_code)
        bookmark_lang_keys = get_keys_from_locale_dir(bookmark_locale_dir, lang_code)

        # 不足キー: コード内で使われているが、bookmark と ./locale のどちらにもないキー
        missing_keys = used_keys - bookmark_lang_keys.union(root_lang_keys)

        # 未使用キー: bookmark/locale に存在するが、コード内で使われていないキー
        unused_keys = bookmark_lang_keys - used_keys

        # 結果の表示
        print(f"=== {lang_code} の翻訳ファイルの分析 ===")

        if missing_keys:
            print("不足している翻訳キー")
            for key in sorted(missing_keys):
                print(key)
            print()

        if unused_keys:
            print("未使用の翻訳キー")
            for key in sorted(unused_keys):
                print(key)
            print()

        if not missing_keys and not unused_keys:
            print("翻訳キーは同期されています")

        print()

    print("翻訳キーの分析が完了しました。")


if __name__ == "__main__":
    find_missing_and_unused_keys()
