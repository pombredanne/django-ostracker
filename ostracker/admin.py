from django.contrib import admin
from ostracker.models import Project, Contributor

class ProjectAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    list_display = ('name', 'status', 'created_date')
    list_filter = ('created_date','language', 'status')

admin.site.register(Project, ProjectAdmin)
