from rest_framework.response import Response
from rest_framework.views import APIView

from main.models import ExampleRating

from ...permissions import IsAuthenticated
from ..mixins import ParamsConversionMixinView


class TopRatedExampleViewSet(APIView, ParamsConversionMixinView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        params = self.get_params_filters(request)
        days = params.get("days", 180)
        limit = params.get("limit", 10)

        examples = ExampleRating.objects.top_rated(days=days, limit=limit)

        data = self.serialize_data(examples)

        return Response(data)

    def serialize_data(self, queryset):
        return queryset
