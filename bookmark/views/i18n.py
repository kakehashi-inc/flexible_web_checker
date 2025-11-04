"""
国際化関連のビュー
"""

from django.http import HttpResponseRedirect
from django.utils import translation
from django.utils.translation import check_for_language
from django.conf import settings


def set_language_view(request):
    """
    カスタム言語切り替えビュー
    Djangoの標準ビューを参考に実装
    """
    next_url = request.POST.get("next", request.META.get("HTTP_REFERER", "/"))

    if request.method == "POST":
        lang_code = request.POST.get("language", None)

        if lang_code and check_for_language(lang_code):
            translation.activate(lang_code)

            if hasattr(request, "session"):
                request.session[settings.LANGUAGE_COOKIE_NAME] = lang_code

            response = HttpResponseRedirect(next_url)

            response.set_cookie(
                settings.LANGUAGE_COOKIE_NAME,
                lang_code,
                max_age=settings.LANGUAGE_COOKIE_AGE,
                path=settings.LANGUAGE_COOKIE_PATH,
                domain=settings.LANGUAGE_COOKIE_DOMAIN,
                secure=settings.LANGUAGE_COOKIE_SECURE,
                httponly=False,
                samesite=settings.LANGUAGE_COOKIE_SAMESITE,
            )

            response.set_cookie(
                "language",
                lang_code,
                max_age=settings.LANGUAGE_COOKIE_AGE,
                path=settings.LANGUAGE_COOKIE_PATH,
            )

            return response

    return HttpResponseRedirect(next_url)
