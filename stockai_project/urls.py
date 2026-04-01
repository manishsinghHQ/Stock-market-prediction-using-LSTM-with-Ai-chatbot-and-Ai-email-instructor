from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("pages.urls", namespace="pages")),

    path("accounts/", include(("accounts.urls", "accounts"), namespace="accounts")),
    path("dashboard/", include(("dashboard.urls", "dashboard"), namespace="dashboard")),
    path("api/", include(("core.api_urls", "core"), namespace="core_api")),
     # default home -> dashboard
]







