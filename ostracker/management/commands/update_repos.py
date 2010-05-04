import os
import datetime
from django.conf import settings
from django.core.management.base import NoArgsCommand
from git import Repo
from ostracker.models import Project, Commit, Contributor

class Command(NoArgsCommand):
    help = 'Update all Projects'

    def handle_noargs(self, **options):
        projects = Project.objects.all()
        for proj in projects:
            proj_dir = proj.get_local_repo_dir()

            # checkout or update project
            if not os.path.exists(proj_dir):
                print 'cloning %s' % proj
                os.system('git clone -q %s %s' % (proj.get_remote_repo_url(),
                                                  proj_dir))
            else:
                print 'updating %s' % proj
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

                    Commit.objects.create(id=c.sha, project=proj, author=author,
                                          message=c.message, time_committed=cdate,
                                          deletions=stats['deletions'],
                                          files=stats['files'],
                                          insertions=stats['insertions'],
                                          lines=stats['lines'])
            print 'added %s commits to %s' % (added, proj)
