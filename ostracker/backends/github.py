import time, itertools
from ostracker.github import Github, GithubApiError

class GithubHost(object):
    def get_remote_repo_url(self, project):
        return 'git://github.com/%(host_username)s/%(slug)s.git' % project.__dict__

    def get_host_url(self, project):
        return 'http://github.com/%(host_username)s/%(slug)s/' % project.__dict__

    def get_issue_url(self, issue):
        url = 'http://github.com/%(host_username)s/%(project)s/issues/issue/%(tracker_id)s'

        return url % {'host_username':issue.project.host_username,
                      'project': issue.project.slug,
                      'tracker_id': issue.tracker_id}

    def update_project(self, project):
        GITHUB_REST = 5
        gh = Github()
        from ostracker.models import ProjectStatus, Issue

        try:
            repo = gh.repos.get(project.host_username, project.slug)
        except GithubApiError:
            print 'error getting repository %s' % project
            return

        # add a ProjectStatus for this project
        collaborators = gh.repos.get_collaborators(project.host_username, project.slug)
        num_collaborators = len(collaborators) - 1
        num_releases = len(gh.repos.get_tags(project.host_username, project.slug))

        closed_issues = gh.issues.get_issues(project.host_username, project.slug, False)
        open_issues = gh.issues.get_issues(project.host_username, project.slug, True)

        # go through all issues at once
        for i in itertools.chain(open_issues, closed_issues):
            issue, created = Issue.objects.get_or_create(project=project,
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

        ProjectStatus.objects.create(project=project,
            open_issues = num_open_issues,
            closed_issues = num_closed_issues,
            forks = repo.forks,
            watchers = repo.watchers,
            collaborators = num_collaborators,
            tagged_releases = num_releases)
        print 'getting latest status for %s' % project

        time.sleep(GITHUB_REST)

