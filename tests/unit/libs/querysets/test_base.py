from operator import and_

from django.db import models

from libs.querysets import BaseQuerySet
from tests.base_test import BaseTestCase


class TestBaseQuerySet(BaseTestCase):
    def test_join_q_objects_with_empty_q_objects(self):
        queryset = BaseQuerySet()

        # Test q_objects is None
        result = queryset._join_q_objects(None, and_)
        self.assertEqual(models.Q(), result)

        # Test q_objects is empty list
        result = queryset._join_q_objects([], and_)
        self.assertEqual(models.Q(), result)

    def test_join_or_q_objects(self):
        queryset = BaseQuerySet()
        q_objects = [models.Q() for _ in range(5)]
        expect_result = None
        for q_obj in q_objects:
            if not expect_result:
                expect_result = q_obj
            else:
                expect_result |= q_obj

        result = queryset._join_q_objects(None, and_)

        self.assertEqual(expect_result, result)

    def test_join_and_q_objects(self):
        queryset = BaseQuerySet()
        q_objects = [models.Q() for _ in range(5)]
        expect_result = None
        for q_obj in q_objects:
            if not expect_result:
                expect_result = q_obj
            else:
                expect_result &= q_obj

        result = queryset._join_q_objects(None, and_)

        self.assertEqual(expect_result, result)
