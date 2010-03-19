import datetime
from django.db import models

class Project(models.Model):
    name = models.CharField(max_length=100)
    username = models.CharField(max_length=100, blank=True)
    description = models.CharField(max_length=200)
    url = models.URLField()
    latest_commit = models.DateField()
    created_date = models.DateField()
    language = models.CharField(max_length=30)

    @property
    def latest_status(self):
        if not hasattr(self, '_latest_status'):
            try:
                status = self.statuses.order_by('-status_date')[0]
            except IndexError:
                status = None
            self._latest_status = status
        return self._latest_status

    def __unicode__(self):
        return '/'.join((self.username, self.name))

class ProjectStatus(models.Model):
    project = models.ForeignKey(Project, related_name='statuses')
    open_issues = models.IntegerField()
    closed_issues = models.IntegerField()
    forks = models.IntegerField()
    watchers = models.IntegerField()
    collaborators = models.IntegerField()
    tagged_releases = models.IntegerField()
    status_date = models.DateField(default=datetime.datetime.now)

    def __unicode__(self):
        return '%s status for %s' % (self.status_date, self.project)

class Contributor(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    # aliases field is used for dumb reconciliation of names
    aliases = models.TextField()

class Commit(models.Model):
    id = models.CharField(max_length=40, primary_key=True)
    project = models.ForeignKey(Project, related_name='commits')
    author = models.ForeignKey(Contributor, related_name='commits')
    message = models.TextField()
    time_committed = models.DateTimeField()
    deletions = models.IntegerField()
    files = models.IntegerField()
    insertions = models.IntegerField()
    lines = models.IntegerField()

    def __unicode__(self):
        return '%s: %s' % (self.id, self.message)
