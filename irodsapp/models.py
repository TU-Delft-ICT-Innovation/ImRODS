# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models


from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone


TYPES = (
    ('St', "String"),        
    ('De', "Decimal"),
    ('Da', 'Date'),
    ('Ti', 'Time')
    )

class Error(models.Model):
    error =  models.CharField(max_length=2000, null=False,blank=False)
    date = models.DateTimeField(default=timezone.now)


class UserIrodsMetaDataAttribute(models.Model):
    name = models.CharField(max_length=128)
    name_unique = models.CharField(max_length=128)
    object_or_collection = models.BooleanField(default=True)
    type = models.CharField(max_length=3,choices=TYPES, default='St')
    
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    use_in_filters = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ['name_unique', 'user', 'object_or_collection']
        ordering = ('name',)  
        
    def __unicode__(self):
        return "%s" % (self.name)        
    

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    irods_user= models.CharField(max_length=30, blank=True)
    irods_password = models.CharField(max_length=128, blank=True)
    zone = models.CharField(max_length=128, blank=True)
    root = models.CharField(max_length=128, blank=True)
    create_thumbs = models.BooleanField(default=False)
    image_columns = models.IntegerField(default = 3)
    
     
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
        #instance.is_active = False
        #instance.save()

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
    
    
class Folder(models.Model):
    id = models.IntegerField(primary_key=True, editable=False)
    name = models.CharField(max_length=512)
    def __unicode__(self):
        return "%s" % (self.name)     


class Thumbnail(models.Model):
    id = models.IntegerField(primary_key=True, editable=False)
    image = models.TextField()
    name = models.CharField(max_length=255)
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE)
    #size = models.IntegerField()
    
    #class Meta:
    #    unique_together = ['name', 'folder']
