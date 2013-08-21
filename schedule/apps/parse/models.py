# -*- coding: utf-8 -*-
from django.db import models


class Faculty(models.Model):
    name = models.CharField(u'Имя', max_length=300)


class Group(models.Model):
    course = models.IntegerField(u'Курс')
    name = models.CharField(u'Имя', max_length=300)


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
