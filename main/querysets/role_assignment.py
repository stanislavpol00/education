from django.contrib.auth.models import Group
from django.db import models
from django.db.transaction import atomic
from django.utils.translation import gettext as _
from rest_framework.serializers import ValidationError

import constants


class RoleAssignmentQuerySet(models.QuerySet):
    @atomic
    def create_or_update_for_user(self, user, by_user, role_assignments_data):
        errors = []
        for role_assignment in role_assignments_data:
            organization = role_assignment["organization"]
            role = role_assignment["group_name"]
            if by_user.can_manage_organization_role(organization.id, role):
                self._create_or_update(user, role_assignment)
            else:
                errors.append(str(organization.id))

        if errors:
            raise ValidationError(
                _(
                    "Cannot creating or updating user's roles, "
                    "dues to have no approviate permissions "
                    "in these organization: {}"
                ).format(",".join(errors))
            )

    def _create_or_update(self, user, role_assignment_data):
        role_assignment = self.filter(
            user=user, organization=role_assignment_data["organization"]
        ).first()
        if role_assignment:
            if role_assignment.group != role_assignment_data["group"]:
                role_assignment.group = role_assignment_data["group"]
                role_assignment.save()
        else:
            role_assignment = self.create(
                user=user,
                organization=role_assignment_data["organization"],
                group=role_assignment_data["group"],
            )

    def create_default(self, user):
        from main.models import Organization

        if user.roleassignment_set.exists():
            return

        default_organization = Organization.objects.get(
            name=constants.Organization.DEFAULT_ORGANIZATION
        )

        group_name = constants.Role.role_to_group_name(user.role)
        group = Group.objects.filter(name=group_name).first()
        if group:
            self.create(
                user=user,
                group=group,
                organization=default_organization,
            )
