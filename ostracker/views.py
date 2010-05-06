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
    c['open_issues'] = []
    c['closed_issues'] = []
    c['forks'] = []
    c['watchers'] = []
    c['collaborators'] = []
    c['status_dates'] = []
    for s in statuses:
        c['status_dates'].append(s['status_date'].strftime('%m/%d'))
        c['open_issues'].append(s['open'])
        c['closed_issues'].append(s['closed'])
        c['forks'].append(s['forks'])
        c['watchers'].append(s['watchers'])
        c['collaborators'].append(s['collaborators'])
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

def summary(request):
    by_lang = defaultdict(int)
    projects = Project.objects.all().order_by('name')
    for proj in projects:
        by_lang[proj.language] += 1

    cumulative = cumulative_by_date(Project, 'created_date')

    context =  {'projects': projects, 'cumulative':cumulative,
                'by_lang':dict(by_lang)}
    context.update(_get_statuses(ProjectStatus.objects.all()))

    return render_to_response('ostracker/summary.html', context,
                             context_instance=RequestContext(request))

def _accumulate_statuses(proj):
    attrs = ['open_issues', 'closed_issues', 'forks', 'watchers',
             'collaborators', 'tagged_releases']
    for attr in attrs:
        setattr(proj, attr, [])

    for s in reversed(proj.statuses.order_by('-status_date')[:10]):
        for attr in attrs:
            getattr(proj, attr).append(getattr(s, attr, 0))

    for attr in attrs:
        attr_data = getattr(proj, attr)
        setattr(proj, attr+'_max', max(attr_data)+0.5)
        setattr(proj, attr+'_delta', attr_data[-1]-attr_data[-2])

def index(request):
    month_ago = datetime.date.today()-datetime.timedelta(30)
    year_ago = datetime.date.today()-datetime.timedelta(365)

    active = 0
    proj_month = 0
    proj_year = 0
    projects = list(Project.objects.all().order_by('name'))
    for proj in projects:
        if proj.created_date > month_ago:
            proj_month += 1
        if proj.created_date > year_ago:
            proj_year += 1
        if proj.latest_commit > month_ago:
            active += 1

        # historical data
        _accumulate_statuses(proj)

    projects_total = len(projects)

    context =  {'projects': projects,
                'projects_total': projects_total,
                'projects_month': proj_month,
                'projects_year': proj_year,
               }

    return render_to_response('ostracker/index.html', context,
                             context_instance=RequestContext(request))


def project(request, name):
    project = get_object_or_404(Project, name=name)

    context = {'project': project}
    context.update(_get_statuses(project.statuses))

    return render_to_response('ostracker/project.html', context,
                             context_instance=RequestContext(request))
