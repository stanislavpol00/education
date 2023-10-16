from tests.base_test import BaseTestCase
from tests.factories import EpisodeFactory, ExampleFactory


class TestEpisode(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.episode = EpisodeFactory.create()
        cls.example = ExampleFactory.create(episode=cls.episode)

    def test_writers(self):
        writers = self.episode.writers

        self.assertEqual(self.example.added_by, writers[0])

    def test_contributors(self):
        contributors = self.episode.contributors

        self.assertEqual(self.example.added_by, contributors[0])
