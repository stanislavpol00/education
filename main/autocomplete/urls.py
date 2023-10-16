from django.urls import path

from .views import (
    EpisodeAutocompleteView,
    StudentAutocompleteView,
    TagAutocompleteView,
    TipAutocompleteView,
    UserAutocompleteView,
)

urlpatterns = [
    path(
        "user/",
        UserAutocompleteView.as_view(),
        name="user",
    ),
    path(
        "student/",
        StudentAutocompleteView.as_view(),
        name="student",
    ),
    path(
        "episode/",
        EpisodeAutocompleteView.as_view(),
        name="episode",
    ),
    path(
        "tag/",
        TagAutocompleteView.as_view(),
        name="tag",
    ),
    path(
        "tip/",
        TipAutocompleteView.as_view(),
        name="tip",
    ),
]
