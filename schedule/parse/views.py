from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from .forms import GroupSelectForm


def index(request):
    if not request.user.is_anonymous():
        if request.user.classes.count():
            return aindex(request)
        else:
            return redirect('select')
    return render(request, 'index.html')


@login_required
def aindex(request):
    return render(request, 'aindex.html')


@login_required
def select(request):
    form = GroupSelectForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        request.user.classes.add(form.cleaned_data['group'])
        request.user.save()
        return redirect('index')
    return render(request, 'select.html', {'form': form})


@login_required
def fill(request):
    request.user.create_events.apply()
    return redirect('index')


@login_required
def remove(request):
    for e in request.user.events.all():
        e.delete_event.apply()
    return redirect('index')


def login(request):
    return redirect('socialauth_begin', backend='google-oauth2')


def error(request):
    return render(request, '500.html')
