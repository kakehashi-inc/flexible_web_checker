import re
from pathlib import Path

def extract_msgids(file_path):
    """
    翻訳ファイルからmsgidを抽出する
    """
    if not Path(file_path).exists():
        return set()

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        msgids = re.findall(r'msgid \"(.+?)\"', content)
        return set(msgids)

def check_language_diff(ja_keys, other_lang_path, other_lang_code):
    """
    日本語と他の言語のmsgidの差分をチェックする
    """
    other_keys = extract_msgids(other_lang_path)
    if not other_keys:
        print(f'=== {other_lang_code} の翻訳ファイルが見つかりません ===\n')
        return

    # 日本語にあって他の言語にないキー
    missing_in_other = ja_keys - other_keys
    # 他の言語にあって日本語にないキー
    missing_in_ja = other_keys - ja_keys

    print(f'=== {other_lang_code} と ja の差分 ===')

    if missing_in_other:
        print(f'{other_lang_code} に存在しないキー:')
        for key in sorted(missing_in_other):
            print(f'  - "{key}"')
    else:
        print(f'{other_lang_code} に存在しないキーはありません')

    if missing_in_ja:
        print('ja に存在しないキー:')
        for key in sorted(missing_in_ja):
            print(f'  - "{key}"')
    else:
        print('ja に存在しないキーはありません')

    print()

def check_all_languages(locale_dir_path: Path):
    """
    指定された locale ディレクトリ内の全言語とjaの差分をチェックする
    """
    print(f"--- Checking directory: {locale_dir_path} ---")
    ja_path = locale_dir_path / "ja" / "LC_MESSAGES" / "django.po"

    if not ja_path.exists():
        print(f"日本語の翻訳ファイルが見つかりません: {ja_path}")
        return

    ja_keys = extract_msgids(ja_path)
    if not ja_keys:
        print(f"日本語の翻訳ファイルにmsgidが見つかりません: {ja_path}")
        return

    # jaディレクトリ以外の言語ディレクトリを取得
    lang_dirs = [d for d in locale_dir_path.iterdir() if d.is_dir() and d.name != "ja"]

    for lang_dir in lang_dirs:
        po_path = lang_dir / "LC_MESSAGES" / "django.po"
        check_language_diff(ja_keys, po_path, lang_dir.name)

if __name__ == "__main__":
    # localeディレクトリを列挙
    locale_dirs = [
        Path("locale")
    ]
    for dir_path in Path(".").iterdir():
        if dir_path.is_dir():
            locale_path = dir_path / "locale"
            if locale_path.exists() and locale_path.is_dir():
                locale_dirs.append(locale_path)

    for locale_dir in locale_dirs:
        check_all_languages(locale_dir)

    print("すべてのチェックが完了しました")
