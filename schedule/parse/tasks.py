# -*- coding: utf-8 -*-
import requests
from celery import task
from lxml import html

from .models import *


@task
def get_group_schedule(group, limit=None):
    is_ok = False
    for semi in xrange(1, 3):
        for week, wname in (('even', 'odd'), (0, 1)):
            schedule = requests.get(group.url + '/week/%s/semi_semester/%d/' % (wname, semi))
            print 'semi', semi, schedule.ok
            container = html.fromstring(schedule.text)
            print 'cont', container
            semester = int(u'Весенний' not in container.xpath('.//div')[0].tail)
            for day, (header, table) in enumerate(
                    zip(container.xpath('.//h1'), container.xpath('.//table[@class="contenttable"]'))):
                for row in table.xpath('.//tr'):
                    row = row.xpath('.//td')
                    if not len(row) == 6:
                        continue
                    npair, time, subject_name, l_type, professor_name, room = row

                    if subject_name.text and professor_name.text:
                        # import ipdb; ipdb.set_trace()
                        print row
                        subject, created = Subject.objects.get_or_create(name=subject_name.text)
                        c, created = Lesson.objects.get_or_create(group=group, semester=semester, semi=semi, week=week,
                                                                  day=day, npair=int(npair.text))
                        c.subject = subject
                        c.professor, created = Professor.objects.get_or_create(name=professor_name.text)
                        type_c = dict((v, k) for k, v in Lesson.TYPE_CHOICES)
                        c.type = type_c.get(l_type.text)
                        c.room = room.text
                        c.save()
    return is_ok


@task
def get_faculty_schedule(faculty, limit=None):
    schedule = requests.get(faculty.url)
    tree = html.fromstring(schedule.text)
    groups = []
    print 'get faculty', faculty
    for i, grade in enumerate(tree.xpath("//div[@class='groups']")[:limit]):
        print 'grade', grade
        for group in grade.xpath('.//a[@href]')[:limit]:
            print 'group', group
            pk = int(group.attrib['href'].split('/')[-2])
            defaults = {'course': i, 'name': group.text, 'faculty': faculty}
            group, created = Group.objects.get_or_create(pk=pk, defaults=defaults)
            get_group_schedule.task.subtask().delay(group, limit=limit)
            groups.append(group)
    return groups


@task
def get_schedule(limit=None):
    schedule = requests.get('http://urfu.ru/student/schedule/')
    tree = html.fromstring(schedule.text)
    department = []
    for fac in tree.xpath('//div/table/tbody/tr/td/a')[:limit]:
        print 'fac', fac
        faculty, created = Faculty.objects.get_or_create(name=fac.text, pk=int(fac.attrib['href'].split('/')[-2]))
        get_faculty_schedule.task.subtask().delay(faculty, limit=limit)
        department.append(faculty)
    return department
