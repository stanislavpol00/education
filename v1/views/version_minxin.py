from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from reversion.models import Version

from ..permissions import IsManagerUser


class VersionViewMixin:
    @action(detail=True, methods=["get"], permission_classes=[IsManagerUser])
    def versions(self, request, pk=None):
        obj = self.get_object()
        versions = Version.objects.get_for_object(obj)
        version_id = request.query_params.get("version", None)
        if version_id:
            versions = versions.filter(pk=version_id)
        obj_versions = []
        for version in versions:
            field_dict = version.field_dict
            field_dict["version_id"] = version.pk

            # remove tags field
            if "tags" in field_dict:
                field_dict.pop("tags")

            obj_versions.append(field_dict)
        return Response(obj_versions, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], permission_classes=[IsManagerUser])
    def recover(self, request, pk=None):
        obj = self.get_object()
        obj_version = Version.objects.get_for_object(obj)
        version_id = request.POST.get("version", None)
        if version_id:
            obj_version = obj_version.filter(pk=version_id).first()
        else:
            obj_version = obj_version[1]

        obj_version.revision.revert()
        return Response({"message": "Success"}, status=status.HTTP_200_OK)
