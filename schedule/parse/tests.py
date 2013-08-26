# -*- coding: utf-8 -*-
import requests
import datetime
import json

from django.test import TestCase

from .tasks import get_schedule
from .models import Faculty, Group


class ScheduleGetTest(TestCase):
    def test_basic(self):
        result = get_schedule.delay(limit=2)
        self.assertTrue(Faculty.objects.count())
        self.assertTrue(Group.objects.count())


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
                          headers=authorization_header, data=json.dumps({'id': calendar_id}))
        self.assertTrue(r.ok)


    def delete(self, access_token, calendar_id):
        authorization_header = {"Authorization": "OAuth %s" % access_token, 'content-type': 'application/json'}
        r = requests.post("https://www.googleapis.com/calendar/v3/users/me/calendarList",
                          headers=authorization_header, data=json.dumps({'id': calendar_id}))
        self.assertTrue(r.ok)

    def test_add_delete_calendar(self):
        calendar_id = 'pr3dj0unj2fbtlisn4pi5boj2o@group.calendar.google.com'
        with open('token_2', 'r') as f:
            access_token = f.read()
        self.assertTrue(access_token)

        count = len(self.list(access_token))
        self.add(access_token, calendar_id)
        self.delete(access_token, calendar_id)
        self.assertEqual(count, len(self.list(access_token)))


    def test_add_event(self):
        calendar_id = 'pr3dj0unj2fbtlisn4pi5boj2o@group.calendar.google.com'
        with open('token_1', 'r') as f:
            access_token = f.read()
        authorization_header = {"Authorization": "OAuth %s" % access_token, 'content-type': 'application/json'}

        data = {
            'start': {'dateTime': datetime.datetime.utcnow().replace(hour=10).isoformat(), 'timeZone': 'Europe/Zurich'},
            'end': {'dateTime': datetime.datetime.utcnow().isoformat(), 'timeZone': 'Europe/Zurich'},
            'summary': 'Created from api',
            'description': 'Created from api description'
        }

        print data
        r = requests.post("https://www.googleapis.com/calendar/v3/calendars/%s/events" % calendar_id,
                          headers=authorization_header, data=json.dumps(data))
        print r.content
        self.assertTrue(r.ok)
        print r.text

    def test_get_event_list(self):
        calendar_id = 'pr3dj0unj2fbtlisn4pi5boj2o@group.calendar.google.com'
        with open('token_1', 'r') as f:
            access_token = f.read()
        authorization_header = {"Authorization": "OAuth %s" % access_token, 'content-type': 'application/json'}

        r = requests.get("https://www.googleapis.com/calendar/v3/calendars/%s/events" % calendar_id,
                         headers=authorization_header)
        self.assertTrue(r.ok)
        print r.text
