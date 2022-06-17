import logging
from django.core.management.base import BaseCommand
import pandas
import numpy

from ddm.utils import generate_model, populate_data
logger = logging.getLogger(__name__)

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('modelname', type=str)
        parser.add_argument('datasource', type=str)
     
    def handle(self, *args, **options):

        model_name = options['modelname']
        external_datasource = options['datasource']

        if external_datasource.endswith('.xlsx'):
            df = pandas.read_excel(external_datasource)
        elif external_datasource.endswith('.csv'):
            df = pandas.read_csv(external_datasource)

        df=df.replace([numpy.inf, -numpy.inf], numpy.nan)
        df = df.fillna(0)

        MODEL,field_map = generate_model(model_name,df,external_datasource)
        is_populate = input('Do you want to populate newly created model with data? (Y/N):')
        if is_populate in ['Y','y']:
            populate_data(MODEL,field_map,df)
        