from dj_rest_auth.views import LoginView
from ipware import get_client_ip
from rest_framework import status

from tasks.user import update_last_login, update_user_ip


class CustomLoginView(LoginView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        if response.status_code == status.HTTP_200_OK:
            username_or_email = request.data.get(
                "username"
            ) or request.data.get("email")
            user_ip, _ = get_client_ip(request)

            update_last_login.delay(username_or_email)
            update_user_ip.delay(username_or_email, user_ip)

        return response
