import re
from collections import Counter
from pathlib import Path

def check_duplicates(file_path):
    if not Path(file_path).exists():
        print(f'翻訳ファイルが見つかりません: {file_path}')
        return

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    msgids = re.findall(r'msgid \"(.+?)\"', content)
    duplicates = [item for item, count in Counter(msgids).items() if count > 1]

    if duplicates:
        print('重複キーが見つかりました。')
        for dup in duplicates:
            print(f'  - \"{dup}\"')
    else:
        print('重複キーはありません。')
    print()

def check_all_languages(locale_dir_path: Path):
    """
    指定された locale ディレクトリ内の全言語の重複キーをチェックする
    """
    print(f"--- Checking directory: {locale_dir_path} ---")
    lang_dirs = [d for d in locale_dir_path.iterdir() if d.is_dir()]

    if not lang_dirs:
        print(f"言語ディレクトリが見つかりません: {locale_dir_path}")
        return

    for lang_dir in lang_dirs:
        po_path = lang_dir / "LC_MESSAGES" / "django.po"
        print(po_path)
        check_duplicates(po_path)

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
