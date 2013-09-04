# -*- coding: utf-8 -*-
import requests
from celery import task
from lxml import html

from .models import *


@task
def get_group_schedule(group, limit=None):
    for semi in xrange(1, 3):
        schedule = requests.get(group.url + '%d/' % semi)
        tree = html.fromstring(schedule.text)
        for container in tree.xpath('//div[@class="tx-studentschedule-pi1"]/div[@id]'):
            semester = int(u'Весенний' not in container.xpath('.//div')[0].tail)
            week = int(container.attrib['id'].replace('week_', '')) % 2
            for day, (header, table) in enumerate(zip(container.xpath('.//h1'), container.xpath('.//table'))):
                for row in table.xpath('.//tr'):
                    row = row.xpath('.//td')
                    npair, time, subject_name, type, professor_name, room = row
                    if subject_name.text and professor_name.text:
                        c = Lesson(group=group, semester=semester, semi=semi, week=week, day=day)
                        c.professor, created = Professor.objects.get_or_create(name=professor_name.text)
                        c.subject, created = Subject.objects.get_or_create(name=subject_name.text)
                        type_c = dict((v, k) for k, v in Lesson.TYPE_CHOICES)
                        c.npair = int(npair.text)
                        c.type = type_c.get(type.text)
                        c.save()


@task
def get_faculty_schedule(faculty, limit=None):
    schedule = requests.get(faculty.url)
    tree = html.fromstring(schedule.text)
    for i, grade in enumerate(tree.xpath("//div[@class='groups-list']")[:limit]):
        for group in grade.xpath('.//a[@href]')[:limit]:
            pk = int(group.attrib['href'].split('/')[-2])
            defaults = {'course': i, 'name': group.text, 'faculty': faculty}
            group, created = Group.objects.get_or_create(pk=pk, defaults=defaults)
            get_group_schedule.task.delay(group, limit=limit)


@task
def get_schedule(limit=None):
    schedule = requests.get('http://urfu.ru/student/schedule/')
    tree = html.fromstring(schedule.text)

    for fac in tree.xpath('//div/table/tbody/tr/td/a')[:limit]:
        faculty, created = Faculty.objects.get_or_create(name=fac.text, pk=int(fac.attrib['href'].split('/')[-2]))
        get_faculty_schedule.task.delay(faculty, limit=limit)


@task
def test2():
    print sum([x for x in xrange(1000000)])


@task
def test():
    for x in range(100):
        test2.task.delay()
