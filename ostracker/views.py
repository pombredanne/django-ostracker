from collections import defaultdict
import datetime
from django.db.models import Sum
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from ostracker.models import Project, ProjectStatus

def _get_statuses(qs):
    c = {}
    statuses = qs.values('status_date').annotate(
        open=Sum('open_issues'), closed=Sum('closed_issues'),
        forks=Sum('forks'), watchers=Sum('watchers'),
        collaborators=Sum('collaborators')).order_by('status_date')
    open_issues = []
    closed_issues = []
    forks = []
    watchers = []
    collaborators = []
    for s in statuses:
        open_issues.append(s['open'])
        closed_issues.append(s['closed'])
        forks.append(s['forks'])
        watchers.append(s['watchers'])
        collaborators.append(s['collaborators'])

    c['issues'] = {'open': open_issues, 'closed': closed_issues}
    c['people'] = {'forks': forks, 'collaborators': collaborators,
                   'watchers': watchers, }
    return c

def cumulative_by_date(model, datefield):
    by_date = defaultdict(int)
    first_date = None
    for obj in model.objects.all().order_by(datefield):
        if not first_date:
            first_date = getattr(obj, datefield).replace(day=1)
        by_date[getattr(obj, datefield).strftime('%Y-%m')] += 1
    cumulative = [[None, 0]]
    d = first_date
    for i,k in enumerate(sorted(by_date.iterkeys())):
        cumulative.append((d, by_date[k] + cumulative[i][1]))
        d += datetime.timedelta(31)

    return cumulative[1:]

def _accumulate_statuses(proj):
    attrs = ['open_issues', 'closed_issues', 'forks', 'watchers',
             'collaborators', 'tagged_releases']
    for attr in attrs:
        setattr(proj, attr, [])

    for s in reversed(proj.statuses.order_by('-status_date')[:10]):
        for attr in attrs:
            getattr(proj, attr).append(getattr(s, attr, 0))

def index(request):
    by_lang = defaultdict(int)
    projects = list(Project.objects.all().order_by('name'))
    for proj in projects:
        _accumulate_statuses(proj)
        by_lang[proj.language] += 1

    #cumulative = cumulative_by_date(Project, 'created_date')

    context =  {'projects': projects, 'by_lang':dict(by_lang)}
    context.update(_get_statuses(ProjectStatus.objects.all()))

    return render_to_response('ostracker/index.html', context,
                             context_instance=RequestContext(request))


def project(request, name):
    project = get_object_or_404(Project, name=name)

    context = {'project': project}
    context.update(_get_statuses(project.statuses))

    return render_to_response('ostracker/project.html', context,
                             context_instance=RequestContext(request))
