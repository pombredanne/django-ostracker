import time, datetime
from django.core.management.base import NoArgsCommand
from ostracker.github import Github, GithubApiError
from ostracker.models import Project, ProjectStatus

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
                closed_issues = len([i for i in gh.issues.get_issues(p.host_username, p.name, False) if (i.user not in collaborators)])
                open_issues = len([i for i in gh.issues.get_issues(p.host_username, p.name, True) if (i.user not in collaborators)])
                num_releases = len(gh.repos.get_tags(p.host_username, p.name))

                ProjectStatus.objects.create(project = p,
                    open_issues = open_issues,
                    closed_issues = closed_issues,
                    forks = repo.forks,
                    watchers = repo.watchers,
                    collaborators = num_collaborators,
                    tagged_releases = num_releases)
                print 'getting latest status for %s' % p

            time.sleep(GITHUB_REST)
