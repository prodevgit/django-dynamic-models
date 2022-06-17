from django.apps import AppConfig
from django.db import models as django_models
from django.contrib import admin as django_admin

class DdmConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ddm'

    def ready(self):
        
        from .models import DataSource
        datasources = DataSource.objects.all()
        for datasource in datasources:
            attrs = {'__module__':'ddm.models'}
            attrs.update({
                'id': django_models.AutoField(primary_key=True)
            })
            field_map = datasource.field_map

            for field,field_real in list(field_map.items()):
                if field_real[1] == 'INT':            
                    attrs.update({
                        field: django_models.IntegerField(null=True,blank=True)
                    })

                elif field_real[1] == 'VARCHAR':
                    attrs.update({
                        field: django_models.CharField(max_length=1000,null=True,blank=True)
                    })

                elif field_real[1] == 'FLOAT':
                    attrs.update({
                        field: django_models.FloatField(null=True,blank=True)
                    })

                else:
                    attrs.update({
                        field: django_models.CharField(max_length=1000,null=True,blank=True)
                    })
            MODEL = type(datasource.model, (django_models.Model,), attrs)
            django_admin.site.register(MODEL)
