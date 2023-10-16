import csv

from django.utils.functional import cached_property
from rest_framework import status
from rest_framework.test import APIClient

from .base_test import BaseTestCase


class BaseAPITestCase(BaseTestCase):
    @cached_property
    def authenticated_admin_client(self):
        client = APIClient()
        client.force_authenticate(user=self.admin_user)
        return client

    @cached_property
    def authenticated_manager_client(self):
        client = APIClient()
        client.force_authenticate(user=self.manager_user)
        return client

    @cached_property
    def authenticated_superuser_client(self):
        client = APIClient()
        client.force_authenticate(user=self.super_user)
        return client

    @cached_property
    def authenticated_dlp_client(self):
        client = APIClient()
        client.force_authenticate(user=self.experimental_user)
        return client

    @cached_property
    def authenticated_guest_client(self):
        client = APIClient()
        client.force_authenticate(user=self.guest_user)
        return client

    def get_main_client(self):
        return APIClient()

    @cached_property
    def forced_authenticated_client(self):
        client = APIClient()
        client.force_authenticate(user=self.normal_user)
        return client

    def get_authenticated_client(self, user):
        client = APIClient()
        client.force_authenticate(user=user)
        return client

    def _assert_export_data(
        self, response, field_name, include_records, exclude_records
    ):
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.has_header("Content-Disposition"))
        self.assertEqual(response["Content-Type"], "text/csv")

        lines = response.content.decode().splitlines()
        csv_reader = csv.DictReader(lines)
        result = [row[field_name] for row in csv_reader]

        self.assertEqual(len(include_records), len(result))
        for record in include_records:
            self.assertIn(record, result)
        for record in exclude_records:
            self.assertNotIn(record, result)

    def _assert_export_data_by_id(self, response, include_ids, exclude_ids):
        include_ids = [str(idx) for idx in include_ids]
        exclude_ids = [str(idx) for idx in exclude_ids]
        self._assert_export_data(response, "id", include_ids, exclude_ids)
