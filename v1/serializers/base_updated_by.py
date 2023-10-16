from django.utils.translation import gettext_lazy as _
from rest_framework import serializers


class BaseUpdatedBySerializer(serializers.ModelSerializer):
    user_fields = ["added_by", "created_by", "user"]

    def validate(self, data):
        data = super().validate(data)
        user = self.context["request"].user
        if not user.is_authenticated:
            raise serializers.ValidationError(
                _("The user is not authenticated")
            )

        if (
            self.Meta.read_only_fields
            and "updated_by" in self.Meta.read_only_fields
        ):
            data["updated_by"] = user

        return data

    def create(self, validated_data):
        user = self.context["request"].user

        for field in self.user_fields:
            if (
                self.Meta.read_only_fields
                and field in self.Meta.read_only_fields
            ):
                validated_data[field] = user

        return super().create(validated_data)
