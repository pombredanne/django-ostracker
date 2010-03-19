import os
from django.conf import settings
from django.core.management.base import NoArgsCommand
# requires pythongit
from git import Repo
from ostracker.models import Project, Commit, Contributor

class Command(NoArgsCommand):
    help = 'Update all Projects'
    requires_model_validation = False

    def handle_noargs(self, **options):
        projects = Project.objects.all()
        for proj in projects:
            proj_dir = os.path.join(settings.BASE_PROJECT_DIR, proj.name)

            # checkout or update project
            if not os.path.exists(proj_dir):
                print 'cloning %s' % proj.name
                os.system('git clone -q -n git://github.com/%s/%s.git %s' % (
                    proj.username, proj.name, proj_dir))
            else:
                print 'updating %s' % proj.name
                os.system('cd %s && git pull -q' % proj_dir)

            # process new commits
            repo = Repo(proj_dir)
            commits = repo.commits_since()
            added = 0
            for c in commits:
                try:
                    Commit.objects.get(id=c.id)
                except Commit.DoesNotExist:
                    added += 1
                    stats = c.stats.total

                    cdate = c.committed_date
                    time = '%s-%02d-%02d %02d:%02d:%02d' % (cdate.tm_year,
                            cdate.tm_mon, cdate.tm_mday, cdate.tm_hour,
                            cdate.tm_min, cdate.tm_sec)

                    try:
                        alias = '%s <%s> ' % (c.author.name, c.author.email)
                        author = Contributor.objects.get(aliases__icontains=alias)
                    except Contributor.DoesNotExist:
                        author = Contributor.objects.create(name=c.author.name,
                                                       email=c.author.email,
                                                       aliases=alias)

                    Commit.objects.create(id=c.id, project=proj, author=author,
                                          message=c.message, time_committed=time,
                                          deletions=stats['deletions'],
                                          files=stats['files'],
                                          insertions=stats['insertions'],
                                          lines=stats['lines'])
            print 'added %s commits to %s' % (added, proj.name)
