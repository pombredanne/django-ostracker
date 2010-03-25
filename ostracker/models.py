import datetime
from django.db import models

PROJECT_HOSTS = (
    ('none', 'none'),
    ('github', 'github'),
)

class Project(models.Model):
    name = models.CharField(max_length=100)
    username = models.CharField(max_length=100, blank=True)
    host_site = models.CharField(max_length=10)
    description = models.CharField(max_length=200)
    url = models.URLField()
    latest_commit = models.DateField()
    created_date = models.DateField(default=datetime.datetime.now)
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
        if self.username:
            return '/'.join((self.username, self.name))
        else:
            return self.name

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
