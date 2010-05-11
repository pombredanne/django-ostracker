import os, time, itertools, datetime
from ostracker.github import Github, GithubApiError
from git import Repo

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
        from ostracker.models import ProjectStatus, Issue
        GITHUB_REST = 5
        gh = Github()

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

    def update_repo(self, project):
        from ostracker.models import Commit, Contributor
        proj_dir = project.get_local_repo_dir()

        # checkout or update project
        if not os.path.exists(proj_dir):
            print 'cloning %s' % project
            os.system('git clone -q %s %s' % (project.get_remote_repo_url(),
                                              proj_dir))
        else:
            print 'updating %s' % project
            os.system('cd %s && git pull -q' % proj_dir)

        # process new commits
        repo = Repo(proj_dir)
        added = 0
        for c in repo.iter_commits():
            try:
                Commit.objects.get(id=c.sha)
            except Commit.DoesNotExist:
                added += 1
                stats = c.stats.total

                cdate = datetime.datetime.fromtimestamp(c.committed_date)

                author = Contributor.objects.lookup(c.author.name, c.author.email)

                Commit.objects.create(id=c.sha, project=project, author=author,
                                      message=c.message, time_committed=cdate,
                                      deletions=stats['deletions'],
                                      files=stats['files'],
                                      insertions=stats['insertions'],
                                      lines=stats['lines'])
        print 'added %s commits to %s' % (added, project)
