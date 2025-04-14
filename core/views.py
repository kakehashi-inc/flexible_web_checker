from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Count, Q
from url_manager.models import UrlItem
from collection_manager.models import Collection
from .tasks import check_all_urls_task


def home(request):
    """ホームページビュー"""
    if request.user.is_authenticated:
        return redirect("core:dashboard")

    return render(request, "core/home.html")


@login_required
def dashboard(request):
    """ダッシュボードビュー"""
    recent_updates = UrlItem.objects.filter(
        user=request.user, last_updated_at__isnull=False
    ).order_by("-last_updated_at")[:10]

    error_urls = UrlItem.objects.filter(user=request.user, error_count__gt=0).order_by(
        "-error_count"
    )[:5]

    collections = (
        Collection.objects.filter(user=request.user)
        .annotate(url_count=Count("url_items"))
        .order_by("-url_count")[:5]
    )

    total_urls = UrlItem.objects.filter(user=request.user).count()
    total_collections = Collection.objects.filter(user=request.user).count()
    total_updated_today = UrlItem.objects.filter(
        user=request.user, last_updated_at__date=timezone.now().date()
    ).count()

    context = {
        "recent_updates": recent_updates,
        "error_urls": error_urls,
        "collections": collections,
        "total_urls": total_urls,
        "total_collections": total_collections,
        "total_updated_today": total_updated_today,
    }

    return render(request, "core/dashboard.html", context)


@login_required
def about(request):
    """アバウトページビュー"""
    return render(request, "core/about.html")


@login_required
def check_all_urls(request):
    """すべてのURL更新チェックビュー"""
    check_all_urls_task.delay(request.user.pk)

    messages.success(request, _("すべてのURLの更新チェックを開始しました。"))

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({"status": "success"})
    else:
        return redirect("core:dashboard")
