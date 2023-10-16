from django.core import mail
from django.urls import reverse
from rest_framework import status
from rest_framework_simplejwt.state import token_backend

from tests.base_api_test import BaseAPITestCase


class TestJWTAPI(BaseAPITestCase):
    def test_rest_login_success_with_email(self):
        client = self.get_main_client()
        url = reverse("api-token-auth")
        data = {
            "email": self.normal_user.email,
            "password": self.normal_password,
        }

        response = client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        jwt_token = response.json()["token"]
        token = token_backend.decode(jwt_token)
        self.assertEqual(token["email"], self.normal_user.email)
        self.assertEqual(token["username"], self.normal_user.username)

    def test_rest_login_success_with_username(self):
        client = self.get_main_client()
        url = reverse("api-token-auth")
        data = {
            "username": self.normal_user.username,
            "password": self.normal_password,
        }

        response = client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        jwt_token = response.json()["token"]
        token = token_backend.decode(jwt_token)
        self.assertEqual(token["email"], self.normal_user.email)
        self.assertEqual(token["username"], self.normal_user.username)

    def test_rest_login_fail_with_wrong_email(self):
        client = self.get_main_client()
        url = reverse("api-token-auth")
        data = {
            "email": "wrong_email@gmail.com",
            "password": self.normal_password,
        }

        response = client.post(url, data, format="json")

        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

        self.assertIn("non_field_errors", response.data)

    def test_rest_login_fail_with_wrong_username(self):
        client = self.get_main_client()
        url = reverse("api-token-auth")
        data = {
            "username": "wrong_username",
            "password": self.normal_password,
        }

        response = client.post(url, data, format="json")

        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

        self.assertIn("non_field_errors", response.data)

    def test_rest_login_fail_as_user_inactive(self):
        client = self.get_main_client()
        url = reverse("api-token-auth")
        user_data = self.create_user()
        user = user_data["user"]
        user.is_active = False
        user.save()
        data = {
            "email": user_data["user"].email,
            "password": user_data["password"],
        }

        response = client.post(url, data, format="json")

        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

        self.assertIn("non_field_errors", response.data)

    def test_get_jwt_token_success(self):
        pass

    def test_get_jwt_token_fail(self):
        pass

    def test_change_password_success(self):
        self.assertTrue(self.normal_user.check_password(self.normal_password))
        self.assertFalse(self.normal_user.check_password("Abc123Def"))

        url = reverse("api-auth:rest_password_change")
        data = {
            "old_password": self.normal_password,
            "new_password1": "Abc123Def",
            "new_password2": "Abc123Def",
        }

        response = self.forced_authenticated_client.post(
            url, data, format="json"
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        self.normal_user.refresh_from_db()
        self.assertFalse(self.normal_user.check_password(self.normal_password))
        self.assertTrue(self.normal_user.check_password("Abc123Def"))

    def test_change_password_fail(self):
        self.assertTrue(self.normal_user.check_password(self.normal_password))
        self.assertFalse(
            self.normal_user.check_password("wrong passs1ss1worddd")
        )
        self.assertFalse(self.normal_user.check_password("Abc123Def"))

        url = reverse("api-auth:rest_password_change")
        data = {
            "old_password": "wrong passs1ss1worddd",
            "new_password1": "Abc123Def",
            "new_password2": "Abc123Def",
        }

        response = self.forced_authenticated_client.post(
            url, data, format="json"
        )

        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

        self.assertIn("old_password", response.data)

    def test_password_reset_success(self):
        client = self.get_main_client()
        url = reverse("drf-password-reset:reset-password-request")

        data = {"email": self.normal_email}

        response = client.post(url, data, format="json")

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        # check send email successfully
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(
            mail.outbox[0].subject,
            "Your password reset request!",
        )

        # check confirm reset password successfully
        body = mail.outbox[0].body
        token = body[body.index("token=") + 6 : body.index("token=") + 12]

        data = {"token": token, "password": "new_password"}

        response = client.post(
            reverse("drf-password-reset:reset-password-confirm"),
            data,
            format="json",
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        self.normal_user.refresh_from_db()
        self.assertFalse(self.normal_user.check_password(self.normal_password))
        self.assertTrue(self.normal_user.check_password("new_password"))

    def test_password_reset_fail_with_email_not_found(self):
        client = self.get_main_client()
        url = reverse("drf-password-reset:reset-password-request")

        data = {"email": "email_not_found@gmail.com"}

        response = client.post(url, data, format="json")

        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

        self.assertIn("email", response.data)

    def test_password_reset_confirm_fail(self):
        client = self.get_main_client()

        data = {"token": "invalid token", "password": "new_password"}

        response = client.post(
            reverse("drf-password-reset:reset-password-confirm"),
            data,
            format="json",
        )

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_get_user_success(self):
        expected_detail_keys = [
            "id",
            "first_name",
            "last_name",
            "full_name",
            "username",
            "email",
            "date_joined",
            "is_staff",
            "role",
            "role_description",
            "photo_url",
            "photo_width",
            "photo_height",
            "is_team_lead",
            "assigned_students",
            "is_active",
            "unique_tried_tips_count",
            "tried_tips_total",
            "assigned_tips_count",
            "professional_goal",
            "role_assignments",
        ]

        url = reverse("api-auth:rest_user_details")
        response = self.forced_authenticated_client.get(url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        self.assertEqual(
            sorted(expected_detail_keys), sorted(response.data.keys())
        )

        self.assertEqual(self.normal_user.id, response.data["id"])

    def test_get_user_fail(self):
        pass

    def test_rest_login_success_with_check_last_login(self):
        last_login = self.normal_user.last_login
        self.assertIsNone(last_login)

        client = self.get_main_client()
        url = reverse("api-token-auth")
        data = {
            "username": self.normal_user.username,
            "password": self.normal_password,
        }

        response = client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.normal_user.refresh_from_db()
        new_last_login = self.normal_user.last_login

        self.assertIsNotNone(new_last_login)

    def test_rest_login_success_with_check_ip_address(self):

        client = self.get_main_client()
        url = reverse("api-token-auth")
        data = {
            "username": self.normal_user.username,
            "password": self.normal_password,
        }

        response = client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
