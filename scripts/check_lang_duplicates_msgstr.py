import polib
from collections import defaultdict
from pathlib import Path

def find_duplicate_msgstr(po_file_path):
    """
    指定された .po ファイル内で重複する msgstr を検索し、
    該当する msgid を表示する。
    ファイルごとに結果をまとめて表示する。
    """
    try:
        po = polib.pofile(po_file_path, encoding='utf-8')
    except OSError as e:
        print(f"Error opening file {po_file_path}: {e}")
        return
    except Exception as e:
        print(f"Error parsing file {po_file_path}: {e}")
        return

    msgstr_map = defaultdict(list)
    for entry in po:
        # msgstr が空でなく、obsolete でないエントリを対象とする
        if entry.msgstr and not entry.obsolete:
            # 大文字小文字を区別せずに比較するため小文字に変換
            msgstr_lower = entry.msgstr.lower()
            msgstr_map[msgstr_lower].append(entry.msgid)

    duplicates_output = [] # Store formatted duplicate strings
    for msgstr_lower, msgids in msgstr_map.items():
        if len(msgids) > 1:
            # Find the original msgstr using the first msgid
            original_msgstr = ""
            try:
                # polib < 1.2.0 does not have find method
                if hasattr(po, 'find'):
                    entry = po.find(msgids[0])
                    if entry:
                         original_msgstr = entry.msgstr
                else: # Fallback for older polib versions
                    for entry in po:
                         if entry.msgid == msgids[0]:
                              original_msgstr = entry.msgstr
                              break
            except Exception as e:
                 # Keep the error message, but don't store it in output list
                 print(f"Error finding original msgstr for {msgids[0]} in {po_file_path}: {e}")

            # Prepare the output string for this duplicate msgstr
            output_str = f'  msgstr: "{original_msgstr if original_msgstr else msgstr_lower}" (該当する msgid {len(msgids)} 件):\n'
            for msgid in msgids:
                output_str += f'    - msgid: "{msgid}"\n'
            duplicates_output.append(output_str)

    # Print the results for the file only if duplicates were found
    if duplicates_output:
        print(f"\n重複する msgstr が見つかりました in {po_file_path}:")
        print("".join(duplicates_output).rstrip()) # Join and print all duplicates
    # Optionally, print a message if the file was processed but no duplicates were found
    elif msgstr_map: # Check if the map has entries (file wasn't empty/only had empty msgstr)
         print(f"\n{po_file_path} 内に重複する msgstr はありませんでした。")

def check_directory_for_po_files(locale_dir_path: Path):
    """
    指定された locale ディレクトリ内の .po ファイルを検索し、重複チェックを行う。
    django標準の locale/<lang>/LC_MESSAGES/django.po 構造を想定。
    """
    print(f"\n--- Checking directory: {locale_dir_path} ---")
    found_po_files = False
    if not locale_dir_path.is_dir():
        print(f"指定されたパスはディレクトリではありません: {locale_dir_path}")
        return

    lang_dirs = [d for d in locale_dir_path.iterdir() if d.is_dir()]

    if not lang_dirs:
        print(f"言語ディレクトリが見つかりません: {locale_dir_path}")
        return

    for lang_dir in lang_dirs:
        lc_messages_dir = lang_dir / "LC_MESSAGES"
        if lc_messages_dir.is_dir():
            po_file = lc_messages_dir / "django.po"
            if po_file.is_file():
                print(f"Checking file: {po_file}")
                find_duplicate_msgstr(str(po_file))
                found_po_files = True

if __name__ == "__main__":
    # Explicitly target bookmark/locale directory
    target_locale_dir = Path("bookmark/locale")

    if not target_locale_dir.is_dir():
        print(f"対象ディレクトリが見つからないか、ディレクトリではありません: {target_locale_dir}")
    else:
        print(f"対象ディレクトリを処理します: {target_locale_dir}")
        check_directory_for_po_files(target_locale_dir)

    print("\nチェックが完了しました")
