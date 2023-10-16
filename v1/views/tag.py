from taggit.models import Tag

from ..filters import TagFilter
from ..permissions import IsManagerUser
from ..serializers import TagSerializer
from .base import BaseStandardPaginationViewSet


class TagViewSet(BaseStandardPaginationViewSet):
    permission_classes = [IsManagerUser]

    serializer_class = TagSerializer

    filterset_class = TagFilter

    def get_queryset(self):
        queryset = Tag.objects.all()

        return queryset
