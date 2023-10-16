from django.urls import path

from . import views
from .routers import (
    episodes_router,
    examples_router,
    router,
    students_router,
    tips_router,
)

urlpatterns = [
    path("constants/", views.ConstantView.as_view(), name="constants"),
    path(
        "content-types/", views.ContentTypeView.as_view(), name="content_types"
    ),
    path(
        "recent-activities/",
        views.RecentActivityView.as_view(),
        name="recent-activities",
    ),
    path(
        "reports/contributions/",
        views.ContributionView.as_view(),
        name="reports-contributions",
    ),
    path(
        "reports/recent-tips/",
        views.RecentTipViewSet.as_view(),
        name="reports-recent-tips",
    ),
    path(
        "reports/recent-examples/",
        views.RecentExampleViewSet.as_view(),
        name="reports-recent-examples",
    ),
    path(
        "reports/top-rated-tips/",
        views.TopRatedTipViewSet.as_view(),
        name="reports-top-rated-tips",
    ),
    path(
        "reports/top-rated-examples/",
        views.TopRatedExampleViewSet.as_view(),
        name="reports-top-rated-examples",
    ),
    # for manager
    path(
        "managers/contributions/",
        views.ManagerContributionView.as_view(),
        name="managers-contributions",
    ),
    path(
        "managers/recent-tips/",
        views.ManagerRecentTipViewSet.as_view(),
        name="managers-recent-tips",
    ),
    path(
        "managers/recent-examples/",
        views.ManagerRecentExampleViewSet.as_view(),
        name="managers-recent-examples",
    ),
    path(
        "managers/users-grid/",
        views.ManagerUserGridView.as_view(),
        name="managers-users-grid",
    ),
]

urlpatterns += router.urls
urlpatterns += students_router.urls
urlpatterns += episodes_router.urls
urlpatterns += tips_router.urls
urlpatterns += examples_router.urls
