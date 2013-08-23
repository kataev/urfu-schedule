"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
from os import environ
from django.test import TestCase
import requests


class SimpleTest(TestCase):
    def test_basic_addition(self):
        access_token = environ.get('ACCESS_TOKEN')

        self.assertTrue(access_token)

        authorization_header = {"Authorization": "OAuth %s" % access_token}
        r = requests.get("https://www.googleapis.com/oauth2/v2/userinfo",
                         headers=authorization_header)
        self.assertTrue(r.ok)

        r = requests.get("https://www.googleapis.com/calendar/v3/users/me/calendarList",
                   headers=authorization_header)
        self.assertTrue(r.ok)
        print r.content
