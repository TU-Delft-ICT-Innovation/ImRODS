from django.core.management.base import BaseCommand

from irodsapp.irods_interface import create_thumbnails
class Command(BaseCommand):

    def handle(self, *args, **options):
        create_thumbnails()
