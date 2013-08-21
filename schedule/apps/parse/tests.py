# -*- coding: utf-8 -*-
from django.test import TestCase

from .tasks import get_schedule
from .models import Faculty, Group, Lesson


class ScheduleGetTest(TestCase):
    def test_basic(self):
        result = get_schedule.delay(limit=2)
        self.assertTrue(Faculty.objects.count())
        self.assertTrue(Group.objects.count())
        print Lesson.object.count()
