from os import environ
from django.test import TestCase
import requests


class GoogleCalendarApi(TestCase):
    def test_basic(self):
        with open('token', 'r') as file:
            access_token = file.read()
        self.assertTrue(access_token)

        authorization_header = {"Authorization": "OAuth %s" % access_token}
        r = requests.get("https://www.googleapis.com/oauth2/v2/userinfo",
                         headers=authorization_header)
        self.assertTrue(r.ok)

        r = requests.get("https://www.googleapis.com/calendar/v3/users/me/calendarList",
                   headers=authorization_header)
        self.assertTrue(r.ok)
        print r.content
