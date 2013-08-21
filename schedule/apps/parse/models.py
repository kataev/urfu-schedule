# -*- coding: utf-8 -*-
from django.db import models


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

    class Meta(object):
        unique_together = ['faculty', 'name']

    @property
    def url(self):
        return 'http://urfu.ru/student/schedule/faculty/%d/group/%d/' % (self.faculty_id, self.pk)


class Professor(models.Model):
    name = models.CharField(u'Имя', max_length=300)


class Subject(models.Model):
    name = models.CharField(u'Имя', max_length=300)


class Class(models.Model):
    number = models.IntegerField(u'Номер пары')
    pred = models.ForeignKey(Subject, verbose_name=u'Предмет')
    type = models.IntegerField(u'Тип занятия')
    prepod = models.ForeignKey(Professor, verbose_name=u'Преподаватель')
    room = models.CharField(u'Аудитория', max_length=30)
