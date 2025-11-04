from django.urls import path, include

from bookmark.views.i18n import set_language_view

app_name = "bookmark"

urlpatterns = [
    path("i18n/setlang/", set_language_view, name="set_language"),
]
