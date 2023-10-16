from rest_framework.response import Response
from rest_framework.views import APIView

import constants

from ..permissions import IsAuthenticated


class ConstantView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        data = {}

        for constant_class_text in constants.__all__:
            constant_data = []
            constant_class = getattr(constants, constant_class_text)
            if not getattr(constant_class, "CHOICES", None):
                continue

            for row in constant_class.CHOICES:
                item = {
                    "name": row[0],
                    "description": row[1],
                }
                constant_data.append(item)

            data[constant_class_text] = constant_data

        return Response(data)
