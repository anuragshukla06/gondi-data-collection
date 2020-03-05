from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from . import models
# Register your models here.

class userResource(resources.ModelResource):
    class Meta:
        model = models.user

class translationResource(resources.ModelResource):
    class Meta:
        model = models.translation

class userAdmin(ImportExportModelAdmin):
    resource_class = userResource

class translationAdmin(ImportExportModelAdmin):
    resource_class = translationResource

    
admin.site.register(models.user, userAdmin)
admin.site.register(models.translation, translationAdmin)