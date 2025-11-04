import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib import messages
from django.http import JsonResponse

from bookmark.models import UrlItem
from bookmark.forms.url_manager import UrlItemForm, BulkUrlAddForm
from bookmark.utils import get_page_title, take_screenshot
from bookmark.tasks.url_check import check_url_update
from bookmark.tasks.thumbnail import update_thumbnail

logger = logging.getLogger(__name__)


@login_required
def url_list(request):
    """URL一覧ビュー (タブ対応)"""
    tab = request.GET.get("tab", "all")
    sort = request.GET.get("sort", "updated_desc")

    base_queryset = UrlItem.objects.filter(user=request.user)

    if tab == "uncategorized":
        queryset = base_queryset.filter(collections__isnull=True)
    elif tab == "all":
        queryset = base_queryset
    else:
        queryset = base_queryset
        tab = "all"

    if sort == "updated_desc":
        queryset = queryset.order_by("-last_updated_at", "-created_at")
    elif sort == "updated_asc":
        queryset = queryset.order_by("last_updated_at", "created_at")
    elif sort == "created_desc":
        queryset = queryset.order_by("-created_at")
    elif sort == "created_asc":
        queryset = queryset.order_by("created_at")
    elif sort == "title":
        queryset = queryset.order_by("title")

    paginator = Paginator(queryset, settings.ITEMS_PER_PAGE)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    context = {
        "url_items": page_obj,
        "page_obj": page_obj,
        "active_tab": tab,
        "current_sort": sort,
    }
    return render(request, "bookmark/url_manager/url_list.html", context)


@login_required
def url_add(request):
    """URL追加ビュー"""
    if request.method == "POST":
        form = UrlItemForm(request.POST)
        if form.is_valid():
            url_item = form.save(commit=False)
            url_item.user = request.user

            if not url_item.title:
                url_item.title = get_page_title(url_item.url)

            url_item.save()

            try:
                check_url_update.delay(url_item.id)
                update_thumbnail.delay(url_item.id)
            except Exception as e:
                logger.error(f"Error scheduling tasks for URL {url_item.id}: {str(e)}")

            messages.success(request, _("URLを追加しました。"))
            return redirect("bookmark:url_list")
    else:
        form = UrlItemForm()

    return render(request, "bookmark/url_manager/url_add.html", {"form": form})


@login_required
def url_detail(request, url_id):
    """URL詳細ビュー"""
    url_item = get_object_or_404(UrlItem, id=url_id, user=request.user)
    return render(request, "bookmark/url_manager/url_detail.html", {"url_item": url_item})


@login_required
def url_edit(request, url_id):
    """URL編集ビュー"""
    url_item = get_object_or_404(UrlItem, id=url_id, user=request.user)

    if request.method == "POST":
        form = UrlItemForm(request.POST, instance=url_item)
        if form.is_valid():
            form.save()
            messages.success(request, _("URLを更新しました。"))
            return redirect("bookmark:url_detail", url_id=url_item.id)
    else:
        form = UrlItemForm(instance=url_item)

    return render(
        request, "bookmark/url_manager/url_edit.html", {"form": form, "url_item": url_item}
    )


@login_required
def url_delete(request, url_id):
    """URL削除ビュー"""
    url_item = get_object_or_404(UrlItem, id=url_id, user=request.user)

    if request.method == "POST":
        url_item.delete()
        messages.success(request, _("URLを削除しました。"))
        return redirect("bookmark:url_list")

    return render(request, "bookmark/url_manager/url_delete.html", {"url_item": url_item})


@login_required
@staff_member_required
def url_check(request, url_id):
    """URL更新チェックビュー"""
    url_item = get_object_or_404(UrlItem, id=url_id, user=request.user)

    try:
        check_url_update.delay(url_item.id)
    except Exception as e:
        logger.error(f"Error scheduling update check for URL {url_item.id}: {str(e)}")

    messages.success(request, _("更新チェックを開始しました。"))

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({"status": "success"})
    else:
        return redirect("bookmark:url_detail", url_id=url_item.id)


@login_required
def url_update_thumbnail(request, url_id):
    """URLサムネイル更新ビュー"""
    url_item = get_object_or_404(UrlItem, id=url_id, user=request.user)

    try:
        update_thumbnail.delay(url_item.id)
    except Exception as e:
        logger.error(f"Error scheduling thumbnail update for URL {url_item.id}: {str(e)}")

    messages.success(request, _("サムネイルの更新を開始しました。"))

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({"status": "success"})
    else:
        return redirect("bookmark:url_detail", url_id=url_item.id)


@login_required
def url_bulk_add(request):
    """複数URL一括追加ビュー"""
    if request.method == 'POST':
        form = BulkUrlAddForm(request.POST)
        if form.is_valid():
            urls_to_add = form.cleaned_data['urls']
            added_count = 0
            error_urls = []

            for url_str in urls_to_add:
                if not url_str.startswith(('http://', 'https://')):
                    error_urls.append(f"{url_str} ({_('無効な形式')})")
                    continue

                if UrlItem.objects.filter(user=request.user, url=url_str).exists():
                    error_urls.append(f"{url_str} ({_('登録済み')})")
                    continue

                try:
                    title = get_page_title(url_str)
                    if not title:
                        title = url_str
                        messages.warning(request, _('URL "{url}" のタイトルを取得できませんでした。URLをタイトルとして使用します。').format(url=url_str))

                    url_item = UrlItem.objects.create(
                        user=request.user,
                        url=url_str,
                        title=title,
                        check_type='HTML_STANDARD'
                    )
                    try:
                        check_url_update.delay(url_item.id)
                        update_thumbnail.delay(url_item.id)
                    except Exception as e:
                        logger.error(f"Error scheduling tasks for URL {url_item.id}: {str(e)}")
                    added_count += 1
                except Exception as e:
                    print(f"Error adding URL {url_str}: {e}")
                    error_urls.append(f"{url_str} ({_('追加エラー')})")

            if added_count > 0:
                messages.success(request, _('{count}件のURLを追加しました。').format(count=added_count))
            if error_urls:
                error_html = _('以下のURLは追加できませんでした:') + '<ul class="list-disc list-inside">' + "".join([f"<li>{err}</li>" for err in error_urls]) + "</ul>"
                messages.error(request, error_html, extra_tags='safe')

            return redirect('bookmark:url_list')
    else:
        form = BulkUrlAddForm()

    return render(request, 'bookmark/url_manager/url_bulk_add.html', {'form': form})
