from rest_framework.permissions import SAFE_METHODS
from taggit.models import TaggedItem

from ..filters import TaggedItemFilter
from ..permissions import IsManagerUser
from ..serializers import LightweightTaggedItemSerializer, TaggedItemSerializer
from .base import BaseStandardPaginationViewSet


class TaggedItemViewSet(BaseStandardPaginationViewSet):
    permission_classes = [IsManagerUser]

    serializer_class = TaggedItemSerializer

    filterset_class = TaggedItemFilter

    def get_queryset(self):
        queryset = TaggedItem.objects.select_related("tag")

        return queryset

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return TaggedItemSerializer
        return LightweightTaggedItemSerializer
