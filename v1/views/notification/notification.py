from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

import constants

from ...pagination import StandardResultsSetPagination
from ...serializers import NotificationSerializer


class NotificationViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]

    serializer_class = NotificationSerializer

    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        user = self.request.user

        verbs = constants.Activity.NORMAL_VERBS
        if user.is_dlp:
            verbs = constants.Activity.DLP_VERBS

        return user.notifications.filter(verb__in=verbs)

    @action(methods=["get"], detail=False)
    def unread(self, request):
        limit = int(request.GET.get("limit", 10))
        notifications = self.get_queryset()
        notifications_unread = notifications.unread()[:limit]
        serializer = self.get_serializer(notifications_unread, many=True)
        return Response(serializer.data)

    @action(methods=["patch"], detail=True)
    def read(self, request, pk=None):
        notification = self.get_object()
        notification.unread = False
        notification.save()
        notification.refresh_from_db()

        serializer = self.get_serializer(notification)
        return Response(serializer.data)

    @action(methods=["patch"], detail=False)
    def read_all(self, request):
        self.get_queryset().mark_all_as_read()
        return Response({}, status=status.HTTP_204_NO_CONTENT)
