from django.urls import path
from . import views

app_name = "url_manager"

urlpatterns = [
    path("", views.url_list, name="url_list"),
    path("add/", views.url_add, name="url_add"),
    path("bulk_add/", views.url_bulk_add, name="url_bulk_add"), # Bulk add URL

    path("<int:url_id>/", views.url_detail, name="url_detail"),
    path("<int:url_id>/edit/", views.url_edit, name="url_edit"),
    path("<int:url_id>/delete/", views.url_delete, name="url_delete"),
    path("<int:url_id>/check/", views.url_check, name="url_check"),
    path(
        "<int:url_id>/thumbnail/",
        views.url_update_thumbnail,
        name="url_update_thumbnail",
    ),
]
