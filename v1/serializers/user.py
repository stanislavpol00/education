from django.contrib.auth.hashers import make_password
from django.db import transaction
from django.utils.crypto import get_random_string
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

import constants
from main.models import RoleAssignment, User

from .student import StudentSerializer


class UserSerializer(serializers.ModelSerializer):
    assigned_students = StudentSerializer(many=True)
    unique_tried_tips_count = serializers.IntegerField(default=0)
    tried_tips_total = serializers.IntegerField(default=0)
    assigned_tips_count = serializers.IntegerField(default=0)

    class Meta:
        model = User
        fields = [
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
        read_only_fields = fields


class LightUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "full_name",
        ]


class UserChangeSerializer(serializers.ModelSerializer):
    usertype = serializers.CharField(required=False)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "is_active",
            "role",
            "usertype",
            "professional_goal",
            "role_assignments",
        ]
        read_only_fields = ["id"]

    def validate_usertype(self, usertype):
        if usertype not in constants.UserType.ALL:
            raise serializers.ValidationError(_("Usertype is invalid"))
        return usertype

    def validate(self, data):
        user = self.context.get("request").user
        if ("role" in data or "is_active" in data) and not user.is_manager:
            raise serializers.ValidationError(
                _("You do not allow update these fields")
            )

        return data

    @transaction.atomic
    def update(self, instance, validated_data):
        user = self.context.get("request").user
        if instance.is_manager and user.id != instance.id:
            raise serializers.ValidationError(
                _("You do not allow update these fields")
            )

        if "usertype" in validated_data:
            usertype = validated_data.pop("usertype")
            profile = instance.profile
            profile.usertype = usertype
            profile.save()

        # create default Role Assignment if needed.
        RoleAssignment.objects.create_default(instance)

        return super().update(instance, validated_data)

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        representation["usertype"] = instance.profile.usertype

        return representation


class UserCreationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "role",
            "role_assignments",
        ]
        read_only_fields = ["id"]

    def validate_role(self, role):
        if role in constants.Role.MANAGERS:
            raise serializers.ValidationError(_("Role is invalid"))
        return role

    @transaction.atomic
    def create(self, validated_data):
        self.initial_data["password"] = get_random_string(length=16)

        validated_data["password"] = make_password(
            self.initial_data["password"]
        )
        user = User.objects.create(**validated_data)

        reset_password_token = user.create_reset_password_token(
            self.context["request"]
        )
        user.send_registered_email(reset_password_token)

        # create default Role Assignment if needed.
        RoleAssignment.objects.create_default(user)

        return user

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        representation["password"] = self.initial_data["password"]

        return representation


class UserAuthSerializer(serializers.ModelSerializer):
    photo_url = serializers.SerializerMethodField()
    photo_width = serializers.IntegerField(source="profile.photo_width")
    photo_height = serializers.IntegerField(source="profile.photo_height")

    def get_photo_url(self, obj):
        request = self.context.get("request")
        try:
            photo_url = obj.profile.photo.url
            return request.build_absolute_uri(photo_url)
        except ValueError:
            return None

    class Meta:
        model = User
        fields = [
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
            "is_team_lead",
            "is_active",
            "professional_goal",
            "role_assignments",
        ]

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        user = (
            User.objects.annotate_tips_count().filter(pk=instance.id).first()
        )
        representation["assigned_students"] = StudentSerializer(
            user.assigned_students, many=True
        ).data

        representation[
            "unique_tried_tips_count"
        ] = user.unique_tried_tips_count
        representation["tried_tips_total"] = user.tried_tips_total
        representation["assigned_tips_count"] = user.assigned_tips_count

        return representation
