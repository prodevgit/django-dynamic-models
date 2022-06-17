from django.db import models

class DataSource(models.Model):
    field_map = models.JSONField()
    file = models.FileField('datasource/')
    model = models.CharField(max_length=50,unique=True)