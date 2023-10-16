from django.utils.translation import gettext_lazy as _


class HeadsUp:
    PLAY_THEMES = "PLAY_THEMES"
    PREFERRED_OBJECTS = "PREFERRED_OBJECTS"
    NEW_CONNECTIONS = "NEW_CONNECTIONS"
    PEER_CONFLICTS = "PEER_CONFLICTS"
    ROUTINE_CHANGES = "ROUTINE_CHANGES"
    NEW_BEHAVIORS = "NEW_BEHAVIORS"
    CELEBRATIONS = "CELEBRATIONS"
    SHADOW_TO_DOS = "SHADOW_TO_DOS"
    MISCELLANEOUS_OBSERVATIONS = "MISCELLANEOUS_OBSERVATIONS"
    UPCOMING_EVENTS = "UPCOMING_EVENTS"

    CHOICES = [
        (PLAY_THEMES, _("Play Themes")),
        (PREFERRED_OBJECTS, _("Preferred Objects")),
        (NEW_CONNECTIONS, _("New Connections")),
        (PEER_CONFLICTS, _("Peer Conflicts")),
        (ROUTINE_CHANGES, _("Routine Changes")),
        (NEW_BEHAVIORS, _("New Behaviors")),
        (SHADOW_TO_DOS, _("Shadow To Dos")),
        (MISCELLANEOUS_OBSERVATIONS, _("Miscellaneous Observations")),
        (UPCOMING_EVENTS, _("Upcoming Events")),
    ]
