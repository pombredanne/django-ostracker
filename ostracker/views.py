from collections import defaultdict
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

def _cumulative_by_date(model, datefield):
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
    projects = Project.objects.all()
    for proj in projects:
        by_lang[proj.language] += 1

    cumulative = _cumulative_by_date(Project, 'created_date')

    context =  {'cumulative':cumulative, 'by_lang':dict(by_lang)}
    context.update(_get_statuses(ProjectStatus.objects.all()))

    return render_to_response('ostracker/summary.html', context,
                             context_instance=RequestContext(request))

def activity(request):
    dates = list(ProjectStatus.objects.dates('status_date', 'day')[:5])
    old_date = dates[-5]
    new_date = dates[-1]
    old_statuses = ProjectStatus.objects.filter(status_date=old_date).select_related()
    new_statuses = ProjectStatus.objects.filter(status_date=new_date).select_related()

    info = defaultdict(dict)
    for s in new_statuses:
        proj = s.project.name
        info[proj]['activity'] = 0
        info[proj]['project'] = proj
        for k,v in s.__dict__.iteritems():
            if k[0] != '_' and k not in ('status_date', 'project_id', 'id'):
                info[proj]['new_' + k] = v
                info[proj]['activity'] += v

    for s in old_statuses:
        proj = s.project.name
        for k,v in s.__dict__.iteritems():
            if k[0] != '_' and k not in ('status_date', 'project_id', 'id'):
                info[proj]['new_' + k] -= v
                info[proj]['activity'] -= v

    info = [v for v in info.values() if v['activity']]
    info.sort(key=lambda x: x['activity'], reverse=True)
    totals = defaultdict(int)
    for i in info:
        for k,v in i.iteritems():
            if k != 'project':
                totals[k] += v

    return render_to_response('ostracker/activity.html', {'activity': info, 'totals': totals},
                              context_instance=RequestContext(request))

def projects(request):
    projects = Project.objects.all().order_by('name')
    return render_to_response('ostracker/projects.html', {'projects':projects},
                             context_instance=RequestContext(request))

def project(request, name):
    project = get_object_or_404(Project, name=name)

    context = {'project': project}
    context.update(_get_statuses(project.statuses))

    return render_to_response('ostracker/project.html', context,
                             context_instance=RequestContext(request))
