from django.db.models import Value
from django.db.models.functions import Concat
from django.utils.translation import gettext_lazy as _
from PIL import Image
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.exceptions import ParseError, ValidationError
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework_simplejwt.state import token_backend

from main.models import User
from libs.jwt_auth import custom_jwt_payload_handler
from libs.serializers import ReadWriteSerializerMixin

from ..filters import UserFilter
from ..permissions import IsManagerUser, IsOwnerOrManager
from ..serializers import (
    AssignStudentSerializer,
    UnAssignStudentSerializer,
    UserChangeSerializer,
    UserCreationSerializer,
    UserSerializer,
)
from .base import BaseStandardPaginationReadOnlyViewSet


class UserViewSet(
    ReadWriteSerializerMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    BaseStandardPaginationReadOnlyViewSet,
):
    permission_classes = [IsOwnerOrManager]

    read_serializer_class = UserSerializer

    filterset_class = UserFilter

    ordering_fields = ["first_name", "last_name", "full_name", "date_joined"]
    ordering = ["id"]

    def get_queryset(self):
        queryset = User.objects.annotate_tips_count()

        queryset = queryset.annotate(
            full_name=Concat("first_name", Value(" "), "last_name")
        ).select_related("profile")

        return queryset

    def get_permissions(self):
        if self.action == "create":
            self.permission_classes = [IsManagerUser]

        return super().get_permissions()

    def get_write_serializer_class(self):
        if self.action == "create":
            self.write_serializer_class = UserCreationSerializer
        else:
            self.write_serializer_class = UserChangeSerializer

        return super().get_write_serializer_class()

    @action(
        detail=True,
        methods=["post"],
        url_path="assign-students",
        permission_classes=[IsManagerUser],
    )
    def assign_students(self, request, pk=None):
        user = self.get_object()
        data = request.data
        data["practitioner"] = user.id
        serializer = AssignStudentSerializer(
            data=data, context={"request": request}
        )

        if serializer.is_valid():
            serializer.save()
            return Response(
                {"status": "created"}, status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=True,
        methods=["post"],
        url_path="unassign-students",
        permission_classes=[IsManagerUser],
    )
    def unassign_students(self, request, pk=None):
        user = self.get_object()
        data = request.data
        data["practitioner"] = user.id
        serializer = UnAssignStudentSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                {"status": _("remove assigned student successfully")},
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=True,
        methods=["patch"],
        url_path="upload-photo",
        parser_classes=[MultiPartParser],
    )
    def upload_photo(self, request, pk=None):
        user = self.get_object()

        if "file" not in request.data:
            raise ValidationError(_("Input data is invalid"))

        file = request.data["file"]

        try:
            img = Image.open(file)
            img.verify()
        except Exception:
            raise ParseError(_("Unsupported image type"))

        user.profile.photo.save(file.name, file, save=True)
        return Response(
            {"message": _("Upload image successfully")},
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["post"], permission_classes=[IsManagerUser])
    def jwt(self, request, pk=None):
        user = self.get_object()

        payload = custom_jwt_payload_handler(user)
        token = token_backend.encode(payload)

        return Response({"token": token})
