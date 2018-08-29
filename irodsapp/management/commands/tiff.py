from django.core.management.base import BaseCommand


class Command(BaseCommand):

    def handle(self, *args, **options):
        
        from wand.image import Image

        with Image(filename='/code/test.tiff') as img:
            img.format = 'jpeg'   
            #img.sample(800, 800)
            
            img.transform(resize='x800')
            
            img.save(filename='/code/testje.jpeg')
