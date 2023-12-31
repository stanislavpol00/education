class Group:
    ORGANIZATION_GUEST = "ORGANIZATION_GUEST"
    ORGANIZATION_DLP = "ORGANIZATION_DLP"
    ORGANIZATION_STAFF = "ORGANIZATION_STAFF"
    ORGANIZATION_ADMIN = "ORGANIZATION_ADMIN"

    ALL_ORGANIZATION_ROLES = [
        ORGANIZATION_GUEST,
        ORGANIZATION_DLP,
        ORGANIZATION_STAFF,
        ORGANIZATION_ADMIN,
    ]
    CHOICES = [(group, group) for group in ALL_ORGANIZATION_ROLES]

    ORGANIZATION_ROLES_ORDERING = {
        ORGANIZATION_GUEST: 0,
        ORGANIZATION_DLP: 1,
        ORGANIZATION_STAFF: 2,
        ORGANIZATION_ADMIN: 3,
    }
