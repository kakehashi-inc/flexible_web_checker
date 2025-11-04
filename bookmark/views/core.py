from django.shortcuts import render, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext_lazy as _
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import timedelta


def home(request):
    """ホームページ/ダッシュボードビュー"""
    if request.user.is_authenticated:
        # ログイン済みユーザーにはダッシュボードを表示
        from bookmark.models import UrlItem, Collection, UrlItemCollection

        # URL統計
        total_urls = UrlItem.objects.filter(user=request.user).count()
        active_urls = UrlItem.objects.filter(user=request.user, is_active=True).count()
        inactive_urls = total_urls - active_urls

        # コレクション統計
        total_collections = Collection.objects.filter(user=request.user).count()
        urls_in_collections = UrlItemCollection.objects.filter(collection__user=request.user).values("url_item").distinct().count()
        uncategorized_urls = total_urls - urls_in_collections

        # 更新情報
        today = timezone.now().date()
        week_ago = timezone.now() - timedelta(days=7)

        updated_today = UrlItem.objects.filter(user=request.user, last_updated_at__date=today).count()

        updated_this_week = UrlItem.objects.filter(user=request.user, last_updated_at__gte=week_ago).count()

        # 未読通知数（Notificationモデルがある場合）
        try:
            from bookmark.models import Notification

            unread_notifications = Notification.objects.filter(user=request.user, is_read=False).count()
        except:
            unread_notifications = 0

        # 最近更新されたURL（上位5件）
        recent_updated_urls = UrlItem.objects.filter(user=request.user).order_by("-last_updated_at")[:5]

        context = {
            "total_urls": total_urls,
            "active_urls": active_urls,
            "inactive_urls": inactive_urls,
            "total_collections": total_collections,
            "urls_in_collections": urls_in_collections,
            "uncategorized_urls": uncategorized_urls,
            "updated_today": updated_today,
            "updated_this_week": updated_this_week,
            "unread_notifications": unread_notifications,
            "recent_updated_urls": recent_updated_urls,
        }

        return render(request, "core/dashboard.html", context)

    # 未ログインユーザーにはホームページを表示
    return render(request, "core/home.html")


def about(request):
    """アバウトページビュー"""
    return render(request, "core/about.html")


@staff_member_required
def check_all_urls(request):
    """すべてのURL更新チェックビュー"""
    if request.method == "POST":
        # 全ユーザーの全アクティブURL項目をチェック
        from bookmark.models import UrlItem
        from bookmark.tasks.url_check import check_url_update

        url_items = UrlItem.objects.filter(is_active=True)
        count = 0

        for url_item in url_items:
            try:
                check_url_update.delay(url_item.id)
                count += 1
            except Exception as e:
                messages.error(request, _("error_occurred") + f": {str(e)}")

        messages.success(request, _("url_check_started_for_count").format(count=count))

        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"status": "success", "count": count})
        return redirect("bookmark:mypage")
    else:
        # GETリクエストの場合はマイページにリダイレクト
        return redirect("bookmark:mypage")


@staff_member_required
def job_management(request):
    """ジョブ管理ビュー"""
    from django_celery_beat.models import PeriodicTask
    from django_celery_results.models import TaskResult

    # 定期実行タスクの取得
    periodic_tasks = PeriodicTask.objects.all().order_by("-last_run_at")

    # タスク実行履歴の取得（最新100件）
    task_results = TaskResult.objects.all().order_by("-date_done")[:100]

    # ページネーション
    paginator = Paginator(task_results, 20)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    context = {
        "periodic_tasks": periodic_tasks,
        "task_results": page_obj,
        "page_obj": page_obj,
    }

    return render(request, "core/job_management.html", context)
