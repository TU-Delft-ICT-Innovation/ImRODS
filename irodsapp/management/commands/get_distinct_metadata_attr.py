from django.core.management.base import BaseCommand

from irodsapp.irods_interface import get_distinct_metadata_attr

class Command(BaseCommand):

    def handle(self, *args, **options):
        get_distinct_metadata_attr()
