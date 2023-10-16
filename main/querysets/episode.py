import constants
from libs.querysets import BaseQuerySet


class EpisodeQuerySet(BaseQuerySet):
    DEFAULT_SEARCH_ICONTAINS_FIELDS = {
        "title": "example__tip__title",
        "description": "example__tip__description",
        "sub_goal": "example__tip__sub_goal",
        "example_description": "example__description",
    }
    DEFAULT_SEARCH_JSON_FIELDS = {
        "child_context": {
            "name": "example__tip__child_context",
            "values": constants.ChildContext.VALUES,
        },
        "environment_context": {
            "name": "example__tip__environment_context",
            "values": constants.Environment.VALUES,
        },
    }
