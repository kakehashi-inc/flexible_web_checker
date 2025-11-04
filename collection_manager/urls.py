from django.urls import path
from . import views

app_name = "collection_manager"

urlpatterns = [
    path("", views.collection_list, name="collection_list"),
    path("add/", views.collection_add, name="collection_add"),
    path("<int:collection_id>/", views.collection_detail, name="collection_detail"),
    path("<int:collection_id>/edit/", views.collection_edit, name="collection_edit"),
    path(
        "<int:collection_id>/delete/", views.collection_delete, name="collection_delete"
    ),
    path(
        "<int:collection_id>/add_url/<int:url_id>/",
        views.collection_add_url,
        name="collection_add_url",
    ),
    path(
        "<int:collection_id>/remove_url/<int:url_id>/",
        views.collection_remove_url,
        name="collection_remove_url",
    ),
]
