from django.shortcuts import render, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext_lazy as _
from django.contrib import messages
from django.http import JsonResponse

from bookmark.tasks.url_check import check_all_urls_task


def home(request):
    """ホームページビュー"""
    if request.user.is_authenticated:
        return redirect("bookmark:url_list")

    return render(request, "bookmark/core/home.html")


@login_required
def about(request):
    """アバウトページビュー"""
    return render(request, "bookmark/core/about.html")


@staff_member_required
def check_all_urls(request):
    """すべてのURL更新チェックビュー"""
    check_all_urls_task.delay(request.user.pk)

    messages.success(request, _("すべてのURLの更新チェックを開始しました。"))

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({"status": "success"})
    return redirect("bookmark:url_list")
