import datetime
from django.core.management.base import NoArgsCommand
from ostracker.models import Project

SAMPLE_RATE = 1

class Command(NoArgsCommand):
    help = 'Updates latest project information'

    def handle_noargs(self, **options):

        for p in Project.objects.exclude(host_site='none'):
            last_status = p.latest_status
            if not last_status or (datetime.date.today() - last_status.status_date) >= datetime.timedelta(SAMPLE_RATE):
                p.host_object.update_project(p)
