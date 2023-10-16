from rest_framework import serializers
from rest_framework_simplejwt.state import token_backend

from libs.jwt_auth import custom_jwt_payload_handler


class CustomJWTSerializer(serializers.Serializer):
    token = serializers.CharField()

    def to_representation(self, instance):
        payload = custom_jwt_payload_handler(instance["user"])
        expected_token = token_backend.encode(payload)
        instance["token"] = expected_token
        return super().to_representation(instance)
