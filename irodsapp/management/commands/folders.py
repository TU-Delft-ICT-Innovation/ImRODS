from django.core.management.base import BaseCommand

from irodsapp.irods_interface import folders

class Command(BaseCommand):

    def handle(self, *args, **options):
        folders('susanb')
