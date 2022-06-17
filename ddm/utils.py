import io
import os
from numpy import dtype
from django.db import models as django_models
from django.apps import apps
from django.contrib import admin as django_admin
from django.core.files.base import  File
from django.db import connection

from ddm.models import DataSource

def generate_model(model_name,df,datasource_path):

    attrs = {'__module__':'ddm.models'}

    table_query =""
    field_map = {}

    attrs.update({
                'id': django_models.AutoField(primary_key=True)
            })
    table_query = 'id INT NOT NULL AUTO_INCREMENT'

    for types in df.dtypes.iteritems():
        
        field = process_field(types[0])[:50]
                
        if types[1] == dtype('int64'):            
            attrs.update({
                field: django_models.IntegerField(null=True,blank=True)
            })
            table_query = f'{table_query},{field} INT NULL'
            field_map[field]=[types[0],'INT']

        elif types[1] == dtype('O'):
            attrs.update({
                field: django_models.CharField(max_length=1000,null=True,blank=True)
            })
            table_query = f'{table_query},{field} varchar(1000) NULL'
            field_map[field]=[types[0],'VARCHAR']

        elif types[1] == dtype('float64'):
            attrs.update({
                field: django_models.FloatField(null=True,blank=True)
            })
            table_query = f'{table_query},{field} FLOAT NULL'
            field_map[field]=[types[0],'FLOAT']

        else:
            attrs.update({
                field: django_models.CharField(max_length=1000,null=True,blank=True)
            })
            table_query = f'{table_query},{field} varchar(1000) NULL'
            field_map[field]=[types[0],'VARCHAR']

    table_query = f'{table_query}, PRIMARY KEY(id)'
    
    cursor = connection.cursor()
    sql_table = f'ddm_{model_name.lower()}'
    create_table_sql = f"CREATE TABLE {sql_table} ({table_query})"
    exists = False
    cursor.execute("""
        SELECT COUNT(*)
        FROM information_schema.tables
        WHERE table_name = '{0}'
        """.format(sql_table.replace('\'', '\'\'')))
    if cursor.fetchone()[0] == 1:
        exists = True
    if not exists:
        cursor.execute(create_table_sql)

    cursor.close()
    
    try:
        model = apps.get_model('ddm', model_name)
        django_admin.site.unregister(model)
    except Exception as e:
        print(e)

    datasource = DataSource.objects.create(
        model=model_name,
        field_map=field_map
    )
    with open(datasource_path,'rb') as data_f:
        datasource.file=File(data_f, name=f'datasource/{os.path.basename(data_f.name)}')
        datasource.save()

    MODEL = type(model_name, (django_models.Model,), attrs)
    django_admin.site.register(MODEL)
    print(f'Registered model {MODEL}')
    return MODEL,field_map


def populate_data(model,field_map,df):
    for index,row in df.iterrows():
        record = {}
        for field,field_real in list(field_map.items()):
            record.update({
                field:row[field_real[0]]
            })
        print(record)
        model.objects.create(**record)

def process_field(field):
    result = field
    result = result.replace(' ','').strip()
    result = ''.join(ch for ch in result if ch.isalnum())
    return result