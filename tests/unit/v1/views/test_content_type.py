from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from rest_framework import status

from tests.base_api_test import BaseAPITestCase


class TestContentTypeAPI(BaseAPITestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.url = reverse("v1:content_types")

    def test_get_content_types_success(self):
        response = self.forced_authenticated_client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        content_types_count = ContentType.objects.filter(
            app_label="main"
        ).count()

        self.assertEqual(content_types_count, len(response.data))
