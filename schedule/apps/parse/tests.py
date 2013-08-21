"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from .tasks import get_schedule
from .models import Faculty, Group
from django.db.models import Count

class ScheduleGetTest(TestCase):
    def test_basic(self):
        result = get_schedule.delay()
        self.assertEqual(Faculty.objects.count(), 11)
        self.assertEqual(Group.objects.count(), 1215)
