import time, datetime, itertools
from django.core.management.base import NoArgsCommand
from ostracker.github import Github, GithubApiError
from ostracker.models import Project, ProjectStatus, Issue

SAMPLE_RATE = 7
GITHUB_REST = 5

class Command(NoArgsCommand):
    help = 'Updates latest project information from github'

    def handle_noargs(self, **options):
        gh = Github()

        for p in Project.objects.filter(host_site='github'):
            last_status = p.latest_status
            if not last_status or (datetime.date.today() - last_status.status_date) >= datetime.timedelta(SAMPLE_RATE):

                try:
                    repo = gh.repos.get(p.host_username, p.name)
                except GithubApiError:
                    print 'error getting repository %s' % p
                    continue

                # add a ProjectStatus for this project
                collaborators = gh.repos.get_collaborators(p.host_username, p.name)
                num_collaborators = len(collaborators) - 1
                num_releases = len(gh.repos.get_tags(p.host_username, p.name))

                closed_issues = gh.issues.get_issues(p.host_username, p.name, False)
                open_issues = gh.issues.get_issues(p.host_username, p.name, True)

                # go through all issues at once
                for i in itertools.chain(open_issues, closed_issues):
                    issue, created = Issue.objects.get_or_create(project=p,
                             tracker_id=i.number, defaults={
                                 'title': i.title,
                                 'description': i.body,
                                 'reported_by': i.user,
                                 'state': i.state,
                                 'votes': i.votes,
                                 'created_date': i.created_at[:10].replace('/','-')})
                    if not created and i.state != issue.state:
                        issue.state = i.state
                        issue.save()


                # could be done inside the loop, but these aren't long to loop back over
                num_closed_issues = len([i for i in closed_issues if (i.user not in collaborators)])
                num_open_issues = len([i for i in open_issues if (i.user not in collaborators)])

                ProjectStatus.objects.create(project = p,
                    open_issues = num_open_issues,
                    closed_issues = num_closed_issues,
                    forks = repo.forks,
                    watchers = repo.watchers,
                    collaborators = num_collaborators,
                    tagged_releases = num_releases)
                print 'getting latest status for %s' % p

            time.sleep(GITHUB_REST)
