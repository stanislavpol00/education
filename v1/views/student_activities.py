from rest_framework import mixins
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from main.models import Student

from ..filters import StudentActivitiesFilter
from ..permissions import IsAuthenticated
from ..serializers import StudentActivitiesSerializer


class StudentActivitiesView(mixins.ListModelMixin, GenericViewSet):
    permission_classes = [IsAuthenticated]

    serializer_class = StudentActivitiesSerializer

    filterset_class = StudentActivitiesFilter

    queryset = Student.objects.all()

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        student_id = self.kwargs["student_pk"]
        queryset = queryset.filter(pk=student_id).first()

        if not queryset:
            raise NotFound("student_id is invalid")

        serializer = self.get_serializer(queryset)
        return Response(serializer.data)
