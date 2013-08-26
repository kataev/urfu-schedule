from os import environ
from django.test import TestCase
import requests
import json


class GoogleCalendarApi(TestCase):
    def list(self, access_token):
        authorization_header = {"Authorization": "OAuth %s" % access_token}
        r = requests.get("https://www.googleapis.com/oauth2/v2/userinfo",
                         headers=authorization_header)
        self.assertTrue(r.ok)

        r = requests.get("https://www.googleapis.com/calendar/v3/users/me/calendarList",
                   headers=authorization_header)
        self.assertTrue(r.ok)
        return r.json()['items']

    def add(self, access_token, calendar_id):
        authorization_header = {"Authorization": "OAuth %s" % access_token, 'content-type': 'application/json'}
        r = requests.post("https://www.googleapis.com/calendar/v3/users/me/calendarList",
                         headers=authorization_header, data=json.dumps({'id':calendar_id}))
        self.assertTrue(r.ok)


    def delete(self, access_token, calendar_id):
        authorization_header = {"Authorization": "OAuth %s" % access_token, 'content-type': 'application/json'}
        r = requests.post("https://www.googleapis.com/calendar/v3/users/me/calendarList",
                         headers=authorization_header, data=json.dumps({'id':calendar_id}))
        self.assertTrue(r.ok)

    def test_add_delete_calendar(self):
        calendar_id = 'pr3dj0unj2fbtlisn4pi5boj2o@group.calendar.google.com'
        with open('token_2', 'r') as file:
            access_token = file.read()
        self.assertTrue(access_token)

        count = len(self.list(access_token))
        self.add(access_token, calendar_id)
        self.delete(access_token, calendar_id)
        self.assertEqual(count, len(self.list(access_token)))
