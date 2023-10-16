from django.db.models import Avg
from import_export import resources
from import_export.fields import Field

from main.models import ExampleRating, TipRating


class TipRatingResource(resources.ModelResource):
    user_id = Field()
    name = Field()
    title = Field()
    clarity_examples = Field()
    rate_number = Field()

    class Meta:
        model = TipRating
        fields = (
            "clarity",
            "relevance",
            "uniqueness",
            "try_comment",
            "tried_at",
            "comment",
            "commented_at",
            "created_at",
        )
        export_order = (
            "user_id",
            "name",
            "title",
            "clarity",
            "uniqueness",
            "clarity_examples",
            "relevance",
            "rate_number",
            "try_comment",
            "tried_at",
            "comment",
            "commented_at",
            "created_at",
        )

    def dehydrate_user_id(self, tip_rating):
        return tip_rating.added_by_id

    def dehydrate_name(self, tip_rating):
        return tip_rating.added_by.full_name

    def dehydrate_title(self, tip_rating):
        return tip_rating.tip.title

    def dehydrate_clarity_examples(self, tip_rating):
        example_ids = tip_rating.tip.example_set.values_list("id", flat=True)

        clarity_examples = (
            ExampleRating.objects.filter(example_id__in=example_ids)
            .values("example_id")
            .annotate(avg_clarity=Avg("clarity"))
            .values("example__headline", "avg_clarity")
        )

        result = []
        for clarity_example in clarity_examples:
            result.append(
                '"{}":{}'.format(
                    clarity_example["example__headline"],
                    clarity_example["avg_clarity"],
                )
            )

        return ", ".join(result)

    def dehydrate_rate_number(self, tip_rating):
        return tip_rating.stars
