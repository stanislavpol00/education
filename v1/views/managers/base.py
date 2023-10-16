from rest_framework.views import APIView

from ...permissions import IsManagerUser
from ..mixins import ParamsConversionMixinView


class BaseManagerView(APIView, ParamsConversionMixinView):
    permission_classes = [IsManagerUser]
