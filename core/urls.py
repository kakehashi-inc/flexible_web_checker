from django.urls import path
from . import views

app_name = "core"

urlpatterns = [
    path("", views.home, name="home"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("about/", views.about, name="about"),
    path("check_all/", views.check_all_urls, name="check_all_urls"),
]
