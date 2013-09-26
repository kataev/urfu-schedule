# -*- coding: utf-8 -*-
import json
import requests
import datetime

from celery.contrib.methods import task

from django.db import models
from django.utils import timezone
from django.utils.dates import WEEKDAYS
from django.contrib.auth.models import AbstractUser

from .utils import get_date_point


class Faculty(models.Model):
    name = models.CharField(u'Имя', max_length=300, unique=True)

    def __unicode__(self):
        return self.name

    @property
    def url(self):
        return 'http://urfu.ru/student/schedule/schedule/list/group/institute/%d/' % self.pk


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
        return 'http://urfu.ru/student/schedule/schedule/list/lesson/institute/%d/sch_group/%d/' % (self.faculty_id, self.pk)

    @task
    def create_calendar(self):
        user = AUser.objects.get(pk=2)
        social_auth = user.social_auth.get(provider='google-oauth2')
        access_token = social_auth.extra_data['access_token']
        authorization_header = {"Authorization": "OAuth %s" % access_token, 'content-type': 'application/json'}
        r = requests.post('https://www.googleapis.com/calendar/v3/calendars',
                          headers=authorization_header,
                          data=json.dumps({'summary': self.name,
                                           'description': u'Расписание группы %s, факультет "%s"' % (
                                               self.name, self.faculty),
                                           'timeZone': 'Asia/Yekaterinburg',
                                           'location': u'Россия, Свердловская область, Екатеринбург',
                          }))
        if r.ok:
            calendar_id = r.json()['id']
            self.calendar_id = calendar_id
            self.save()
            return self

    @task
    def share_calendar(self):
        user = AUser.objects.get(pk=2)
        social_auth = user.social_auth.get(provider='google-oauth2')
        access_token = social_auth.extra_data['access_token']
        authorization_header = {"Authorization": "OAuth %s" % access_token, 'content-type': 'application/json'}
        r = requests.post('https://www.googleapis.com/calendar/v3/calendars/%s/acl' % self.calendar_id,
                          headers=authorization_header,
                          data=json.dumps({'role': 'reader', 'scope': {'type': 'default'}}))
        if r.ok:
            return r.ok

    @task
    def delete_calendar(self):
        user = AUser.objects.get(pk=2)
        social_auth = user.social_auth.get(provider='google-oauth2')
        access_token = social_auth.extra_data['access_token']
        authorization_header = {"Authorization": "OAuth %s" % access_token, 'content-type': 'application/json'}
        r = requests.delete('https://www.googleapis.com/calendar/v3/calendars/%s' % self.calendar_id,
                            headers=authorization_header)
        if r.ok:
            self.calendar_id = None
            self.save()
            return self

    @task
    def list_events(self):
        user = AUser.objects.get(pk=2)
        social_auth = user.social_auth.get(provider='google-oauth2')
        access_token = social_auth.extra_data['access_token']
        authorization_header = {"Authorization": "OAuth %s" % access_token, 'content-type': 'application/json'}
        r = requests.get('https://www.googleapis.com/calendar/v3/calendars/%s/events' % self.calendar_id,
                         headers=authorization_header)
        if r.ok:
            return self

    def create_events(self):
        today = datetime.date.today()
        monday = today - datetime.timedelta(days=today.weekday())
        for date in [monday + datetime.timedelta(days=x) for x in range(14)]:
            semester, semi, week, day = get_date_point(date)
            for l in self.lessons.filter(semester=semester, semi=semi, week=week % 2, day=day - 1):
                event = l.event(date)
                event.create_event()


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

    PAIR_TIME = (
        (1, (datetime.time(8, 30), datetime.time(10, 00))),
        (2, (datetime.time(10, 15), datetime.time(11, 45))),
        (3, (datetime.time(12, 00), datetime.time(13, 30))),
        (4, (datetime.time(14, 15), datetime.time(15, 45))),
        (5, (datetime.time(16, 00), datetime.time(17, 30))),
        (6, (datetime.time(17, 40), datetime.time(19, 05))),
        (7, (datetime.time(19, 15), datetime.time(20, 40))),
    )

    NPAIR_CHOICES = [(i, '%s - %s' % time) for i, time in PAIR_TIME]

    semester = models.SmallIntegerField(u'Семестр', choices=SEMESTER_CHOICES)
    semi = models.SmallIntegerField(u'Полусеместр', choices=SEMI_CHOICES)
    week = models.NullBooleanField(u'Неделя', choices=WEEK_CHOICES)
    day = models.SmallIntegerField(u'День недели', choices=DAY_OF_WEEK_CHOICES)

    group = models.ForeignKey(Group, related_name='lessons')

    npair = models.IntegerField(u'Номер пары', choices=NPAIR_CHOICES)
    subject = models.ForeignKey(Subject, verbose_name=u'Предмет', null=True)
    type = models.CharField(u'Тип занятия', max_length=300, null=True)
    professor = models.ForeignKey(Professor, verbose_name=u'Преподаватель', null=True)
    room = models.CharField(u'Аудитория', max_length=30, blank=True, null=True, default='')

    def __unicode__(self):
        return u'%s %d, %s' % (self.get_day_display(), self.npair, self.subject)

    @property
    def time(self):
        return dict(self.PAIR_TIME)[self.npair]

    @property
    def location(self):
        if not self.room:
            return ''
        addresses = {u'Р': u'ул. Мира, 32, Екатеринбург, Свердловская область'}
        address = addresses.get(self.room[0], '')
        return u'{}, {}'.format(self.room, address).strip()

    def event(self, user, date):
        e, created = Event.objects.get_or_create(user=user, lesson=self, date=date)
        return e

    @property
    def siblings(self):
        queryset = Lesson.objects.filter(semester=self.semester, semi=self.semi, week=self.week, day=self.day)
        if self.room:
            return queryset.filter(room=self.room, npair=self.npair)


class Event(models.Model):
    lesson = models.ForeignKey('Lesson', related_name='events')
    event_id = models.CharField(max_length=300, null=True)
    date = models.DateField(u'Дата занятия')
    user = models.ForeignKey('AUser', related_name='events')

    def __unicode__(self):
        return u'%s %s' % (self.lesson, self.date)

    @task
    def create_event(self):
        if self.event_id:
            return self.event_id
        social_auth = self.user.social_auth.get(provider='google-oauth2')
        access_token = social_auth.extra_data['access_token']
        authorization_header = {"Authorization": "OAuth %s" % access_token, 'content-type': 'application/json'}
        start, end = self.lesson.time
        start, end = datetime.datetime.combine(self.date, start), datetime.datetime.combine(self.date, end)
        current_tz = timezone.get_current_timezone()
        start = current_tz.localize(start)
        end = current_tz.localize(end)
        description = u""" Преподаваель: %s """ % (self.lesson.professor,)
        data = {
            'start': {'dateTime': start.isoformat()},
            'end': {'dateTime': end.isoformat()},
            'summary': unicode(self.lesson.subject),
            'description': description,
            'location': self.lesson.location,
        }
        r = requests.post("https://www.googleapis.com/calendar/v3/calendars/%s/events" % self.user.email,
                          headers=authorization_header, data=json.dumps(data))
        if r.ok:
            self.event_id = r.json()['id']
            self.save()
            return self
        else:
            print r.content


    @task
    def delete_event(self):
        if not self.event_id:
            return None
        user = self.user
        social_auth = user.social_auth.get(provider='google-oauth2')
        access_token = social_auth.extra_data['access_token']
        authorization_header = {"Authorization": "OAuth %s" % access_token, 'content-type': 'application/json'}
        url = "https://www.googleapis.com/calendar/v3/calendars/%s/events/" % self.user.email
        r = requests.delete(url + self.event_id, headers=authorization_header)

        if r.ok:
            self.event_id = None
            self.save()
            return self
        else:
            print r.content


class AUser(AbstractUser):
    classes = models.ManyToManyField('Group')

    @task
    def join_to_group(self, group):
        social_auth = self.social_auth.get(provider='google-oauth2')
        access_token = social_auth.extra_data['access_token']
        authorization_header = {"Authorization": "OAuth %s" % access_token, 'content-type': 'application/json'}
        r = requests.post("https://www.googleapis.com/calendar/v3/users/me/calendarList",
                      headers=authorization_header, data=json.dumps({'id': group.calendar_id}))
        if r.ok:
            return r

    def personal_schedule(self):
        semester, semi, week, day = get_date_point()
        day -= 1
        lessons = Lesson.objects.filter(group__in=self.classes.all()).filter(semester=semester, semi=semi,
                                                                             week=week % 2, day=day)
        return lessons

    def calendar_list(self):
        social_auth = self.social_auth.get(provider='google-oauth2')
        access_token = social_auth.extra_data['access_token']
        authorization_header = {"Authorization": "OAuth %s" % access_token}

        r = requests.get("https://www.googleapis.com/calendar/v3/users/me/calendarList",
                         headers=authorization_header)
        if r.ok:
            return r.json()['items']
        else:
            print r.content

    @task
    def create_events(self):
        today = datetime.date.today()
        monday = today - datetime.timedelta(days=today.weekday())
        for date in [monday + datetime.timedelta(days=x) for x in range(14)]:
            semester, semi, week, day = get_date_point(date)
            for g in self.classes.all():
                for l in g.lessons.filter(semester=semester, semi=semi, week=week % 2, day=day - 1):
                    event = l.event(self, date)
                    event.create_event.subtask().apply()
        return True
