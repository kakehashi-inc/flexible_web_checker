from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext_lazy as _
from django.contrib import messages
from django.http import JsonResponse
from .models import Collection, UrlItemCollection
from url_manager.models import UrlItem
from .forms import CollectionForm


@login_required
def collection_list(request):
    """コレクション一覧ビュー"""
    collections = Collection.objects.filter(user=request.user).order_by("order", "name")
    return render(
        request, "collection_manager/collection_list.html", {"collections": collections}
    )


@login_required
def collection_add(request):
    """コレクション追加ビュー"""
    if request.method == "POST":
        form = CollectionForm(request.POST)
        if form.is_valid():
            collection = form.save(commit=False)
            collection.user = request.user

            max_order = (
                Collection.objects.filter(user=request.user).order_by("-order").first()
            )
            collection.order = (max_order.order + 1) if max_order else 0

            collection.save()
            messages.success(request, _("コレクションを追加しました。"))
            return redirect(
                "collection_manager:collection_detail", collection_id=collection.pk
            )
    else:
        form = CollectionForm()

    return render(request, "collection_manager/collection_add.html", {"form": form})


@login_required
def collection_detail(request, collection_id):
    """コレクション詳細ビュー"""
    collection = get_object_or_404(Collection, pk=collection_id, user=request.user)
    url_items = UrlItem.objects.filter(collections__collection=collection).order_by(
        "-last_updated_at"
    )

    other_url_items = UrlItem.objects.filter(user=request.user).exclude(
        collections__collection=collection
    )

    return render(
        request,
        "collection_manager/collection_detail.html",
        {
            "collection": collection,
            "url_items": url_items,
            "other_url_items": other_url_items,
        },
    )


@login_required
def collection_edit(request, collection_id):
    """コレクション編集ビュー"""
    collection = get_object_or_404(Collection, pk=collection_id, user=request.user)

    if request.method == "POST":
        form = CollectionForm(request.POST, instance=collection)
        if form.is_valid():
            form.save()
            messages.success(request, _("コレクションを更新しました。"))
            return redirect(
                "collection_manager:collection_detail", collection_id=collection.pk
            )
    else:
        form = CollectionForm(instance=collection)

    return render(
        request,
        "collection_manager/collection_edit.html",
        {"form": form, "collection": collection},
    )


@login_required
def collection_delete(request, collection_id):
    """コレクション削除ビュー"""
    collection = get_object_or_404(Collection, pk=collection_id, user=request.user)

    if request.method == "POST":
        collection.delete()
        messages.success(request, _("コレクションを削除しました。"))
        return redirect("collection_manager:collection_list")

    return render(
        request, "collection_manager/collection_delete.html", {"collection": collection}
    )


@login_required
def collection_add_url(request, collection_id, url_id):
    """コレクションにURL追加ビュー"""
    collection = get_object_or_404(Collection, pk=collection_id, user=request.user)
    url_item = get_object_or_404(UrlItem, pk=url_id, user=request.user)

    if not UrlItemCollection.objects.filter(
        collection=collection, url_item=url_item
    ).exists():
        UrlItemCollection.objects.create(collection=collection, url_item=url_item)
        messages.success(request, _("URLをコレクションに追加しました。"))
    else:
        messages.info(request, _("このURLは既にコレクションに追加されています。"))

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({"status": "success"})
    else:
        return redirect(
            "collection_manager:collection_detail", collection_id=collection.pk
        )


@login_required
def collection_remove_url(request, collection_id, url_id):
    """コレクションからURL削除ビュー"""
    collection = get_object_or_404(Collection, pk=collection_id, user=request.user)
    url_item = get_object_or_404(UrlItem, pk=url_id, user=request.user)

    UrlItemCollection.objects.filter(collection=collection, url_item=url_item).delete()
    messages.success(request, _("URLをコレクションから削除しました。"))

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({"status": "success"})
    else:
        return redirect(
            "collection_manager:collection_detail", collection_id=collection.pk
        )
