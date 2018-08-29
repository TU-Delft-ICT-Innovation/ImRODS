from django.core.management.base import BaseCommand

from irodsapp.irods_interface import remove_none

class Command(BaseCommand):

    def handle(self, *args, **options):
        remove_none('med_frame_time')
