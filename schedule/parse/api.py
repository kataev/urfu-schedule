from tastypie import fields
from tastypie.resources import ModelResource
from .models import Faculty, Group


class FacultyResource(ModelResource):
    value = fields.CharField(attribute='name')


    class Meta:
        queryset = Faculty.objects.all()
        resource_name = 'faculty'
        fields = ('values', 'id')
        filtering = {
            'name': ['in', 'exact'],
        }

class GroupResource(ModelResource):
    faculty = fields.CharField(attribute='faculty')

    class Meta:
        queryset = Group.objects.all()
        resource_name = 'group'
        fields = ('name', 'faculty')
        filtering = {
            'name': ('exact', 'startswith','contains'),
        }
