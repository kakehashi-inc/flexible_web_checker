from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required

from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib import messages
from django.http import JsonResponse
from .models import UrlItem
from .forms import UrlItemForm, BulkUrlAddForm
from core.utils import get_page_title, take_screenshot
from core.tasks import check_url_update, update_thumbnail

@login_required
def url_list(request):
    """URL一覧ビュー (タブ対応)"""
    active_tab = request.GET.get('tab', 'all') # Default to 'all' tab

    url_items_query = UrlItem.objects.filter(user=request.user) # pylint: disable=no-member

    if active_tab == 'uncategorized':
        url_items_query = url_items_query.filter(collections__isnull=True)

    url_items = url_items_query.order_by('-last_updated_at', '-created_at')

    context = {
        'url_items': url_items,
        'active_tab': active_tab,
    }
    return render(request, 'url_manager/url_list.html', context)

@login_required
def url_add(request):
    """URL追加ビュー"""
    if request.method == 'POST':
        form = UrlItemForm(request.POST)
        if form.is_valid():
            url_item = form.save(commit=False)
            url_item.user = request.user
            
            if not url_item.title:
                url_item.title = get_page_title(url_item.url)
                
            url_item.save()
            
            check_url_update.delay(url_item.id)
            update_thumbnail.delay(url_item.id)
            
            messages.success(request, _('URLを追加しました。'))
            return redirect('url_manager:url_list')
    else:
        form = UrlItemForm()
    
    return render(request, 'url_manager/url_add.html', {'form': form})

@login_required
def url_detail(request, url_id):
    """URL詳細ビュー"""
    url_item = get_object_or_404(UrlItem, id=url_id, user=request.user)
    return render(request, 'url_manager/url_detail.html', {'url_item': url_item})

@login_required
def url_edit(request, url_id):
    """URL編集ビュー"""
    url_item = get_object_or_404(UrlItem, id=url_id, user=request.user)
    
    if request.method == 'POST':
        form = UrlItemForm(request.POST, instance=url_item)
        if form.is_valid():
            form.save()
            messages.success(request, _('URLを更新しました。'))
            return redirect('url_manager:url_detail', url_id=url_item.id)
    else:
        form = UrlItemForm(instance=url_item)
    
    return render(request, 'url_manager/url_edit.html', {'form': form, 'url_item': url_item})

@login_required
def url_delete(request, url_id):
    """URL削除ビュー"""
    url_item = get_object_or_404(UrlItem, id=url_id, user=request.user)
    
    if request.method == 'POST':
        url_item.delete()
        messages.success(request, _('URLを削除しました。'))
        return redirect('url_manager:url_list')
    
    return render(request, 'url_manager/url_delete.html', {'url_item': url_item})

@login_required
@staff_member_required

def url_check(request, url_id):
    """URL更新チェックビュー"""
    url_item = get_object_or_404(UrlItem, id=url_id, user=request.user)
    
    check_url_update.delay(url_item.id)
    
    messages.success(request, _('更新チェックを開始しました。'))
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success'})
    else:
        return redirect('url_manager:url_detail', url_id=url_item.id)

@login_required
def url_update_thumbnail(request, url_id):
    """URLサムネイル更新ビュー"""
    url_item = get_object_or_404(UrlItem, id=url_id, user=request.user)
    
    update_thumbnail.delay(url_item.id)
    
    messages.success(request, _('サムネイルの更新を開始しました。'))
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success'})
    else:
        return redirect('url_manager:url_detail', url_id=url_item.id)

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
                    
                if UrlItem.objects.filter(user=request.user, url=url_str).exists(): # pylint: disable=no-member
                    error_urls.append(f"{url_str} ({_('登録済み')})")
                    continue

                try:
                    title = get_page_title(url_str)
                    if not title:
                        title = url_str
                        messages.warning(request, _('URL "{url}" のタイトルを取得できませんでした。URLをタイトルとして使用します。').format(url=url_str))

                    url_item = UrlItem.objects.create( # pylint: disable=no-member
                        user=request.user,
                        url=url_str,
                        title=title,
                        check_type='HTML_STANDARD' # Default check type
                    )
                    check_url_update.delay(url_item.id)
                    update_thumbnail.delay(url_item.id)
                    added_count += 1
                except Exception as e:
                    print(f"Error adding URL {url_str}: {e}") # Basic logging for now
                    error_urls.append(f"{url_str} ({_('追加エラー')})") # Simplified error message

            if added_count > 0:
                messages.success(request, _('{count}件のURLを追加しました。').format(count=added_count))
            if error_urls:
                error_html = _('以下のURLは追加できませんでした:') + '<ul class="list-disc list-inside">' + "".join([f"<li>{err}</li>" for err in error_urls]) + "</ul>"
                messages.error(request, error_html, extra_tags='safe') 

            return redirect('url_manager:url_list')
    else:
        form = BulkUrlAddForm()
    
    return render(request, 'url_manager/url_bulk_add.html', {'form': form})
