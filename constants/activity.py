from django.utils.translation import gettext_lazy as _


class Activity:
    # tip
    READ_TIP = "read_tip"
    TRY_TIP = "try_tip"
    COMMENT_TIP = "comment_tip"
    RATE_TIP = "rate_tip"
    CREATE_TIP = "create_tip"
    UPDATE_TIP = "update_tip"
    SUGGEST_TIP = "suggest_tip"
    SET_TIP_EDIT_MARK = "set_tip_edit_mark"
    REMOVE_TIP_EDIT_MARK = "remove_tip_edit_mark"
    ATTACH_RELATED_TIPS_WITH_TIP = "attach_related_tips_with_tip"
    DETACH_RELATED_TIPS_WITH_TIP = "detach_related_tips_with_tip"

    ATTACH_TIP_WITH_EXAMPLE = "attach_tip_with_example"
    DETACH_TIP_FROM_EXAMPLE = "detach_tip_from_example"

    # example
    CREATE_EXAMPLE = "create_example"
    UPDATE_EXAMPLE = "update_example"
    RATE_EXAMPLE = "rate_example"
    TOGGLE_EXAMPLE_BOOKMARK = "toggle_example_bookmark"

    # episode
    CREATE_EPISODE = "create_episode"
    UPDATE_EPISODE = "update_episode"

    # student
    ASSIGN_STUDENT = "assign_student"
    UNASSIGN_STUDENT = "unassign_student"
    CREATE_STUDENT = "create_student"
    ASSIGN_TIP_TO_STUDENT = "assign_tip_to_student"
    ASSIGN_EXAMPLE_TO_STUDENT = "assign_example_to_student"

    RATING_REMINDER = "rating_reminder"

    CHOICES = [
        # tip
        (READ_TIP, _("Read Tip")),
        (TRY_TIP, _("Try Tip")),
        (COMMENT_TIP, _("Comment Tip")),
        (RATE_TIP, _("Rate Tip")),
        (CREATE_TIP, _("Create Tip")),
        (UPDATE_TIP, _("Update Tip")),
        (SUGGEST_TIP, _("Suggest Tip")),
        (SET_TIP_EDIT_MARK, _("SET TIP EDIT MARK")),
        (REMOVE_TIP_EDIT_MARK, _("REMOVE TIP EDIT MARK")),
        (ATTACH_RELATED_TIPS_WITH_TIP, _("Attach Related Tips With Tip")),
        (DETACH_RELATED_TIPS_WITH_TIP, _("Detach Related Tips With Tip")),
        (ATTACH_TIP_WITH_EXAMPLE, _("Attach Tip With Example")),
        (DETACH_TIP_FROM_EXAMPLE, _("Detach Tip With Example")),
        # example
        (CREATE_EXAMPLE, _("Create Example")),
        (UPDATE_EXAMPLE, _("Update Example")),
        (RATE_EXAMPLE, _("Rate Example")),
        # episode
        (CREATE_EPISODE, _("Create Episode")),
        (UPDATE_EPISODE, _("Update Episode")),
        # students
        (ASSIGN_STUDENT, _("Assign Student")),
        (UNASSIGN_STUDENT, _("Unassign Student")),
        (CREATE_STUDENT, _("Create Student")),
        (ASSIGN_TIP_TO_STUDENT, _("Assign Tip To Student")),
        (ASSIGN_EXAMPLE_TO_STUDENT, _("Assign Example To Student")),
        (RATING_REMINDER, _("Rating Reminder")),
    ]

    DLP_VERBS = [
        SUGGEST_TIP,
    ]
    NORMAL_VERBS = [
        CREATE_EPISODE,
        SUGGEST_TIP,
        ASSIGN_STUDENT,
        SET_TIP_EDIT_MARK,
        ATTACH_RELATED_TIPS_WITH_TIP,
        ATTACH_TIP_WITH_EXAMPLE,
        RATING_REMINDER,
    ]
    REPRESENTED_VERBS = [
        CREATE_EPISODE,
        SUGGEST_TIP,
        ASSIGN_STUDENT,
        SET_TIP_EDIT_MARK,
        ATTACH_RELATED_TIPS_WITH_TIP,
        ATTACH_TIP_WITH_EXAMPLE,
    ]
