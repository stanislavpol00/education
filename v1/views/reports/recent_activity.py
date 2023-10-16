from django.contrib.contenttypes.models import ContentType
from rest_framework.response import Response
from rest_framework.views import APIView

from main.models import Example, Tip

from ...permissions import IsAuthenticated
from ...serializers import (
    RecentActivityExampleSerializer,
    RecentActivityTipSerializer,
)
from ..mixins import ParamsConversionMixinView


class RecentActivityView(APIView, ParamsConversionMixinView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        params = self.get_params_filters(request)
        user = request.user

        activities = user.get_activities(**params)

        serialized_data = self.serialize_data(activities)

        return Response(serialized_data)

    def get_all_action_objects(self, activities):
        actions = activities

        content_types = ContentType.objects.get_for_models(
            Tip, Example
        )
        tips = Tip.objects.annotate_contributed_at(
            actions.get(content_types[Tip].id)
        )
        examples = Example.objects.annotate_contributed_at(
            actions.get(content_types[Example].id),
            select_related=["added_by", "updated_by"],
        )

        return {
            Tip: tips,
            Example: examples,
        }

    def serialize_data(self, activities):
        all_action_objects = self.get_all_action_objects(activities)

        data = {
            "tips": RecentActivityTipSerializer(
                all_action_objects[Tip].values(), many=True
            ).data,
            "examples": RecentActivityExampleSerializer(
                all_action_objects[Example].values(),
                many=True,
            ).data,
        }

        return data
