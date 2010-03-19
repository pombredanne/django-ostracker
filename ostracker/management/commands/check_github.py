import time
from django.core.management.base import BaseCommand
from ostracker.github import Github
from ostracker.models import Project

class Command(BaseCommand):
    help = 'Check github for latest information on a project or user'
    args = 'github-username [github-project]'

    def handle(self, username, *projects, **options):
        process_forks = False

        gh = Github()

        if projects:
            all_repos = [gh.repos.get(username, p) for p in projects]
            process_forks = True
        else:
            all_repos = gh.repos.for_user(username)

        for repo in all_repos:
            if process_forks or not repo.fork:

                # [:10] here gets the YYYY-MM-DD part of date string
                latest_commit = gh.commits.get_commits(username, repo.name)[0].committed_date[:10]

                p, created = Project.objects.get_or_create(name=repo.name,
                                                           username=username,
                                                           url=repo.url,
                              defaults={'description':repo.description,
                                        'latest_commit':latest_commit,
                                        'created_date':'2000-01-01',
                                        'host_site': 'github',
                                        'language':'?', })

                if created:
                    print 'Created Project for %s' % repo.name
                    results = gh.repos.search(repo.name)
                    for result in results:
                        if result.username == username:
                            p.created_date = result.created[:10]
                            p.language = result.language
                            p.save()
                            break

                time.sleep(3)
            else:
                print 'ignoring fork of %s' % repo.name
