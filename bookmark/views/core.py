from django.shortcuts import render, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext_lazy as _
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.conf import settings

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
    periodic_tasks = PeriodicTask.objects.all().order_by('-last_run_at')

    # タスク実行履歴の取得（最新100件）
    task_results = TaskResult.objects.all().order_by('-date_done')[:100]

    # ページネーション
    paginator = Paginator(task_results, 20)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    context = {
        'periodic_tasks': periodic_tasks,
        'task_results': page_obj,
        'page_obj': page_obj,
    }

    return render(request, "bookmark/core/job_management.html", context)
