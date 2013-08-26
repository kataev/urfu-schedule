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

    def __unicode__(self):
        return u'%s %s' % (self.faculty, self.name)

    @property
    def url(self):
        return 'http://urfu.ru/student/schedule/faculty/%d/group/%d/' % (self.faculty_id, self.pk)


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

    semester = models.SmallIntegerField(u'Семестр', choices=SEMESTER_CHOICES)
    semi = models.SmallIntegerField(u'Полусеместр', choices=SEMI_CHOICES)
    week = models.NullBooleanField(u'Неделя', choices=WEEK_CHOICES)

    group = models.ForeignKey(Group)

    npair = models.IntegerField(u'Номер пары')
    subject = models.ForeignKey(Subject, verbose_name=u'Предмет')
    type = models.CharField(u'Тип занятия', max_length=300)
    professor = models.ForeignKey(Professor, verbose_name=u'Преподаватель')
    room = models.CharField(u'Аудитория', max_length=30)
