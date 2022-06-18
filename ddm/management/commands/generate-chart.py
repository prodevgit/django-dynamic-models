from django.core.management.base import BaseCommand

from ddm.models import DataSource
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('value', type=str)
        parser.add_argument('datasource', type=str)
   
    def handle(self, *args, **options):

        datasources = DataSource.objects.all()