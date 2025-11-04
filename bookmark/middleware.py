from django.utils import translation
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings


class LanguageMiddleware(MiddlewareMixin):
    """
    言語設定をクッキーから取得するミドルウェア
    クッキーが設定されていない場合はブラウザの優先言語を使用し、
    日本語または英語以外の場合はデフォルトで英語を使用する
    """

    def process_request(self, request):
        if settings.LANGUAGE_COOKIE_NAME in request.COOKIES:
            language = request.COOKIES.get(settings.LANGUAGE_COOKIE_NAME)
            if language in [lang[0] for lang in settings.LANGUAGES]:
                translation.activate(language)
                request.LANGUAGE_CODE = translation.get_language()
                return

        if "language" in request.COOKIES:
            language = request.COOKIES.get("language")
            if language in [lang[0] for lang in settings.LANGUAGES]:
                translation.activate(language)
                request.LANGUAGE_CODE = translation.get_language()
                return

        if hasattr(request, "LANGUAGE_CODE") and request.LANGUAGE_CODE:
            return

        accept_language = request.META.get("HTTP_ACCEPT_LANGUAGE", "")
        if accept_language:
            browser_language = accept_language.split(",")[0].split(";")[0].split("-")[0]
            if browser_language in [lang[0] for lang in settings.LANGUAGES]:
                language = browser_language
            else:
                language = "ja"  # 日本語をデフォルトとする

            if language in [lang[0] for lang in settings.LANGUAGES]:
                translation.activate(language)
                request.LANGUAGE_CODE = translation.get_language()
