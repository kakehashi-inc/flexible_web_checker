from django.urls import path

from bookmark.views import i18n
from bookmark.views import user_accounts
from bookmark.views import url_manager
from bookmark.views import collection_manager
from bookmark.views import core

app_name = "bookmark"

urlpatterns = [
    # i18n
    path("i18n/setlang/", i18n.set_language_view, name="set_language"),

    # Core
    path("", core.home, name="home"),
    path("about/", core.about, name="about"),
    path("check_all/", core.check_all_urls, name="check_all_urls"),

    # User Accounts
    path("register/", user_accounts.register, name="register"),
    path("login/", user_accounts.login_view, name="login"),
    path("logout/", user_accounts.logout_view, name="logout"),
    path("mypage/", user_accounts.profile, name="mypage"),
    path("mypage/edit/", user_accounts.edit_profile, name="edit_mypage"),
    path("verify-email/<uuid:token>/", user_accounts.verify_email, name="verify_email"),
    path("password/reset/", user_accounts.password_reset_request, name="password_reset_request"),
    path("password/reset/<uuid:token>/", user_accounts.password_reset, name="password_reset"),
    path(
        "password/change/",
        user_accounts.PasswordChangeView.as_view(),
        name="password_change",
    ),
    path(
        "password/change/done/",
        user_accounts.PasswordChangeDoneView.as_view(),
        name="password_change_done",
    ),

    # URL Manager
    path("urls/", url_manager.url_list, name="url_list"),
    path("urls/add/", url_manager.url_add, name="url_add"),
    path("urls/bulk_add/", url_manager.url_bulk_add, name="url_bulk_add"),
    path("urls/<int:url_id>/", url_manager.url_detail, name="url_detail"),
    path("urls/<int:url_id>/edit/", url_manager.url_edit, name="url_edit"),
    path("urls/<int:url_id>/delete/", url_manager.url_delete, name="url_delete"),
    path("urls/<int:url_id>/check/", url_manager.url_check, name="url_check"),
    path(
        "urls/<int:url_id>/thumbnail/",
        url_manager.url_update_thumbnail,
        name="url_update_thumbnail",
    ),

    # Collection Manager
    path("collections/", collection_manager.collection_list, name="collection_list"),
    path("collections/add/", collection_manager.collection_add, name="collection_add"),
    path("collections/<int:collection_id>/", collection_manager.collection_detail, name="collection_detail"),
    path("collections/<int:collection_id>/edit/", collection_manager.collection_edit, name="collection_edit"),
    path(
        "collections/<int:collection_id>/delete/",
        collection_manager.collection_delete,
        name="collection_delete"
    ),
    path(
        "collections/<int:collection_id>/add_url/<int:url_id>/",
        collection_manager.collection_add_url,
        name="collection_add_url",
    ),
    path(
        "collections/<int:collection_id>/remove_url/<int:url_id>/",
        collection_manager.collection_remove_url,
        name="collection_remove_url",
    ),
]
