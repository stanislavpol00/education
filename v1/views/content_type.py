from django.contrib.contenttypes.models import ContentType
from rest_framework.response import Response
from rest_framework.views import APIView

from ..permissions import IsAuthenticated


class ContentTypeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        content_types = ContentType.objects.filter(app_label="main")

        data = []
        for content_type in content_types:
            item = {"id": content_type.id, "model": content_type.model}

            data.append(item)

        return Response(data)
