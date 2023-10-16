from rest_framework_nested import routers

from . import views

router = routers.SimpleRouter()

router.register("timelines", views.TimelineViewSet, basename="timelines")

router.register("users", views.UserViewSet, basename="users")

router.register("tasks", views.TaskViewSet, basename="tasks")

# examples router
router.register("examples", views.ExampleViewSet, basename="examples")

examples_router = routers.NestedSimpleRouter(
    router, "examples", lookup="example"
)
examples_router.register(
    "ratings", views.ExampleRatingViewSet, basename="example-ratings"
)

# tips router
router.register("tips", views.TipViewSet, basename="tips")

tips_router = routers.NestedSimpleRouter(router, "tips", lookup="tip")
tips_router.register("ratings", views.TipRatingViewSet, basename="tip-ratings")


# students router
router.register("students", views.StudentViewSet, basename="students")

students_router = routers.NestedSimpleRouter(
    router, "students", lookup="student"
)
students_router.register(
    "tips", views.StudentTipViewSet, basename="student-tips"
)
students_router.register(
    "episodes", views.StudentEpisodeViewSet, basename="student-episodes"
)
students_router.register(
    "activities", views.StudentActivitiesView, basename="student-activities"
)
router.register(
    "student-examples",
    views.StudentExampleViewSet,
    basename="student-examples",
)

# episode router
router.register("episodes", views.EpisodeViewSet, basename="episodes")

episodes_router = routers.NestedSimpleRouter(
    router, "episodes", lookup="episode"
)
episodes_router.register(
    "examples", views.EpisodeExampleViewSet, basename="episode-examples"
)

# notification router
router.register(
    "notifications",
    views.NotificationViewSet,
    basename="notifications",
)

# activity router
router.register(
    "activities",
    views.ActivityViewSet,
    basename="activities",
)

# tag router
router.register(
    "tags",
    views.TagViewSet,
    basename="tags",
)

# tagged item router
router.register(
    "tagged-items",
    views.TaggedItemViewSet,
    basename="tagged_items",
)
