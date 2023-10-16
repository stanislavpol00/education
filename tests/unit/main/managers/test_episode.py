import constants
from main.models import Episode
from tests.base_test import BaseTestCase
from tests.factories import EpisodeFactory, ExampleFactory, TipFactory


class TestEpisode(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.episode1 = EpisodeFactory.create()
        cls.episode2 = EpisodeFactory.create()

        cls.tip1 = TipFactory.create(
            title="tip1",
            description="description1",
            environment_context={
                constants.Environment.SPACE_OPPORTUNITIES: "SPACE_OPPORTUNITIES_TEST1",
                constants.Environment.SPACE_EXPECTATIONS: "new1",
            },
            child_context={
                constants.ChildContext.CURRENT_MOTIVATOR: "CURRENT_MOTIVATOR_TEST1",
                constants.ChildContext.ANTICIPATED_BEHAVIOR: "old1",
            },
            sub_goal="sub_goal1",
        )

        cls.tip2 = TipFactory.create(
            title="tip2",
            description="description2",
            environment_context={
                constants.Environment.SPACE_OPPORTUNITIES: "SPACE_OPPORTUNITIES_TEST2",
                constants.Environment.SPACE_EXPECTATIONS: "new2",
            },
            child_context={
                constants.ChildContext.CURRENT_MOTIVATOR: "CURRENT_MOTIVATOR_TEST2",
                constants.ChildContext.ANTICIPATED_BEHAVIOR: "old2",
            },
            sub_goal="sub_goal2",
        )
        ExampleFactory.create(
            tip=cls.tip1, episode=cls.episode1, description="example1"
        )
        ExampleFactory.create(
            tip=cls.tip2, episode=cls.episode2, description="example2"
        )

    def test_search_without_search_text(self):
        episodes = Episode.objects.search(None, None, None)

        ids = [episode.id for episode in episodes]
        self.assertIn(self.episode1.id, ids)
        self.assertIn(self.episode2.id, ids)

    def test_search_title_without_search_fields(self):
        episodes = Episode.objects.search(None, "tip1", None)

        ids = [episode.id for episode in episodes]
        self.assertIn(self.episode1.id, ids)
        self.assertNotIn(self.episode2.id, ids)

        episodes = Episode.objects.search(None, "tip", None)

        ids = [episode.id for episode in episodes]
        self.assertIn(self.episode1.id, ids)
        self.assertIn(self.episode2.id, ids)

    def test_search_title_with_search_fields(self):
        episodes = Episode.objects.search(None, "tip1", ["title"])

        ids = [episode.id for episode in episodes]
        self.assertIn(self.episode1.id, ids)
        self.assertNotIn(self.episode2.id, ids)

        episodes = Episode.objects.search(None, "tip", ["title"])

        ids = [episode.id for episode in episodes]
        self.assertIn(self.episode1.id, ids)
        self.assertIn(self.episode2.id, ids)

    def test_search_description_without_search_fields(self):
        episodes = Episode.objects.search(None, "description1", None)

        ids = [episode.id for episode in episodes]
        self.assertIn(self.episode1.id, ids)
        self.assertNotIn(self.episode2.id, ids)

        episodes = Episode.objects.search(None, "description", None)

        ids = [episode.id for episode in episodes]
        self.assertIn(self.episode1.id, ids)
        self.assertIn(self.episode2.id, ids)

    def test_search_description_with_search_fields(self):
        episodes = Episode.objects.search(
            None, "description1", ["title", "description"]
        )

        ids = [episode.id for episode in episodes]
        self.assertIn(self.episode1.id, ids)
        self.assertNotIn(self.episode2.id, ids)

        episodes = Episode.objects.search(
            None, "description", ["title", "description"]
        )

        ids = [episode.id for episode in episodes]
        self.assertIn(self.episode1.id, ids)
        self.assertIn(self.episode2.id, ids)

    def test_search_sub_goal_without_search_fields(self):
        episodes = Episode.objects.search(None, "sub_goal1", None)

        ids = [episode.id for episode in episodes]
        self.assertIn(self.episode1.id, ids)
        self.assertNotIn(self.episode2.id, ids)

        episodes = Episode.objects.search(None, "sub_goal", None)

        ids = [episode.id for episode in episodes]
        self.assertIn(self.episode1.id, ids)
        self.assertIn(self.episode2.id, ids)

    def test_search_sub_goal_with_search_fields(self):
        episodes = Episode.objects.search(
            None, "sub_goal1", ["title", "description", "sub_goal"]
        )

        ids = [episode.id for episode in episodes]
        self.assertIn(self.episode1.id, ids)
        self.assertNotIn(self.episode2.id, ids)

        episodes = Episode.objects.search(
            None, "sub_goal", ["title", "description", "sub_goal"]
        )

        ids = [episode.id for episode in episodes]
        self.assertIn(self.episode1.id, ids)
        self.assertIn(self.episode2.id, ids)

    def test_search_environment_context_without_search_fields(self):
        episodes = Episode.objects.search(
            None, "SPACE_OPPORTUNITIES_TEST1", None
        )

        ids = [episode.id for episode in episodes]
        self.assertIn(self.episode1.id, ids)
        self.assertNotIn(self.episode2.id, ids)

        episodes = Episode.objects.search(
            None, "SPACE_OPPORTUNITIES_TEST", None
        )

        ids = [episode.id for episode in episodes]
        self.assertIn(self.episode1.id, ids)
        self.assertIn(self.episode2.id, ids)

    def test_search_environment_context_with_search_fields(self):
        episodes = Episode.objects.search(
            None,
            "SPACE_OPPORTUNITIES_TEST1",
            ["title", "environment_context", "child_context"],
        )

        ids = [episode.id for episode in episodes]
        self.assertIn(self.episode1.id, ids)
        self.assertNotIn(self.episode2.id, ids)

        episodes = Episode.objects.search(
            None,
            "SPACE_OPPORTUNITIES_TEST",
            ["title", "environment_context", "child_context"],
        )

        ids = [episode.id for episode in episodes]
        self.assertIn(self.episode1.id, ids)
        self.assertIn(self.episode2.id, ids)

    def test_search_child_context_without_search_fields(self):
        episodes = Episode.objects.search(
            None, "CURRENT_MOTIVATOR_TEST1", None
        )

        ids = [episode.id for episode in episodes]
        self.assertIn(self.episode1.id, ids)
        self.assertNotIn(self.episode2.id, ids)

        episodes = Episode.objects.search(None, "CURRENT_MOTIVATOR_TEST", None)

        ids = [episode.id for episode in episodes]
        self.assertIn(self.episode1.id, ids)
        self.assertIn(self.episode2.id, ids)

    def test_search_child_context_with_search_fields(self):
        episodes = Episode.objects.search(
            None,
            "CURRENT_MOTIVATOR_TEST1",
            ["title", "environment_context", "child_context"],
        )

        ids = [episode.id for episode in episodes]
        self.assertIn(self.episode1.id, ids)
        self.assertNotIn(self.episode2.id, ids)

        episodes = Episode.objects.search(
            None,
            "CURRENT_MOTIVATOR_TEST",
            ["title", "environment_context", "child_context"],
        )

        ids = [episode.id for episode in episodes]
        self.assertIn(self.episode1.id, ids)
        self.assertIn(self.episode2.id, ids)

    def test_search_example_description_without_search_fields(self):
        episodes = Episode.objects.search(None, "example1", None)

        ids = [episode.id for episode in episodes]
        self.assertIn(self.episode1.id, ids)
        self.assertNotIn(self.episode2.id, ids)

        episodes = Episode.objects.search(None, "example", None)

        ids = [episode.id for episode in episodes]
        self.assertIn(self.episode1.id, ids)
        self.assertIn(self.episode2.id, ids)

    def test_search_example_description_with_search_fields(self):
        episodes = Episode.objects.search(
            None, "example1", ["title", "example_description"]
        )

        ids = [episode.id for episode in episodes]
        self.assertIn(self.episode1.id, ids)
        self.assertNotIn(self.episode2.id, ids)

        episodes = Episode.objects.search(
            None, "example", ["title", "example_description"]
        )

        ids = [episode.id for episode in episodes]
        self.assertIn(self.episode1.id, ids)
        self.assertIn(self.episode2.id, ids)
