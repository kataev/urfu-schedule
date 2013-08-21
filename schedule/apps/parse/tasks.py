# -*- coding: utf-8 -*-


import requests
from celery import task
from lxml import html

from .models import Faculty, Group


def get_group_schedule(group):
    schedule = requests.get(group.url)
    tree = html.fromstring(schedule.text)
    print tree


def get_faculty_schedule(faculty):
    schedule = requests.get(faculty.url)
    tree = html.fromstring(schedule.text)
    for i, grade in enumerate(tree.xpath("//div[@class='groups-list']")):
        for group in grade.xpath('.//a[@href]'):
            pk = int(group.attrib['href'].split('/')[-2])
            defaults = {'course': i, 'name': group.text, 'faculty': faculty}
            group, created = Group.objects.get_or_create(pk=pk, defaults=defaults)
            get_group_schedule(group)


@task
def get_schedule():
    schedule = requests.get('http://urfu.ru/student/schedule/')
    tree = html.fromstring(schedule.text)

    for fac in tree.xpath('//div/table/tbody/tr/td/a'):
        # import ipdb;ipdb.set_trace()
        faculty, created = Faculty.objects.get_or_create(name=fac.text, pk=int(fac.attrib['href'].split('/')[-2]))
        get_faculty_schedule(faculty)
