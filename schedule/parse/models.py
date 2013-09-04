# -*- coding: utf-8 -*-
import json
import requests
import datetime

from celery.contrib.methods import task

from django.db import models
from django.utils.dates import WEEKDAYS
from django.utils.timezone import utc
from django.contrib.auth.models import AbstractUser


class Faculty(models.Model):
    name = models.CharField(u'Имя', max_length=300, unique=True)

    def __unicode__(self):
        return self.name

    @property
    def url(self):
        return 'http://urfu.ru/student/schedule/faculty/%d/' % self.pk


class Group(models.Model):
    faculty = models.ForeignKey(Faculty, verbose_name=u'Факультет')
    name = models.CharField(u'Имя', max_length=300)
    course = models.IntegerField(u'Курс')

    calendar_id = models.CharField(u'Айди календаря', max_length=300, null=True)

    class Meta(object):
        unique_together = ['faculty', 'name']

    def __unicode__(self):
        return u'%s %s' % (self.faculty, self.name)

    @property
    def url(self):
        return 'http://urfu.ru/student/schedule/faculty/%d/group/%d/' % (self.faculty_id, self.pk)

    @task
    def create_calendar(self):
        user = AUser.objects.get(pk=2)
        social_auth = user.social_auth.get(provider='google-oauth2')
        access_token = social_auth.extra_data['access_token']
        authorization_header = {"Authorization": "OAuth %s" % access_token, 'content-type': 'application/json'}
        r = requests.post('https://www.googleapis.com/calendar/v3/calendars',
                          headers=authorization_header,
                          data=json.dumps({'summary': self.name, 'timeZone': 'Asia/Yekaterinburg'}))
        print r.content
        if r.ok:
            calendar_id = r.json()['id']
            self.calendar_id = calendar_id
            self.save()

    @task
    def share_calendar(self):
        user = AUser.objects.get(pk=2)
        social_auth = user.social_auth.get(provider='google-oauth2')
        access_token = social_auth.extra_data['access_token']
        authorization_header = {"Authorization": "OAuth %s" % access_token, 'content-type': 'application/json'}
        r = requests.post('https://www.googleapis.com/calendar/v3/calendars/%s/acl' % self.calendar_id,
                          headers=authorization_header,
                          data=json.dumps({'role': 'reader', 'scope': {'type': 'default'}}))
        print r.content

    @task
    def delete_calendar(self):
        user = AUser.objects.get(pk=2)
        social_auth = user.social_auth.get(provider='google-oauth2')
        access_token = social_auth.extra_data['access_token']
        authorization_header = {"Authorization": "OAuth %s" % access_token, 'content-type': 'application/json'}
        r = requests.delete('https://www.googleapis.com/calendar/v3/calendars/%s' % self.calendar_id,
                            headers=authorization_header)

        print r.content
        if r.ok:
            self.calendar_id = None
            self.save()


class Professor(models.Model):
    name = models.CharField(u'Имя', max_length=300)

    def __unicode__(self):
        return self.name


class Subject(models.Model):
    name = models.CharField(u'Имя', max_length=300)

    def __unicode__(self):
        return self.name


class Lesson(models.Model):
    SEMESTER_CHOICES = ((1, u'Осенний'), (0, u'Весенний'))
    SEMI_CHOICES = ((1, u'Первый'), (2, u'Второй'))
    WEEK_CHOICES = ((None, u''), (True, u'Нечетная'), (False, u'Четная'))
    TYPE_CHOICES = ((0, u'Лекция'), (1, u'Практика'), (2, u'Лабораторная работа'))
    DAY_OF_WEEK_CHOICES = WEEKDAYS.items()

    semester = models.SmallIntegerField(u'Семестр', choices=SEMESTER_CHOICES)
    semi = models.SmallIntegerField(u'Полусеместр', choices=SEMI_CHOICES)
    week = models.NullBooleanField(u'Неделя', choices=WEEK_CHOICES)
    day = models.SmallIntegerField(u'День недели', choices=DAY_OF_WEEK_CHOICES)

    group = models.ForeignKey(Group, related_name='lessons')

    npair = models.IntegerField(u'Номер пары')
    subject = models.ForeignKey(Subject, verbose_name=u'Предмет')
    type = models.CharField(u'Тип занятия', max_length=300)
    professor = models.ForeignKey(Professor, verbose_name=u'Преподаватель')
    room = models.CharField(u'Аудитория', max_length=30)

    def __unicode__(self):
        return u'%s %d, %s' % (self.get_day_display(), self.npair, self.subject)


class Event(models.Model):
    lesson = models.ForeignKey('Lesson', related_name='events')
    event_id = models.CharField(max_length=300)
    week = models.IntegerField(u'Номер недели')

    @task
    def create_event(self):
        user = AUser.objects.get(pk=2)
        social_auth = user.social_auth.get(provider='google-oauth2')
        access_token = social_auth.extra_data['access_token']
        authorization_header = {"Authorization": "OAuth %s" % access_token, 'content-type': 'application/json'}

        data = {
            'start': {'dateTime': datetime.datetime.utcnow().replace(hour=10).isoformat(), 'timeZone': 'Europe/Zurich'},
            'end': {'dateTime': datetime.datetime.utcnow().isoformat(), 'timeZone': 'Europe/Zurich'},
            'summary': unicode(self.lesson),
            'description': 'Created from api description',
            'location': self.lesson.room,
        }

        print data
        r = requests.post("https://www.googleapis.com/calendar/v3/calendars/%s/events" % self.lesson.group.calendar_id,
                          headers=authorization_header, data=json.dumps(data))
        print r.content
        if r.ok:
            self.event_id = r['id']
            self.save()


class AUser(AbstractUser):
    classes = models.ManyToManyField('Group')

    @task
    def join_to_group(self, group):
        social_auth = self.social_auth.get(provider='google-oauth2')
        access_token = social_auth.extra_data['access_token']
        authorization_header = {"Authorization": "OAuth %s" % access_token, 'content-type': 'application/json'}
        r = requests.post("https://www.googleapis.com/calendar/v3/users/me/calendarList",
                          headers=authorization_header, data=json.dumps({'id': group.calendar_id}))
        print r.content

    def get_date_point(self, date=None):
        if date is None:
            date = datetime.datetime.utcnow().replace(tzinfo=utc)
        if 6 <= date.month <= 12:
            semester = 1
        else:
            semester = 2
        semi = 1
        week, day = date.isocalendar()[1:]
        return semester, semi, week, day

    def personal_schedule(self):
        semester, semi, week, day = self.get_date_point()
        day -= 1
        lessons = Lesson.objects.filter(group__in=self.classes.all()).filter(semester=semester, semi=semi, week=week % 2, day=day)
        return lessons
