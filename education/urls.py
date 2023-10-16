"""URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path
from rest_framework_simplejwt.views import TokenVerifyView

from libs.jwt_auth.custom_login import CustomLoginView

urlpatterns = [
    re_path(r"^admin/", admin.site.urls),
    re_path(
        r"^autocomplete/",
        include(
            ("main.autocomplete.urls", "main.autocomplete"),
            namespace="autocomplete",
        ),
    ),
    re_path(
        r"^api-token-auth/",
        CustomLoginView.as_view(),
        name="api-token-auth",
    ),  # End point for JWT authentication with password.
    re_path(
        r"^api-token-verify/",
        TokenVerifyView.as_view(),
        name="api-token-verify",
    ),  # Veryfy JWT.
    re_path(r"^api-auth/", include(("dj_rest_auth.urls", "api-auth"))),
    re_path(
        r"^api-auth/password-reset/",
        include(
            "django_rest_passwordreset.urls", namespace="drf-password-reset"
        ),
    ),
    re_path(r"^v1/", include(("v1.urls", "v1"))),
]
urlpatterns = (
    static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + urlpatterns
)

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [
        path("__debug__/", include(debug_toolbar.urls))
    ] + urlpatterns
