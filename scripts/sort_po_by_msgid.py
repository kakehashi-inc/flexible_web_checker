"""
bookmark/locale ディレクトリ内の django.po ファイルを検索し、
各ファイルのエントリを msgid でソートして上書き保存するスクリプト。
"""
import polib
from pathlib import Path
import sys

def sort_po_file_by_msgid(po_file_path):
    """
    指定された .po ファイルを msgid でソートして上書き保存する。
    ヘッダーコメント、エントリコメント、フラグ情報も保持する。
    """
    print(f"Processing: {po_file_path}") # ファイル名表示
    try:
        # wrapwidth=0 を指定して読み込み時の自動折り返しを防ぐ
        po = polib.pofile(po_file_path, wrapwidth=0)

        # ヘッダーコメント、メタデータ、通常のエントリを分離
        header = po.header # ファイル先頭のコメントを取得
        metadata = po.metadata
        # 空のmsgidを持つヘッダーエントリと、Obsoleteエントリを除外
        entries = [entry for entry in po if entry.msgid and not entry.obsolete]
        original_entry_count = len(entries)

        # msgidでエントリをソート (大文字小文字を区別)
        sorted_entries = sorted(entries, key=lambda entry: entry.msgid)
        sorted_entry_count = len(sorted_entries)

        # 新しいPOFileオブジェクトを作成 (wrapwidth=0 を指定)
        new_po = polib.POFile(wrapwidth=0)
        new_po.header = header # ヘッダーコメントを設定
        new_po.metadata = metadata
        # ソート済みエントリを追加
        for entry in sorted_entries:
            new_po.append(entry)

        # ソートした内容でファイルを上書き保存
        new_po.save(po_file_path)

        # 完了メッセージは件数のみ表示（ファイル名は削除）
        print(f"  -> Sorted ({original_entry_count} -> {sorted_entry_count} entries)")

    except OSError as e:
        print(f"Error processing file {po_file_path}: {e}", file=sys.stderr)
    except Exception as e:
        print(f"An unexpected error occurred while processing {po_file_path}: {e}", file=sys.stderr)


def process_locale_directory(locale_dir_path: Path):
    """
    指定された locale ディレクトリ内の .po ファイルを検索し、ソート処理を行う。
    django標準の locale/<lang>/LC_MESSAGES/django.po 構造を想定。
    """
    print(f"--- Processing directory: {locale_dir_path} ---")
    if not locale_dir_path.is_dir():
        print(f"Error: Not a directory: {locale_dir_path}", file=sys.stderr)
        return

    lang_dirs = [d for d in locale_dir_path.iterdir() if d.is_dir()]

    if not lang_dirs:
        print(f"No language directories found in: {locale_dir_path}")
        return

    processed_files = 0
    for lang_dir in lang_dirs:
        lc_messages_dir = lang_dir / "LC_MESSAGES"
        if lc_messages_dir.is_dir():
            po_file = lc_messages_dir / "django.po"
            if po_file.is_file():
                sort_po_file_by_msgid(str(po_file))
                processed_files += 1

    if processed_files == 0:
         print(f"No 'django.po' files found to process in subdirectories of: {locale_dir_path}")


if __name__ == "__main__":
    # 対象ディレクトリを固定
    target_locale_dir = Path("bookmark/locale")

    if not target_locale_dir.is_dir():
        print(f"Error: Target directory not found or not a directory: {target_locale_dir}", file=sys.stderr)
        sys.exit(1) # エラーで終了

    process_locale_directory(target_locale_dir)

    print("Processing complete.")
