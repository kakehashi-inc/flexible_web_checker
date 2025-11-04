from django.utils import translation

def language_context(request):
    """
    言語設定をテンプレートコンテキストに追加するコンテキストプロセッサ
    """
    return {
        'LANGUAGE_CODE': translation.get_language(),
    }
