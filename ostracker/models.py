import datetime
import os
from django.conf import settings
from django.db import models

PROJECT_STATUSES = (
    ('private', 'Private'),
    ('public', 'Public'),
    ('featured', 'Featured'),
)

PROJECT_HOSTS = (
    ('none', 'none'),
    ('github', 'github'),
)

class GithubHost(object):
    def get_remote_repo_url(project):
        return 'git://github.com/%(host_username)s/%(slug)s.git' % project.__dict__

    def get_host_url(project):
        return 'http://github.com/%(host_username)s/%(slug)s/' % project.__dict__

    def get_issue_url(issue):
        url = 'http://github.com/%(host_username)s/%(project)s/issues/issue/%(tracker_id)s'

        return url % {'host_username':issue.project.host_username,
                      'project': issue.project.slug,
                      'tracker_id': issue.tracker_id}

class ProjectManager(models.Manager):
    def all_public(self):
        return self.get_query_set().exclude(status='private')
    def featured(self):
        return self.get_query_set().filter(status='featured')

class Project(models.Model):
    objects = ProjectManager()

    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=50, unique=True)
    status = models.CharField(max_length=10, default='public',
                              choices=PROJECT_STATUSES)

    description = models.TextField()
    language = models.CharField(max_length=30)

    host_site = models.CharField(max_length=10, choices=PROJECT_HOSTS)
    host_username = models.CharField(max_length=100, blank=True)

    latest_commit = models.DateField()
    created_date = models.DateField(default=datetime.datetime.now)

    class Meta:
        ordering = ['-created_date']

    def __unicode__(self):
        if self.host_username:
            return '/'.join((self.host_username, self.name))
        else:
            return self.name

    @property
    def latest_status(self):
        if not hasattr(self, '_latest_status'):
            try:
                status = self.statuses.order_by('-status_date')[0]
            except IndexError:
                status = None
            self._latest_status = status
        return self._latest_status

    @property
    def host_object(self):
        return GithubHost()

    def get_remote_repo_url(self):
        self.host_object.get_remote_repo_url(self)

    def get_host_url(self):
        self.host_object.get_host_url(self)

    def get_local_repo_dir(self):
        return os.path.join(settings.OSTRACKER_PROJECT_DIR, self.host_username
                            or '', self.slug)


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

class ContributorManager(models.Manager):

    def lookup(self, name, email):
        alias = '%s <%s>' % (name, email)
        try:
            c = Contributor.objects.get(aliases__icontains=alias)
        except Contributor.DoesNotExist:
            c = Contributor.objects.create(name=name, email=email,
                                           aliases=alias)
        return c

class Contributor(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    # aliases field is used for dumb reconciliation of names
    aliases = models.TextField()

    objects = ContributorManager()

    def __unicode__(self):
        return '%s <%s>' % (self.name, self.email)

    def merge(self, *children):
        aliases = ['%s <%s>' % (child.name, child.email) for child in children]
        self.aliases += ' ' + ' '.join(aliases)
        self.save()

        # loop over children replacing all reverse relationships
        for child in children:
            for ro in child._meta.get_all_related_objects():

                # get reverse queryset
                related_objects = getattr(child, ro.get_accessor_name()).all()

                # for each item in reverse queryset replace var_name with self
                for obj in related_objects:
                    #print '%s.%s = %s' % (obj, ro.var_name, self)
                    setattr(obj, ro.var_name, self)

            for m2m in child._meta.get_all_related_many_to_many_objects():
                all_related = getattr(child, m2m.get_accessor_name()).all()

                for obj in all_related:
                    #print '%s.%s.add(%s)' % (obj, m2m.field.name, self)
                    getattr(obj, m2m.field.name).add(self)

            child.delete()

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

class Issue(models.Model):
    project = models.ForeignKey(Project, related_name='issues')
    tracker_id = models.PositiveIntegerField()
    title = models.CharField(max_length=200)
    description = models.TextField()
    reported_by = models.CharField(max_length=100)
    state = models.CharField(max_length=20)
    votes = models.PositiveIntegerField()
    created_date = models.DateField()

    class Meta:
        ordering = ['state', 'created_date']

    def __unicode__(self):
        return self.title

    def get_host_url(self):
        self.project.host_object.get_issue_url(self)
