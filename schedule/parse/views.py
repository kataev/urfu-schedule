import json
from django.shortcuts import render, redirect
from django.http import HttpResponse

from .models import Group, Faculty
from .forms import GroupSelectForm


def index(request):
    form = GroupSelectForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        request.user.classes.add(form.cleaned_data.get('group'))
        return redirect('/')
    else:
        print form.errors
    groups = Group.objects.values_list('pk', 'name', 'faculty__name')
    return render(request, 'index.html', {'groups': groups})


def login(request):
    return render(request, 'login.html')


def groups(request):
    queryset = list(Group.objects.filter(name__contains=request.GET.get('q', '')).values_list('pk', 'name', 'faculty'))
    return HttpResponse(json.dumps(queryset), mimetype="application/json")
