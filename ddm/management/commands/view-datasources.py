import logging
from django.core.management.base import BaseCommand

from ddm.models import DataSource


logger = logging.getLogger(__name__)

class Command(BaseCommand):
   
    def handle(self, *args, **options):

        datasources = DataSource.objects.all()
        for _,datasource in enumerate(datasources):
            print(_+1,'.',datasource.model)