# Create your tasks here
from __future__ import absolute_import, unicode_literals
from irodsapp import irods_interface 
from celery import task
from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)


@task()
def create_thumbnails():
    logger.info('Starting task creat_thumbnails')
    irods_interface.create_thumbnails()
    
    irods_interface.get_distinct_metadata_attr()
    logger.info('Task creat_thumbnails done')

#print(create_thumbnails)