from django.shortcuts import render, redirect
from django.contrib.admin.views.decorators import staff_member_required

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
        return redirect('url_manager:url_list') # Redirect to URL list
    
    return render(request, 'core/home.html')

@login_required
def about(request):
    """アバウトページビュー"""
    return render(request, 'core/about.html')

@staff_member_required # Restrict check_all_urls to staff/superusers
def check_all_urls(request):
    """すべてのURL更新チェックビュー"""
    check_all_urls_task.delay(request.user.pk)
    
    messages.success(request, _('すべてのURLの更新チェックを開始しました。'))
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success'})
    else:
        return redirect('url_manager:url_list') # Redirect to URL list
